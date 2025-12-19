"""Comparison Engine - Compare automations and find similarities."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

_LOGGER = logging.getLogger(__name__)


@dataclass
class DiffItem:
    """Single difference item."""

    type: Literal["added", "removed", "modified", "same"]
    component_type: Literal["trigger", "condition", "action", "metadata"]
    before: Optional[Dict[str, Any]] = None
    after: Optional[Dict[str, Any]] = None
    path: str = ""  # JSON path to the change

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "component_type": self.component_type,
            "before": self.before,
            "after": self.after,
            "path": self.path,
        }


@dataclass
class AutomationDiff:
    """Complete diff between two automations."""

    automation_id_1: str
    automation_id_2: str
    triggers_diff: List[DiffItem]
    conditions_diff: List[DiffItem]
    actions_diff: List[DiffItem]
    metadata_diff: List[DiffItem]
    total_differences: int
    similarity_score: float  # 0-100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "automation_id_1": self.automation_id_1,
            "automation_id_2": self.automation_id_2,
            "triggers_diff": [d.to_dict() for d in self.triggers_diff],
            "conditions_diff": [d.to_dict() for d in self.conditions_diff],
            "actions_diff": [d.to_dict() for d in self.actions_diff],
            "metadata_diff": [d.to_dict() for d in self.metadata_diff],
            "total_differences": self.total_differences,
            "similarity_score": round(self.similarity_score, 2),
        }


@dataclass
class ConsolidationSuggestion:
    """Consolidation recommendation."""

    automations: List[str]
    suggestion: str
    consolidation_level: Literal["high", "medium", "low"]
    estimated_components_reduction: int
    potential_benefits: List[str]
    implementation_complexity: Literal["simple", "moderate", "complex"] = "moderate"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "automations": self.automations,
            "suggestion": self.suggestion,
            "consolidation_level": self.consolidation_level,
            "estimated_components_reduction": self.estimated_components_reduction,
            "potential_benefits": self.potential_benefits,
            "implementation_complexity": self.implementation_complexity,
        }


class ComparisonEngine:
    """Engine for comparing automations."""

    def __init__(self, hass):
        """Initialize comparison engine."""
        self.hass = hass
        _LOGGER.debug("Comparison Engine initialized")

    async def compare(self, automation_ids: List[str]) -> Dict[str, Any]:
        """
        Compare multiple automations.

        Args:
            automation_ids: List of automation IDs (2-5)

        Returns:
            Dictionary with comparison results
        """
        try:
            if len(automation_ids) < 2:
                raise ValueError("Need at least 2 automations to compare")

            if len(automation_ids) > 5:
                raise ValueError("Maximum 5 automations per comparison")

            _LOGGER.info(f"Comparing {len(automation_ids)} automations")

            # Get all automation configs (in real implementation from Home Assistant)
            automations_data = {}
            for auto_id in automation_ids:
                # In real implementation: automations_data[auto_id] = await self._get_automation(auto_id)
                automations_data[auto_id] = {
                    "triggers": [],
                    "conditions": [],
                    "actions": [],
                }

            # Generate pairwise diffs
            comparisons = []
            for i, auto1_id in enumerate(automation_ids):
                for auto2_id in automation_ids[i + 1 :]:
                    diff = self._generate_diff(
                        automations_data[auto1_id], automations_data[auto2_id]
                    )
                    diff.automation_id_1 = auto1_id
                    diff.automation_id_2 = auto2_id
                    comparisons.append(diff.to_dict())

            # Generate consolidation suggestions
            diffs = [
                self._generate_diff(
                    automations_data[auto_ids[0]], automations_data[auto_ids[1]]
                )
                for auto_ids in [
                    (automation_ids[i], automation_ids[i + 1])
                    for i in range(len(automation_ids) - 1)
                ]
            ]
            suggestions = self._suggest_consolidation(diffs)

            result = {
                "automations": automation_ids,
                "comparisons": comparisons,
                "suggestions": [s.to_dict() for s in suggestions],
                "total_differences": sum(c["total_differences"] for c in comparisons),
                "timestamp": datetime.now().isoformat(),
            }

            _LOGGER.info(
                f"Comparison complete: {len(comparisons)} comparisons, {len(suggestions)} suggestions"
            )
            return result

        except Exception as err:
            _LOGGER.error(f"Comparison failed: {err}", exc_info=True)
            raise

    async def find_similar(
        self, automation_id: str, limit: int = 10, threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Find automations similar to the given one.

        Args:
            automation_id: Base automation
            limit: Max results
            threshold: Minimum similarity (0-1)

        Returns:
            List of similar automations
        """
        try:
            _LOGGER.info(
                f"Finding similar automations to {automation_id} (threshold: {threshold})"
            )

            if threshold < 0 or threshold > 1:
                raise ValueError("Threshold must be between 0 and 1")

            # In real implementation:
            # 1. Get base automation config
            # 2. Compare to all others
            # 3. Calculate similarity scores
            # 4. Filter by threshold
            # 5. Sort by score
            # 6. Return top results

            base_automation = {
                "triggers": [],
                "conditions": [],
                "actions": [],
            }

            similar = []
            # In real implementation would iterate all automations
            # For now, return empty list as template

            # Filter by threshold and limit
            filtered = [s for s in similar if s["similarity_score"] >= threshold]
            result = sorted(
                filtered, key=lambda x: x["similarity_score"], reverse=True
            )[:limit]

            _LOGGER.info(f"Found {len(result)} similar automations")
            return result

        except Exception as err:
            _LOGGER.error(f"Find similar failed: {err}", exc_info=True)
            raise

    def _calculate_similarity(
        self, auto1: Dict[str, Any], auto2: Dict[str, Any]
    ) -> float:
        """
        Calculate similarity score between two automations.

        Uses weighted algorithm:
        - Trigger platforms: 20%
        - Conditions: 20%
        - Services called: 20%
        - Entities involved: 20%
        - Graph structure: 10%
        - Metadata: 10%

        Args:
            auto1: First automation config
            auto2: Second automation config

        Returns:
            Similarity score (0-100)
        """
        try:
            scores = {}

            # Extract components
            triggers1 = set(t.get("platform", "") for t in auto1.get("triggers", []))
            triggers2 = set(t.get("platform", "") for t in auto2.get("triggers", []))

            conditions1 = len(auto1.get("conditions", []))
            conditions2 = len(auto2.get("conditions", []))

            actions1 = set(a.get("service", "") for a in auto1.get("actions", []))
            actions2 = set(a.get("service", "") for a in auto2.get("actions", []))

            # Calculate individual scores (0-100)
            # Trigger similarity
            if triggers1 or triggers2:
                intersection = len(triggers1 & triggers2)
                union = len(triggers1 | triggers2)
                scores["triggers"] = (intersection / union * 100) if union > 0 else 0
            else:
                scores["triggers"] = 100

            # Condition similarity (based on count proximity)
            condition_diff = abs(conditions1 - conditions2)
            max_conditions = max(conditions1, conditions2, 1)
            scores["conditions"] = max(0, 100 - (condition_diff / max_conditions * 100))

            # Action similarity
            if actions1 or actions2:
                intersection = len(actions1 & actions2)
                union = len(actions1 | actions2)
                scores["actions"] = (intersection / union * 100) if union > 0 else 0
            else:
                scores["actions"] = 100

            # Entities similarity
            entities1 = set()
            entities2 = set()
            for item in auto1.get("triggers", []) + auto1.get("actions", []):
                if "entity_id" in item:
                    entities1.add(item["entity_id"])
            for item in auto2.get("triggers", []) + auto2.get("actions", []):
                if "entity_id" in item:
                    entities2.add(item["entity_id"])

            if entities1 or entities2:
                intersection = len(entities1 & entities2)
                union = len(entities1 | entities2)
                scores["entities"] = (intersection / union * 100) if union > 0 else 0
            else:
                scores["entities"] = 100

            # Graph structure similarity (trigger -> condition -> action chain similarity)
            scores["structure"] = 50  # Placeholder for structural analysis

            # Metadata similarity
            scores["metadata"] = 0  # No metadata to compare in this structure

            # Calculate weighted score
            weighted_score = (
                scores["triggers"] * 0.20
                + scores["conditions"] * 0.20
                + scores["actions"] * 0.20
                + scores["entities"] * 0.20
                + scores["structure"] * 0.10
                + scores["metadata"] * 0.10
            )

            return round(weighted_score, 2)

        except Exception as err:
            _LOGGER.error(f"Similarity calculation failed: {err}")
            return 0.0

    def _generate_diff(
        self, auto1: Dict[str, Any], auto2: Dict[str, Any]
    ) -> AutomationDiff:
        """
        Generate detailed diff between two automations.

        Args:
            auto1: First automation
            auto2: Second automation

        Returns:
            AutomationDiff object
        """
        try:
            # Compare triggers
            triggers_diff = self._diff_component_lists(
                auto1.get("triggers", []), auto2.get("triggers", []), "trigger"
            )

            # Compare conditions
            conditions_diff = self._diff_component_lists(
                auto1.get("conditions", []), auto2.get("conditions", []), "condition"
            )

            # Compare actions
            actions_diff = self._diff_component_lists(
                auto1.get("actions", []), auto2.get("actions", []), "action"
            )

            # Metadata comparison
            metadata_diff = []

            # Count differences
            total_differences = (
                len(triggers_diff)
                + len(conditions_diff)
                + len(actions_diff)
                + len(metadata_diff)
            )

            # Calculate similarity
            similarity = self._calculate_similarity(auto1, auto2)

            return AutomationDiff(
                automation_id_1="",
                automation_id_2="",
                triggers_diff=triggers_diff,
                conditions_diff=conditions_diff,
                actions_diff=actions_diff,
                metadata_diff=metadata_diff,
                total_differences=total_differences,
                similarity_score=similarity,
            )

        except Exception as err:
            _LOGGER.error(f"Diff generation failed: {err}")
            return AutomationDiff(
                automation_id_1="",
                automation_id_2="",
                triggers_diff=[],
                conditions_diff=[],
                actions_diff=[],
                metadata_diff=[],
                total_differences=0,
                similarity_score=0,
            )

    def _diff_component_lists(
        self,
        list1: List[Dict[str, Any]],
        list2: List[Dict[str, Any]],
        component_type: Literal["trigger", "condition", "action", "metadata"],
    ) -> List[DiffItem]:
        """
        Generate diff for component lists (triggers, conditions, actions).

        Args:
            list1: First component list
            list2: Second component list
            component_type: Type of component

        Returns:
            List of DiffItems
        """
        diff_items = []

        # Simple diff: items in list1 but not in list2 are removed,
        # items in list2 but not in list1 are added
        for i, item1 in enumerate(list1):
            if i < len(list2):
                if item1 != list2[i]:
                    diff_items.append(
                        DiffItem(
                            type="modified",
                            component_type=component_type,
                            before=item1,
                            after=list2[i],
                            path=f"$[{i}]",
                        )
                    )
            else:
                diff_items.append(
                    DiffItem(
                        type="removed",
                        component_type=component_type,
                        before=item1,
                        after=None,
                        path=f"$[{i}]",
                    )
                )

        # Items only in list2
        for i in range(len(list1), len(list2)):
            diff_items.append(
                DiffItem(
                    type="added",
                    component_type=component_type,
                    before=None,
                    after=list2[i],
                    path=f"$[{i}]",
                )
            )

        return diff_items

    def _suggest_consolidation(
        self, diffs: List[AutomationDiff]
    ) -> List[ConsolidationSuggestion]:
        """
        Generate consolidation suggestions from diffs.

        Args:
            diffs: List of automation diffs

        Returns:
            List of consolidation suggestions
        """
        try:
            suggestions = []

            for diff in diffs:
                # High similarity (>80%) - easy consolidation
                if diff.similarity_score > 80:
                    suggestion = ConsolidationSuggestion(
                        automations=[diff.automation_id_1, diff.automation_id_2],
                        suggestion=f"These automations are very similar ({diff.similarity_score}% match). "
                        f"Consider consolidating them into a single automation with conditional logic.",
                        consolidation_level="high",
                        estimated_components_reduction=int(
                            diff.total_differences * 0.7
                        ),
                        potential_benefits=[
                            "Reduced number of automations to maintain",
                            "Simpler configuration",
                            "Easier to debug and update",
                            "Better performance",
                        ],
                        implementation_complexity="simple",
                    )
                    suggestions.append(suggestion)

                # Medium similarity (60-80%) - moderate consolidation
                elif diff.similarity_score > 60:
                    suggestion = ConsolidationSuggestion(
                        automations=[diff.automation_id_1, diff.automation_id_2],
                        suggestion=f"These automations share some similarities ({diff.similarity_score}% match). "
                        f"You might consolidate them by using condition groups and templates.",
                        consolidation_level="medium",
                        estimated_components_reduction=int(
                            diff.total_differences * 0.4
                        ),
                        potential_benefits=[
                            "Reduced redundancy",
                            "Shared trigger/action logic",
                            "Easier maintenance",
                        ],
                        implementation_complexity="moderate",
                    )
                    suggestions.append(suggestion)

            return suggestions

        except Exception as err:
            _LOGGER.error(f"Consolidation suggestion generation failed: {err}")
            return []
