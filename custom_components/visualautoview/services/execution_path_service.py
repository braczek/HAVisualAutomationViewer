"""Execution Path Service for Visual AutoView.

This service tracks and displays automation execution paths, showing
which conditions passed/failed and which actions executed.
"""

import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Callable, Literal

_LOGGER = logging.getLogger(__name__)


@dataclass
class ConditionEvaluation:
    """Result of condition evaluation."""

    condition_id: str
    condition_label: str

    result: bool
    start_time: datetime
    end_time: datetime
    duration_ms: int

    condition_type: str
    condition_data: dict[str, Any] = field(default_factory=dict)

    error: str | None = None
    warning: str | None = None

    template_evaluated: bool = False
    template_variables: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result["start_time"] = self.start_time.isoformat()
        result["end_time"] = self.end_time.isoformat()
        return result


@dataclass
class ActionExecution:
    """Record of action execution."""

    action_id: str
    action_label: str

    sequence_number: int
    start_time: datetime
    end_time: datetime
    duration_ms: int

    action_type: str
    service: str | None = None
    target: dict[str, Any] | None = None

    status: Literal["success", "failed", "skipped", "running"] = "success"
    result_data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result["start_time"] = self.start_time.isoformat()
        result["end_time"] = self.end_time.isoformat()
        return result


@dataclass
class ExecutionPath:
    """Complete record of single automation execution."""

    execution_id: str
    automation_id: str
    automation_alias: str

    trigger_time: datetime
    trigger_entity: str | None = None
    trigger_platform: str = ""
    trigger_data: dict[str, Any] = field(default_factory=dict)

    condition_evaluations: list[ConditionEvaluation] = field(
        default_factory=list
    )
    actions_executed: list[ActionExecution] = field(default_factory=list)

    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)
    total_duration_ms: int = 0

    execution_result: Literal["success", "failed", "stopped"] = "success"
    executed_actions_count: int = 0
    skipped_actions_count: int = 0
    failed_actions_count: int = 0

    error_message: str | None = None
    errors: list[dict[str, Any]] = field(default_factory=list)

    variables: dict[str, Any] = field(default_factory=dict)
    context_user_id: str | None = None
    context_automation_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "execution_id": self.execution_id,
            "automation_id": self.automation_id,
            "automation_alias": self.automation_alias,
            "trigger_time": self.trigger_time.isoformat(),
            "trigger_entity": self.trigger_entity,
            "trigger_platform": self.trigger_platform,
            "trigger_data": self.trigger_data,
            "condition_evaluations": [c.to_dict() for c in self.condition_evaluations],
            "actions_executed": [a.to_dict() for a in self.actions_executed],
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "total_duration_ms": self.total_duration_ms,
            "execution_result": self.execution_result,
            "executed_actions_count": self.executed_actions_count,
            "skipped_actions_count": self.skipped_actions_count,
            "failed_actions_count": self.failed_actions_count,
            "error_message": self.error_message,
            "errors": self.errors,
            "variables": self.variables,
            "context_user_id": self.context_user_id,
            "context_automation_id": self.context_automation_id,
        }


@dataclass
class ExecutionHistory:
    """History of automation executions."""

    automation_id: str
    executions: list[ExecutionPath] = field(default_factory=list)

    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    success_rate: float = 0.0

    avg_duration_ms: int = 0
    min_duration_ms: int = 0
    max_duration_ms: int = 0

    last_execution: ExecutionPath | None = None
    last_triggered: datetime | None = None

    common_failures: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "automation_id": self.automation_id,
            "executions": [e.to_dict() for e in self.executions],
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "success_rate": self.success_rate,
            "avg_duration_ms": self.avg_duration_ms,
            "min_duration_ms": self.min_duration_ms,
            "max_duration_ms": self.max_duration_ms,
            "last_execution": self.last_execution.to_dict() if self.last_execution else None,
            "last_triggered": self.last_triggered.isoformat() if self.last_triggered else None,
            "common_failures": self.common_failures,
        }


class ExecutionPathService:
    """Service for tracking and displaying automation execution paths."""

    def __init__(self, hass: Any) -> None:
        """Initialize the service.

        Args:
            hass: Home Assistant instance
        """
        self.hass = hass
        self._execution_history: dict[str, list[ExecutionPath]] = {}
        self._max_history_per_automation = 50
        self._execution_subscribers: dict[str, list[Callable]] = {}

        _LOGGER.debug("ExecutionPathService initialized")

    async def on_automation_triggered(
        self, automation_id: str, trigger_data: dict[str, Any]
    ) -> None:
        """Called when automation is triggered.

        Args:
            automation_id: ID of triggered automation
            trigger_data: Trigger details
        """
        _LOGGER.debug(f"Automation triggered: {automation_id}")

        try:
            if automation_id not in self._execution_history:
                self._execution_history[automation_id] = []
            
            execution_id = f"{automation_id}_{int(datetime.now().timestamp() * 1000)}"
            path = ExecutionPath(
                execution_id=execution_id,
                automation_id=automation_id,
                automation_alias=automation_id.split(".")[-1],
                trigger_time=datetime.now(),
                trigger_data=trigger_data,
            )
            
            self._execution_history[automation_id].append(path)
            
            if len(self._execution_history[automation_id]) > self._max_history_per_automation:
                self._execution_history[automation_id].pop(0)
        except Exception as e:
            _LOGGER.error(f"Error tracking trigger: {e}")

    async def on_condition_evaluated(
        self,
        automation_id: str,
        execution_id: str,
        condition: ConditionEvaluation,
    ) -> None:
        """Called when condition is evaluated.

        Args:
            automation_id: Automation ID
            execution_id: Execution ID
            condition: Condition evaluation result
        """
        _LOGGER.debug(
            f"Condition evaluated in {automation_id}: {condition.condition_id}"
        )

        try:
            if automation_id in self._execution_history:
                for path in self._execution_history[automation_id]:
                    if path.execution_id == execution_id:
                        path.condition_evaluations.append(condition)
                        return
        except Exception as e:
            _LOGGER.error(f"Error tracking condition: {e}")

    async def on_action_executed(
        self,
        automation_id: str,
        execution_id: str,
        action: ActionExecution,
    ) -> None:
        """Called when action completes.

        Args:
            automation_id: Automation ID
            execution_id: Execution ID
            action: Action execution result
        """
        _LOGGER.debug(
            f"Action executed in {automation_id}: {action.action_id}"
        )

        try:
            if automation_id in self._execution_history:
                for path in self._execution_history[automation_id]:
                    if path.execution_id == execution_id:
                        path.actions_executed.append(action)
                        if action.status == "success":
                            path.executed_actions_count += 1
                        elif action.status == "skipped":
                            path.skipped_actions_count += 1
                        elif action.status == "failed":
                            path.failed_actions_count += 1
                        return
        except Exception as e:
            _LOGGER.error(f"Error tracking action: {e}")

    async def on_automation_completed(
        self,
        automation_id: str,
        execution_id: str,
        result: dict[str, Any],
    ) -> None:
        """Called when automation execution completes.

        Args:
            automation_id: Automation ID
            execution_id: Execution ID
            result: Execution result
        """
        _LOGGER.debug(f"Automation completed: {automation_id}")

        try:
            if automation_id in self._execution_history:
                for path in self._execution_history[automation_id]:
                    if path.execution_id == execution_id:
                        path.end_time = datetime.now()
                        path.total_duration_ms = int((path.end_time - path.start_time).total_seconds() * 1000)
                        path.execution_result = result.get("status", "success")
                        if "error" in result:
                            path.error_message = result["error"]
                            path.execution_result = "failed"
                        
                        if automation_id in self._execution_subscribers:
                            for callback in self._execution_subscribers[automation_id]:
                                try:
                                    callback(path.to_dict())
                                except Exception as cb_error:
                                    _LOGGER.error(f"Error in execution callback: {cb_error}")
                        return
        except Exception as e:
            _LOGGER.error(f"Error tracking completion: {e}")

    async def get_execution_history(
        self, automation_id: str, limit: int = 20
    ) -> ExecutionHistory:
        """Get execution history for automation.

        Args:
            automation_id: Automation ID
            limit: Maximum number of executions to return

        Returns:
            ExecutionHistory object
        """
        _LOGGER.debug(
            f"Getting execution history for {automation_id} (limit={limit})"
        )

        try:
            executions = self._execution_history.get(automation_id, [])
            recent_executions = executions[-limit:] if len(executions) > limit else executions
            
            history = ExecutionHistory(
                automation_id=automation_id,
                executions=recent_executions,
                total_executions=len(executions),
                successful_executions=sum(1 for e in executions if e.execution_result == "success"),
                failed_executions=sum(1 for e in executions if e.execution_result == "failed"),
            )
            
            if executions:
                history.last_execution = executions[-1]
                history.last_triggered = executions[-1].trigger_time
                
                if history.total_executions > 0:
                    history.success_rate = history.successful_executions / history.total_executions
                
                durations = [e.total_duration_ms for e in executions if e.total_duration_ms > 0]
                if durations:
                    history.avg_duration_ms = int(sum(durations) / len(durations))
                    history.min_duration_ms = min(durations)
                    history.max_duration_ms = max(durations)
            
            return history
        except Exception as e:
            _LOGGER.error(f"Error getting execution history: {e}")
            return ExecutionHistory(automation_id=automation_id)

    async def get_last_execution(self, automation_id: str) -> ExecutionPath | None:
        """Get last execution details.

        Args:
            automation_id: Automation ID

        Returns:
            Last ExecutionPath or None
        """
        _LOGGER.debug(f"Getting last execution for {automation_id}")

        try:
            executions = self._execution_history.get(automation_id, [])
            return executions[-1] if executions else None
        except Exception as e:
            _LOGGER.error(f"Error getting last execution: {e}")
            return None

    async def subscribe_execution_updates(
        self,
        automation_id: str,
        callback: Callable[[dict[str, Any]], None],
    ) -> Callable[[], None]:
        """Subscribe to real-time execution updates.

        Args:
            automation_id: Automation ID
            callback: Callback function for updates

        Returns:
            Unsubscribe function
        """
        _LOGGER.debug(f"Subscribing to execution updates for {automation_id}")

        try:
            if automation_id not in self._execution_subscribers:
                self._execution_subscribers[automation_id] = []
            
            self._execution_subscribers[automation_id].append(callback)
            
            def unsubscribe() -> None:
                try:
                    if automation_id in self._execution_subscribers:
                        self._execution_subscribers[automation_id].remove(callback)
                except Exception as e:
                    _LOGGER.error(f"Error unsubscribing: {e}")
            
            return unsubscribe
        except Exception as e:
            _LOGGER.error(f"Error subscribing: {e}")
            return lambda: None

    def analyze_failures(self, automation_id: str) -> dict[str, Any]:
        """Analyze common failure patterns.

        Args:
            automation_id: Automation ID

        Returns:
            Failure analysis dictionary
        """
        _LOGGER.debug(f"Analyzing failures for {automation_id}")

        try:
            executions = self._execution_history.get(automation_id, [])
            failed_executions = [e for e in executions if e.execution_result == "failed"]
            
            if not failed_executions:
                return {
                    "automation_id": automation_id,
                    "total_failures": 0,
                    "failure_rate": 0.0,
                    "common_errors": {},
                    "last_failure": None,
                }
            
            error_counts = {}
            last_failure = None
            
            for execution in failed_executions:
                if execution.error_message:
                    error_type = execution.error_message.split(":")[0] if ":" in execution.error_message else execution.error_message
                    error_counts[error_type] = error_counts.get(error_type, 0) + 1
                    last_failure = execution
            
            failure_rate = len(failed_executions) / len(executions) if executions else 0
            
            return {
                "automation_id": automation_id,
                "total_failures": len(failed_executions),
                "total_executions": len(executions),
                "failure_rate": failure_rate,
                "common_errors": error_counts,
                "last_failure": last_failure.to_dict() if last_failure else None,
                "most_common_error": max(error_counts, key=error_counts.get) if error_counts else None,
            }
        except Exception as e:
            _LOGGER.error(f"Error analyzing failures: {e}")
            return {}
