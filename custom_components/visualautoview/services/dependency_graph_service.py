"""Dependency Graph Service for Visual AutoView.

This service analyzes automation dependencies, detecting chains and
potential issues like circular dependencies.
"""

import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Literal

_LOGGER = logging.getLogger(__name__)


@dataclass
class DependencyRelation:
    """Represents dependency between two automations."""

    source_automation_id: str
    target_automation_id: str
    source_alias: str
    target_alias: str

    dependency_type: Literal[
        "direct_trigger",
        "entity_trigger",
        "shared_entity",
        "shared_condition",
        "service_dependency",
        "potential",
    ]

    is_required: bool = True
    likelihood: float = 1.0  # 0.0-1.0
    delay: int | None = None  # milliseconds

    has_circular_dependency: bool = False
    could_cause_race_condition: bool = False
    could_cause_loop: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class DependencyChain:
    """A sequence of dependent automations."""

    automations: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)

    total_estimated_duration: int = 0
    is_circular: bool = False
    is_optimal: bool = True

    risk_level: Literal["low", "medium", "high"] = "low"
    potential_issues: list[str] = field(default_factory=list)
    optimization_suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class DependencyGraph:
    """Complete dependency graph of all automations."""

    nodes: list[str] = field(default_factory=list)
    edges: list[DependencyRelation] = field(default_factory=list)

    chains: list[DependencyChain] = field(default_factory=list)
    circular_dependencies: list[DependencyChain] = field(default_factory=list)

    total_automations: int = 0
    total_dependencies: int = 0
    avg_chain_length: float = 0.0
    has_circular_deps: bool = False
    critical_path_length: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "nodes": self.nodes,
            "edges": [e.to_dict() for e in self.edges],
            "chains": [c.to_dict() for c in self.chains],
            "circular_dependencies": [c.to_dict() for c in self.circular_dependencies],
            "total_automations": self.total_automations,
            "total_dependencies": self.total_dependencies,
            "avg_chain_length": self.avg_chain_length,
            "has_circular_deps": self.has_circular_deps,
            "critical_path_length": self.critical_path_length,
        }


class DependencyGraphService:
    """Service for analyzing automation dependencies."""

    def __init__(self, hass: Any, entity_service: Any = None) -> None:
        """Initialize the service.

        Args:
            hass: Home Assistant instance
            entity_service: EntityRelationshipService for entity analysis
        """
        self.hass = hass
        self.entity_service = entity_service
        self._dependency_cache: DependencyGraph | None = None

        _LOGGER.debug("DependencyGraphService initialized")

    async def build_dependency_graph(self) -> DependencyGraph:
        """Build complete dependency graph for all automations.

        Returns:
            DependencyGraph with all relationships
        """
        _LOGGER.debug("Building complete dependency graph")

        try:
            graph = DependencyGraph()
            automations = self.hass.data.get("automation", {})

            if not automations:
                return graph

            graph.nodes = list(automations.keys())
            graph.total_automations = len(automations)

            # Build dependency relations
            edges: list[DependencyRelation] = []

            for source_id, source_config in automations.items():
                source_alias = source_config.get("alias", source_id)

                # Extract entities this automation uses
                source_actions = source_config.get("action", [])
                if not isinstance(source_actions, list):
                    source_actions = [source_actions] if source_actions else []

                source_entities = set()
                for action in source_actions:
                    if isinstance(action, dict) and "entity_id" in action:
                        ent_id = action["entity_id"]
                        if isinstance(ent_id, list):
                            source_entities.update(ent_id)
                        else:
                            source_entities.add(ent_id)

                # Find target automations that are triggered by these entities
                for target_id, target_config in automations.items():
                    if source_id == target_id:
                        continue

                    target_alias = target_config.get("alias", target_id)
                    target_triggers = target_config.get("trigger", [])
                    if not isinstance(target_triggers, list):
                        target_triggers = [target_triggers]

                    for trigger in target_triggers:
                        if isinstance(trigger, dict):
                            trigger_entity = trigger.get("entity_id")
                            if trigger_entity:
                                if isinstance(trigger_entity, list):
                                    if any(
                                        e in source_entities for e in trigger_entity
                                    ):
                                        edge = DependencyRelation(
                                            source_automation_id=source_id,
                                            target_automation_id=target_id,
                                            source_alias=source_alias,
                                            target_alias=target_alias,
                                            dependency_type="entity_trigger",
                                            is_required=True,
                                            likelihood=0.9,
                                        )
                                        edges.append(edge)
                                        break
                                elif trigger_entity in source_entities:
                                    edge = DependencyRelation(
                                        source_automation_id=source_id,
                                        target_automation_id=target_id,
                                        source_alias=source_alias,
                                        target_alias=target_alias,
                                        dependency_type="entity_trigger",
                                        is_required=True,
                                        likelihood=0.9,
                                    )
                                    edges.append(edge)
                                    break

            graph.edges = edges
            graph.total_dependencies = len(edges)

            if graph.total_automations > 0:
                graph.avg_chain_length = graph.total_dependencies / max(
                    1, graph.total_automations
                )

            # Detect circular dependencies
            graph.circular_dependencies = await self.detect_circular_dependencies()
            graph.has_circular_deps = len(graph.circular_dependencies) > 0

            # Cache the result
            self._dependency_cache = graph

        except Exception as e:
            _LOGGER.error(f"Error building dependency graph: {e}")

        return graph

    async def find_chains(self) -> list[DependencyChain]:
        """Find all automation chains in the system.

        Returns:
            List of detected chains
        """
        _LOGGER.debug("Finding automation chains")

        try:
            chains = []
            graph = await self.build_dependency_graph()

            visited = set()

            async def trace_chain(start_id: str, current_chain: list[str]) -> None:
                """Trace a dependency chain."""
                if start_id in visited or len(current_chain) > 20:
                    return

                visited.add(start_id)
                current_chain.append(start_id)

                # Find dependencies
                found_dependency = False
                for edge in graph.edges:
                    if edge.source_automation_id == start_id:
                        found_dependency = True
                        await trace_chain(
                            edge.target_automation_id, current_chain.copy()
                        )

                if not found_dependency and len(current_chain) > 1:
                    # End of chain
                    automations_config = self.hass.data.get("automation", {})
                    aliases = [
                        automations_config.get(aid, {}).get("alias", aid)
                        for aid in current_chain
                    ]

                    chain = DependencyChain(
                        automations=current_chain.copy(),
                        aliases=aliases,
                        total_estimated_duration=len(current_chain)
                        * 100,  # 100ms per automation
                        is_circular=False,
                        risk_level="low",
                    )
                    chains.append(chain)

            for node in graph.nodes:
                if node not in visited:
                    await trace_chain(node, [])

            return chains

        except Exception as e:
            _LOGGER.error(f"Error finding chains: {e}")
            return []

    async def detect_circular_dependencies(self) -> list[DependencyChain]:
        """Detect circular automation dependencies.

        Returns:
            List of circular dependency chains
        """
        _LOGGER.debug("Detecting circular dependencies")

        try:
            circular_chains = []
            graph = await self.build_dependency_graph()

            def has_cycle(
                node: str,
                visited: set[str],
                rec_stack: set[str],
                path: list[str],
            ) -> bool:
                """Check if node is part of a cycle."""
                visited.add(node)
                rec_stack.add(node)
                path.append(node)

                for edge in graph.edges:
                    if edge.source_automation_id == node:
                        neighbor = edge.target_automation_id

                        if neighbor not in visited:
                            if has_cycle(neighbor, visited, rec_stack, path.copy()):
                                return True
                        elif neighbor in rec_stack:
                            # Found a cycle
                            cycle_start = path.index(neighbor)
                            cycle = path[cycle_start:] + [neighbor]

                            automations_config = self.hass.data.get("automation", {})
                            aliases = [
                                automations_config.get(aid, {}).get("alias", aid)
                                for aid in cycle[:-1]
                            ]

                            chain = DependencyChain(
                                automations=cycle[:-1],
                                aliases=aliases,
                                is_circular=True,
                                risk_level="high",
                                potential_issues=[
                                    "Circular dependency detected",
                                    "Could cause infinite execution loops",
                                ],
                            )
                            circular_chains.append(chain)
                            return True

                path.pop()
                rec_stack.remove(node)
                return False

            visited = set()
            for node in graph.nodes:
                if node not in visited:
                    has_cycle(node, visited, set(), [])

            return circular_chains

        except Exception as e:
            _LOGGER.error(f"Error detecting circular dependencies: {e}")
            return []

    async def analyze_automation_impact(self, automation_id: str) -> dict[str, Any]:
        """Analyze cascading impact of one automation.

        Args:
            automation_id: Automation to analyze

        Returns:
            Impact analysis dictionary
        """
        _LOGGER.debug(f"Analyzing impact of automation {automation_id}")

        try:
            graph = await self.build_dependency_graph()

            direct_dependents = []
            cascade_count = 0
            affected_automations = set()

            # Find direct dependents
            for edge in graph.edges:
                if edge.source_automation_id == automation_id:
                    direct_dependents.append(
                        {
                            "automation_id": edge.target_automation_id,
                            "alias": edge.target_alias,
                            "dependency_type": edge.dependency_type,
                            "risk": "high" if edge.could_cause_loop else "low",
                        }
                    )
                    affected_automations.add(edge.target_automation_id)

            # Find cascading effects
            def find_cascade(auto_id: str, depth: int = 0, max_depth: int = 10) -> None:
                """Recursively find cascading effects."""
                if depth > max_depth:
                    return

                for edge in graph.edges:
                    if (
                        edge.source_automation_id == auto_id
                        and edge.target_automation_id not in affected_automations
                    ):
                        affected_automations.add(edge.target_automation_id)
                        cascade_count += 1
                        find_cascade(edge.target_automation_id, depth + 1, max_depth)

            find_cascade(automation_id)

            return {
                "automation_id": automation_id,
                "direct_dependents": direct_dependents,
                "cascade_count": len(affected_automations) - len(direct_dependents),
                "total_affected": len(affected_automations),
                "affected_automations": list(affected_automations),
                "risk_level": (
                    "high"
                    if len(affected_automations) > 5
                    else "medium" if len(affected_automations) > 2 else "low"
                ),
            }

        except Exception as e:
            _LOGGER.error(f"Error analyzing automation impact: {e}")
            return {"error": str(e)}

    async def find_optimization_opportunities(
        self,
    ) -> list[dict[str, Any]]:
        """Find consolidation and optimization suggestions.

        Returns:
            List of optimization opportunities
        """
        _LOGGER.debug("Finding optimization opportunities")

        try:
            opportunities = []
            graph = await self.build_dependency_graph()

            # Check for long chains
            chains = await self.find_chains()
            for chain in chains:
                if len(chain.automations) > 3:
                    opportunities.append(
                        {
                            "type": "consolidate_chain",
                            "automations": chain.automations,
                            "reason": f"Long automation chain with {len(chain.automations)} automations",
                            "suggestion": "Consider consolidating into fewer automations",
                            "benefit": "Reduced complexity and execution time",
                            "priority": "medium",
                        }
                    )

            # Check for circular dependencies
            circular = await self.detect_circular_dependencies()
            for circ in circular:
                opportunities.append(
                    {
                        "type": "remove_circular",
                        "automations": circ.automations,
                        "reason": "Circular dependency detected",
                        "suggestion": "Redesign automation logic to break the cycle",
                        "benefit": "Prevent infinite loops",
                        "priority": "high",
                    }
                )

            return opportunities

        except Exception as e:
            _LOGGER.error(f"Error finding optimization opportunities: {e}")
            return []

    def calculate_chain_risk(self, chain: DependencyChain) -> dict[str, Any]:
        """Assess risk level of automation chain.

        Args:
            chain: Chain to analyze

        Returns:
            Risk assessment dictionary
        """
        risk_score = 0.0
        issues = chain.potential_issues.copy() if chain.potential_issues else []

        # Length risk
        if len(chain.automations) > 5:
            risk_score += 0.3
            issues.append(f"Long chain with {len(chain.automations)} automations")
        elif len(chain.automations) > 3:
            risk_score += 0.15

        # Circular risk
        if chain.is_circular:
            risk_score += 0.5
            if "Circular dependency" not in " ".join(issues):
                issues.append("Potential infinite execution loop")

        # Duration risk
        if chain.total_estimated_duration > 5000:  # 5 seconds
            risk_score += 0.2
            issues.append(
                f"Long execution duration: {chain.total_estimated_duration}ms"
            )

        risk_level = (
            "low" if risk_score < 0.3 else "medium" if risk_score < 0.6 else "high"
        )

        return {
            "risk_score": min(1.0, risk_score),
            "risk_level": risk_level,
            "issues": issues,
            "chain_length": len(chain.automations),
            "estimated_duration_ms": chain.total_estimated_duration,
        }

    async def simulate_execution_order(
        self, trigger_automation_id: str
    ) -> list[dict[str, Any]]:
        """Simulate execution order of dependent automations.

        Args:
            trigger_automation_id: Starting automation

        Returns:
            List of automations in execution order
        """
        _LOGGER.debug(f"Simulating execution order from {trigger_automation_id}")

        try:
            execution_order = []
            graph = await self.build_dependency_graph()

            visited = set()

            def add_to_execution(auto_id: str, depth: int = 0) -> None:
                """Add automation and its dependents to execution order."""
                if auto_id in visited or depth > 10:
                    return

                visited.add(auto_id)

                automations_config = self.hass.data.get("automation", {})
                auto_config = automations_config.get(auto_id, {})

                execution_order.append(
                    {
                        "order": len(execution_order) + 1,
                        "automation_id": auto_id,
                        "alias": auto_config.get("alias", auto_id),
                        "depth": depth,
                        "estimated_duration_ms": 100 * (depth + 1),
                        "expected_start_ms": sum(
                            100 for _ in range(len(execution_order))
                        ),
                    }
                )

                # Add dependents
                for edge in graph.edges:
                    if edge.source_automation_id == auto_id:
                        add_to_execution(edge.target_automation_id, depth + 1)

            add_to_execution(trigger_automation_id)

            return execution_order

        except Exception as e:
            _LOGGER.error(f"Error simulating execution order: {e}")
            return []
