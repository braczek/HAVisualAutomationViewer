"""Entity Relationship Service for Visual AutoView.

This service analyzes relationships between entities and automations,
showing which entities trigger or are affected by automations.
"""

import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Literal

_LOGGER = logging.getLogger(__name__)


@dataclass
class EntityRelationship:
    """Relationship between an entity and automation."""

    entity_id: str
    automation_id: str
    automation_alias: str

    relationship_type: Literal[
        "trigger",
        "condition",
        "action_target",
        "data_template",
        "service_param",
    ]

    direction: Literal["input", "bidirectional", "output"]
    strength: float  # 0.0-1.0

    data: dict[str, Any] = field(default_factory=dict)
    last_triggered: datetime | None = None
    interaction_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        if self.last_triggered:
            result["last_triggered"] = self.last_triggered.isoformat()
        return result


@dataclass
class EntityNode:
    """Node representing a single entity in relationship view."""

    entity_id: str
    entity_name: str
    entity_type: str
    current_state: str

    relationships: list[EntityRelationship] = field(default_factory=list)
    incoming_relationships: int = 0
    outgoing_relationships: int = 0

    is_trigger_source: bool = False
    is_action_target: bool = False
    is_condition_check: bool = False
    cascade_chains: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "entity_type": self.entity_type,
            "current_state": self.current_state,
            "relationships": [r.to_dict() for r in self.relationships],
            "incoming_relationships": self.incoming_relationships,
            "outgoing_relationships": self.outgoing_relationships,
            "is_trigger_source": self.is_trigger_source,
            "is_action_target": self.is_action_target,
            "is_condition_check": self.is_condition_check,
            "cascade_chains": self.cascade_chains,
        }


@dataclass
class RelationshipGraph:
    """Complete graph of entity relationships."""

    entities: dict[str, EntityNode] = field(default_factory=dict)
    relationships: list[EntityRelationship] = field(default_factory=list)

    cascade_chains: list[list[str]] = field(default_factory=list)
    critical_entities: list[str] = field(default_factory=list)

    total_entities: int = 0
    total_relationships: int = 0
    automation_count: int = 0
    avg_relationships_per_entity: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "entities": {k: v.to_dict() for k, v in self.entities.items()},
            "relationships": [r.to_dict() for r in self.relationships],
            "cascade_chains": self.cascade_chains,
            "critical_entities": self.critical_entities,
            "total_entities": self.total_entities,
            "total_relationships": self.total_relationships,
            "automation_count": self.automation_count,
            "avg_relationships_per_entity": self.avg_relationships_per_entity,
        }


class EntityRelationshipService:
    """Service for analyzing entity relationships in automations."""

    def __init__(self, hass: Any) -> None:
        """Initialize the service.

        Args:
            hass: Home Assistant instance
        """
        self.hass = hass
        self._relationship_cache: dict[str, RelationshipGraph] = {}
        self._cache_ttl = 300  # 5 minutes

        _LOGGER.debug("EntityRelationshipService initialized")

    async def get_entity_relationships(
        self,
        automation_id: str | None = None,
        entity_id: str | None = None,
    ) -> RelationshipGraph:
        """Get entity relationships for automation(s).

        Args:
            automation_id: Specific automation ID or None for all
            entity_id: Filter by specific entity or None for all

        Returns:
            RelationshipGraph with all relationships
        """
        _LOGGER.debug(
            f"Getting entity relationships for automation_id={automation_id}, entity_id={entity_id}"
        )

        # Try cache first
        cache_key = f"{automation_id}:{entity_id}"
        if cache_key in self._relationship_cache:
            return self._relationship_cache[cache_key]
        
        graph = RelationshipGraph()
        
        try:
            # Get all automations from config
            automations = self.hass.data.get("automation", {})
            if not automations:
                automations = {}
            
            relationships: list[EntityRelationship] = []
            entities_found: dict[str, EntityNode] = {}
            
            # Analyze each automation
            for auto_id, auto_config in automations.items():
                if automation_id and auto_id != automation_id:
                    continue
                    
                # Extract triggers
                triggers = auto_config.get("trigger", [])
                if not isinstance(triggers, list):
                    triggers = [triggers]
                    
                for trigger in triggers:
                    if isinstance(trigger, dict):
                        # Entity trigger
                        if "entity_id" in trigger:
                            ent_id = trigger["entity_id"]
                            if isinstance(ent_id, list):
                                for e in ent_id:
                                    self._add_relationship(
                                        relationships, entities_found,
                                        e, auto_id, auto_config.get("alias", auto_id),
                                        "trigger", "input", 0.95
                                    )
                            else:
                                self._add_relationship(
                                    relationships, entities_found,
                                    ent_id, auto_id, auto_config.get("alias", auto_id),
                                    "trigger", "input", 0.95
                                )
                
                # Extract conditions
                conditions = auto_config.get("condition", [])
                if not isinstance(conditions, list):
                    conditions = [conditions] if conditions else []
                    
                for condition in conditions:
                    if isinstance(condition, dict):
                        if "entity_id" in condition:
                            ent_id = condition["entity_id"]
                            if isinstance(ent_id, list):
                                for e in ent_id:
                                    self._add_relationship(
                                        relationships, entities_found,
                                        e, auto_id, auto_config.get("alias", auto_id),
                                        "condition", "input", 0.80
                                    )
                            else:
                                self._add_relationship(
                                    relationships, entities_found,
                                    ent_id, auto_id, auto_config.get("alias", auto_id),
                                    "condition", "input", 0.80
                                )
                
                # Extract actions
                actions = auto_config.get("action", [])
                if not isinstance(actions, list):
                    actions = [actions] if actions else []
                    
                for action in actions:
                    if isinstance(action, dict):
                        if "entity_id" in action:
                            ent_id = action["entity_id"]
                            if isinstance(ent_id, list):
                                for e in ent_id:
                                    self._add_relationship(
                                        relationships, entities_found,
                                        e, auto_id, auto_config.get("alias", auto_id),
                                        "action_target", "output", 0.90
                                    )
                            else:
                                self._add_relationship(
                                    relationships, entities_found,
                                    ent_id, auto_id, auto_config.get("alias", auto_id),
                                    "action_target", "output", 0.90
                                )
            
            # Filter by entity_id if specified
            if entity_id:
                relationships = [r for r in relationships if r.entity_id == entity_id]
                entities_found = {entity_id: entities_found.get(entity_id, EntityNode(
                    entity_id=entity_id,
                    entity_name=entity_id.split(".")[-1],
                    entity_type="unknown",
                    current_state="unknown"
                ))} if entity_id in entities_found else {}
            
            graph.entities = entities_found
            graph.relationships = relationships
            graph.total_entities = len(entities_found)
            graph.total_relationships = len(relationships)
            graph.automation_count = len(set(r.automation_id for r in relationships))
            
            if graph.total_entities > 0:
                graph.avg_relationships_per_entity = len(relationships) / len(entities_found)
            
            # Cache the result
            self._relationship_cache[cache_key] = graph
            
        except Exception as e:
            _LOGGER.error(f"Error getting entity relationships: {e}")
        
        return graph
    
    def _add_relationship(
        self,
        relationships: list[EntityRelationship],
        entities: dict[str, EntityNode],
        entity_id: str,
        automation_id: str,
        automation_alias: str,
        rel_type: str,
        direction: str,
        strength: float,
    ) -> None:
        """Helper to add a relationship and update entity node."""
        # Create relationship
        rel = EntityRelationship(
            entity_id=entity_id,
            automation_id=automation_id,
            automation_alias=automation_alias,
            relationship_type=rel_type,
            direction=direction,
            strength=strength,
        )
        relationships.append(rel)
        
        # Update or create entity node
        if entity_id not in entities:
            entity_name = entity_id.split(".")[-1] if "." in entity_id else entity_id
            entity_type = entity_id.split(".")[0] if "." in entity_id else "unknown"
            entities[entity_id] = EntityNode(
                entity_id=entity_id,
                entity_name=entity_name,
                entity_type=entity_type,
                current_state=self.hass.states.get(entity_id, None) and self.hass.states.get(entity_id).state or "unknown",
                relationships=[rel],
            )
        else:
            entities[entity_id].relationships.append(rel)
        
        # Update relationship counts
        if direction in ["input", "bidirectional"]:
            entities[entity_id].incoming_relationships += 1
        if direction in ["output", "bidirectional"]:
            entities[entity_id].outgoing_relationships += 1
        
        # Mark entity roles
        if rel_type == "trigger":
            entities[entity_id].is_trigger_source = True
        elif rel_type == "action_target":
            entities[entity_id].is_action_target = True
        elif rel_type == "condition":
            entities[entity_id].is_condition_check = True

    async def analyze_entity_impact(self, entity_id: str) -> dict[str, Any]:
        """Analyze impact of entity changes on all automations.

        Args:
            entity_id: Entity to analyze

        Returns:
            Impact analysis dictionary
        """
        _LOGGER.debug(f"Analyzing entity impact for {entity_id}")

        try:
            graph = await self.get_entity_relationships(entity_id=entity_id)
            
            if entity_id not in graph.entities:
                return {
                    "entity_id": entity_id,
                    "affected_automations": [],
                    "impact_score": 0.0,
                    "direct_impacts": 0,
                    "indirect_impacts": 0,
                }
            
            entity_node = graph.entities[entity_id]
            affected = set()
            
            for rel in entity_node.relationships:
                affected.add(rel.automation_id)
            
            cascades = await self.detect_cascades_for_entity(entity_id, affected)
            
            return {
                "entity_id": entity_id,
                "entity_name": entity_node.entity_name,
                "entity_type": entity_node.entity_type,
                "current_state": entity_node.current_state,
                "affected_automations": list(affected),
                "cascade_chains": cascades,
                "impact_score": min(1.0, len(affected) * 0.1),
                "direct_impacts": len(affected),
                "indirect_impacts": sum(len(c) - 1 for c in cascades),
                "incoming_relationships": entity_node.incoming_relationships,
                "outgoing_relationships": entity_node.outgoing_relationships,
            }
        except Exception as e:
            _LOGGER.error(f"Error analyzing entity impact: {e}")
            return {"error": str(e)}

    async def detect_cascades(self, automation_id: str) -> list[list[str]]:
        """Detect cascading automation chains.

        Args:
            automation_id: Automation to check for cascades

        Returns:
            List of cascade chains (each chain is list of automation IDs)
        """
        _LOGGER.debug(f"Detecting cascades for automation {automation_id}")

        cascades = []
        visited = set()
        
        async def find_cascade_chain(
            start_auto_id: str,
            chain: list[str],
            max_depth: int = 10,
        ) -> None:
            """Recursively find cascade chains."""
            if start_auto_id in visited or len(chain) > max_depth:
                return
            
            visited.add(start_auto_id)
            chain.append(start_auto_id)
            
            # Get automations that might be triggered by this one
            try:
                relationships = await self.get_entity_relationships(automation_id=start_auto_id)
                
                for rel in relationships.relationships:
                    if rel.direction in ["output", "bidirectional"]:
                        # This automation outputs to an entity
                        # Find other automations triggered by this entity
                        triggered = await self.get_entity_relationships(entity_id=rel.entity_id)
                        for triggered_rel in triggered.relationships:
                            if triggered_rel.relationship_type == "trigger" and triggered_rel.automation_id not in visited:
                                await find_cascade_chain(
                                    triggered_rel.automation_id,
                                    chain.copy(),
                                    max_depth,
                                )
            except Exception:
                pass
        
        try:
            await find_cascade_chain(automation_id, [])
        except Exception as e:
            _LOGGER.error(f"Error detecting cascades: {e}")
        
        return cascades if cascades else [[automation_id]]

    async def find_orphaned_entities(self, automation_id: str) -> list[str]:
        """Find entities referenced but not actively used.

        Args:
            automation_id: Automation to analyze

        Returns:
            List of orphaned entity IDs
        """
        _LOGGER.debug(f"Finding orphaned entities in automation {automation_id}")

        try:
            orphaned = []
            
            # Get automation config
            automations = self.hass.data.get("automation", {})
            auto_config = automations.get(automation_id)
            
            if not auto_config:
                return orphaned
            
            # Collect all referenced entities
            all_referenced = set()
            
            # Check triggers
            triggers = auto_config.get("trigger", [])
            if not isinstance(triggers, list):
                triggers = [triggers]
            for trigger in triggers:
                if isinstance(trigger, dict) and "entity_id" in trigger:
                    ent_id = trigger["entity_id"]
                    if isinstance(ent_id, list):
                        all_referenced.update(ent_id)
                    else:
                        all_referenced.add(ent_id)
            
            # Check conditions
            conditions = auto_config.get("condition", [])
            if not isinstance(conditions, list):
                conditions = [conditions] if conditions else []
            for condition in conditions:
                if isinstance(condition, dict) and "entity_id" in condition:
                    ent_id = condition["entity_id"]
                    if isinstance(ent_id, list):
                        all_referenced.update(ent_id)
                    else:
                        all_referenced.add(ent_id)
            
            # Check actions
            actions = auto_config.get("action", [])
            if not isinstance(actions, list):
                actions = [actions] if actions else []
            for action in actions:
                if isinstance(action, dict) and "entity_id" in action:
                    ent_id = action["entity_id"]
                    if isinstance(ent_id, list):
                        all_referenced.update(ent_id)
                    else:
                        all_referenced.add(ent_id)
            
            # Find which are used in conditions/actions (active usage)
            used_in_conditions = set()
            for condition in conditions:
                if isinstance(condition, dict) and "entity_id" in condition:
                    ent_id = condition["entity_id"]
                    if isinstance(ent_id, list):
                        used_in_conditions.update(ent_id)
                    else:
                        used_in_conditions.add(ent_id)
            
            used_in_actions = set()
            for action in actions:
                if isinstance(action, dict) and "entity_id" in action:
                    ent_id = action["entity_id"]
                    if isinstance(ent_id, list):
                        used_in_actions.update(ent_id)
                    else:
                        used_in_actions.add(ent_id)
            
            # Entities only in triggers with no action/condition are potentially orphaned
            orphaned = list(all_referenced - used_in_conditions - used_in_actions)
            
        except Exception as e:
            _LOGGER.error(f"Error finding orphaned entities: {e}")
        
        return orphaned

    def calculate_relationship_strength(
        self, relationship: EntityRelationship
    ) -> float:
        """Calculate relationship importance score.

        Args:
            relationship: Relationship to analyze

        Returns:
            Strength score (0.0-1.0)
        """
        # Base strength is already assigned
        strength = relationship.strength
        
        # Increase for critical relationship types
        if relationship.relationship_type == "trigger":
            strength = min(1.0, strength * 1.1)
        elif relationship.relationship_type == "action_target":
            strength = min(1.0, strength * 1.05)
        elif relationship.relationship_type == "condition":
            strength = min(1.0, strength * 0.95)
        
        # Consider frequency if available
        if relationship.interaction_count > 0:
            frequency_factor = min(1.2, 1.0 + (relationship.interaction_count * 0.02))
            strength = min(1.0, strength * frequency_factor)
        
        return strength

    async def get_cross_automation_impacts(
        self, automation_id: str
    ) -> list[dict[str, Any]]:
        """Find other automations affected by this one.

        Args:
            automation_id: Automation to analyze

        Returns:
            List of affected automations with details
        """
        _LOGGER.debug(
            f"Getting cross-automation impacts for {automation_id}"
        )

        try:
            affected = []
            
            # Get entities this automation outputs to
            graph = await self.get_entity_relationships(automation_id=automation_id)
            output_entities = set()
            
            for rel in graph.relationships:
                if rel.direction in ["output", "bidirectional"]:
                    output_entities.add(rel.entity_id)
            
            # Find automations triggered by these entities
            for entity_id in output_entities:
                impact_graph = await self.get_entity_relationships(entity_id=entity_id)
                
                for rel in impact_graph.relationships:
                    if rel.automation_id != automation_id and rel.relationship_type == "trigger":
                        affected.append({
                            "automation_id": rel.automation_id,
                            "automation_alias": rel.automation_alias,
                            "trigger_entity": entity_id,
                            "relationship_type": rel.relationship_type,
                            "strength": rel.strength,
                            "cascade_depth": 1,
                        })
            
            return affected
            
        except Exception as e:
            _LOGGER.error(f"Error getting cross-automation impacts: {e}")
            return []
    
    async def detect_cascades_for_entity(
        self,
        entity_id: str,
        affected_automations: set[str],
    ) -> list[list[str]]:
        """Helper to detect cascades for an entity."""
        cascades = []
        
        for auto_id in affected_automations:
            chain = await self.detect_cascades(auto_id)
            if chain:
                cascades.extend(chain)
        
        return cascades
