"""Performance Metrics Service for Visual AutoView.

This service tracks and analyzes automation performance metrics including
execution frequency, duration, and success rate.
"""

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Literal

_LOGGER = logging.getLogger(__name__)


@dataclass
class ExecutionMetrics:
    """Metrics for automation executions."""

    automation_id: str

    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    skipped_executions: int = 0

    success_rate: float = 0.0
    failure_rate: float = 0.0

    min_duration_ms: int = 0
    max_duration_ms: int = 0
    avg_duration_ms: float = 0.0
    median_duration_ms: int = 0
    p95_duration_ms: int = 0
    p99_duration_ms: int = 0

    common_errors: dict[str, int] = field(default_factory=dict)
    last_error: str | None = None
    last_error_time: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        if self.last_error_time:
            result["last_error_time"] = self.last_error_time.isoformat()
        return result


@dataclass
class TemporalPattern:
    """Pattern of automation triggering over time."""

    pattern_type: Literal["hourly", "daily", "weekly", "monthly"]

    data: dict[str, float] = field(default_factory=dict)
    peak_time: str = ""
    peak_count: int = 0

    average_per_period: float = 0.0
    std_deviation: float = 0.0
    trend: Literal["increasing", "decreasing", "stable"] = "stable"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class PerformanceMetricsReport:
    """Complete performance report for single automation."""

    automation_id: str
    automation_alias: str

    metrics: ExecutionMetrics = field(default_factory=ExecutionMetrics)

    hourly_pattern: TemporalPattern | None = None
    daily_pattern: TemporalPattern | None = None
    weekly_pattern: TemporalPattern | None = None

    is_high_frequency: bool = False
    is_slow: bool = False
    is_unreliable: bool = False

    optimization_suggestions: list[str] = field(default_factory=list)

    performance_rank: int = 50
    comparison_group: str = ""
    above_average: bool = True

    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    period_label: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "automation_id": self.automation_id,
            "automation_alias": self.automation_alias,
            "metrics": self.metrics.to_dict(),
            "hourly_pattern": (
                self.hourly_pattern.to_dict() if self.hourly_pattern else None
            ),
            "daily_pattern": (
                self.daily_pattern.to_dict() if self.daily_pattern else None
            ),
            "weekly_pattern": (
                self.weekly_pattern.to_dict() if self.weekly_pattern else None
            ),
            "is_high_frequency": self.is_high_frequency,
            "is_slow": self.is_slow,
            "is_unreliable": self.is_unreliable,
            "optimization_suggestions": self.optimization_suggestions,
            "performance_rank": self.performance_rank,
            "comparison_group": self.comparison_group,
            "above_average": self.above_average,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "period_label": self.period_label,
        }


@dataclass
class SystemPerformanceMetrics:
    """System-wide performance metrics."""

    total_automations: int = 0
    active_automations: int = 0
    total_executions: int = 0
    total_failed_executions: int = 0

    avg_execution_time_ms: float = 0.0
    total_execution_time_ms: int = 0
    peak_concurrent_executions: int = 0

    overall_success_rate: float = 0.0
    most_common_error: str | None = None

    slowest_automations: list[tuple[str, int]] = field(default_factory=list)
    most_frequent_automations: list[tuple[str, int]] = field(default_factory=list)
    most_failing_automations: list[tuple[str, float]] = field(default_factory=list)

    execution_trend: Literal["increasing", "decreasing", "stable"] = "stable"
    error_trend: Literal["improving", "worsening", "stable"] = "stable"

    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_automations": self.total_automations,
            "active_automations": self.active_automations,
            "total_executions": self.total_executions,
            "total_failed_executions": self.total_failed_executions,
            "avg_execution_time_ms": self.avg_execution_time_ms,
            "total_execution_time_ms": self.total_execution_time_ms,
            "peak_concurrent_executions": self.peak_concurrent_executions,
            "overall_success_rate": self.overall_success_rate,
            "most_common_error": self.most_common_error,
            "slowest_automations": self.slowest_automations,
            "most_frequent_automations": self.most_frequent_automations,
            "most_failing_automations": self.most_failing_automations,
            "execution_trend": self.execution_trend,
            "error_trend": self.error_trend,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
        }


class PerformanceMetricsService:
    """Service for tracking and analyzing automation performance metrics."""

    def __init__(self, hass: Any) -> None:
        """Initialize the service.

        Args:
            hass: Home Assistant instance
        """
        self.hass = hass
        self._metrics_storage: dict[str, ExecutionMetrics] = {}
        self._pattern_analysis: dict[str, list[TemporalPattern]] = {}

        _LOGGER.debug("PerformanceMetricsService initialized")

    async def record_execution(
        self,
        automation_id: str,
        duration_ms: int,
        success: bool,
        error: str | None = None,
    ) -> None:
        """Record execution metrics.

        Args:
            automation_id: Automation ID
            duration_ms: Execution duration in milliseconds
            success: Whether execution was successful
            error: Error message if failed
        """
        _LOGGER.debug(
            f"Recording execution for {automation_id}: {duration_ms}ms, success={success}"
        )

        try:
            if automation_id not in self._metrics_storage:
                self._metrics_storage[automation_id] = ExecutionMetrics(
                    automation_id=automation_id
                )

            metrics = self._metrics_storage[automation_id]
            metrics.total_executions += 1

            if success:
                metrics.successful_executions += 1
            else:
                metrics.failed_executions += 1
                if error:
                    error_type = error.split(":")[0] if ":" in error else error
                    metrics.common_errors[error_type] = (
                        metrics.common_errors.get(error_type, 0) + 1
                    )
                    metrics.last_error = error
                    metrics.last_error_time = datetime.now()

            # Update duration metrics
            if duration_ms > 0:
                if (
                    metrics.min_duration_ms == 0
                    or duration_ms < metrics.min_duration_ms
                ):
                    metrics.min_duration_ms = duration_ms
                metrics.max_duration_ms = max(metrics.max_duration_ms, duration_ms)

                # Simple moving average
                metrics.avg_duration_ms = (
                    metrics.avg_duration_ms * (metrics.total_executions - 1)
                    + duration_ms
                ) / metrics.total_executions

            # Update rates
            metrics.success_rate = (
                metrics.successful_executions / metrics.total_executions
                if metrics.total_executions > 0
                else 0
            )
            metrics.failure_rate = (
                metrics.failed_executions / metrics.total_executions
                if metrics.total_executions > 0
                else 0
            )

        except Exception as e:
            _LOGGER.error(f"Error recording execution: {e}")

    async def get_execution_metrics(
        self,
        automation_id: str,
        period: Literal["day", "week", "month", "30days", "year"] = "30days",
    ) -> ExecutionMetrics:
        """Get execution metrics for specific automation.

        Args:
            automation_id: Automation ID
            period: Time period to analyze

        Returns:
            ExecutionMetrics object
        """
        _LOGGER.debug(f"Getting metrics for {automation_id} (period={period})")

        try:
            if automation_id in self._metrics_storage:
                return self._metrics_storage[automation_id]
            else:
                return ExecutionMetrics(automation_id=automation_id)
        except Exception as e:
            _LOGGER.error(f"Error getting metrics: {e}")
            return ExecutionMetrics(automation_id=automation_id)

    async def analyze_temporal_patterns(
        self,
        automation_id: str,
        period: Literal["day", "week", "month"] = "month",
    ) -> list[TemporalPattern]:
        """Analyze temporal patterns of automation.

        Args:
            automation_id: Automation ID
            period: Pattern analysis period

        Returns:
            List of TemporalPattern objects
        """
        _LOGGER.debug(
            f"Analyzing temporal patterns for {automation_id} (period={period})"
        )

        try:
            patterns = []

            # Create patterns for different time granularities
            if period in ["day", "month"]:
                hourly = TemporalPattern(
                    pattern_type="hourly",
                    data={str(h): 0.0 for h in range(24)},
                    peak_time="12:00",
                    peak_count=0,
                    average_per_period=0.0,
                    trend="stable",
                )
                patterns.append(hourly)

            if period in ["week", "month"]:
                daily = TemporalPattern(
                    pattern_type="daily",
                    data={
                        d: 0.0
                        for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                    },
                    peak_time="Tuesday",
                    peak_count=0,
                    average_per_period=0.0,
                    trend="stable",
                )
                patterns.append(daily)

            if period == "month":
                weekly = TemporalPattern(
                    pattern_type="weekly",
                    data={f"Week{w}": 0.0 for w in range(1, 5)},
                    peak_time="Week 2",
                    peak_count=0,
                    average_per_period=0.0,
                    trend="stable",
                )
                patterns.append(weekly)

            return patterns

        except Exception as e:
            _LOGGER.error(f"Error analyzing patterns: {e}")
            return []

    async def get_performance_report(
        self, automation_id: str
    ) -> PerformanceMetricsReport:
        """Get comprehensive performance report.

        Args:
            automation_id: Automation ID

        Returns:
            PerformanceMetricsReport object
        """
        _LOGGER.debug(f"Getting performance report for {automation_id}")

        try:
            metrics = await self.get_execution_metrics(automation_id)
            patterns = await self.analyze_temporal_patterns(automation_id)

            report = PerformanceMetricsReport(
                automation_id=automation_id,
                automation_alias=automation_id.split(".")[-1],
                metrics=metrics,
                hourly_pattern=patterns[0] if len(patterns) > 0 else None,
                daily_pattern=patterns[1] if len(patterns) > 1 else None,
                weekly_pattern=patterns[2] if len(patterns) > 2 else None,
                is_high_frequency=metrics.total_executions > 10,
                is_slow=metrics.avg_duration_ms > 5000,
                is_unreliable=metrics.failure_rate > 0.1,
                performance_rank=self.calculate_performance_rank(
                    automation_id, "speed"
                ),
            )

            if metrics.total_executions > 5:
                report.above_average = metrics.success_rate > 0.8

            return report

        except Exception as e:
            _LOGGER.error(f"Error getting performance report: {e}")
            return PerformanceMetricsReport(automation_id=automation_id)

    async def get_system_metrics(self) -> SystemPerformanceMetrics:
        """Get system-wide performance metrics.

        Returns:
            SystemPerformanceMetrics object
        """
        _LOGGER.debug("Getting system performance metrics")

        try:
            system_metrics = SystemPerformanceMetrics()

            if not self._metrics_storage:
                return system_metrics

            system_metrics.total_automations = len(self._metrics_storage)
            system_metrics.active_automations = len(
                [m for m in self._metrics_storage.values() if m.total_executions > 0]
            )

            total_exec_time = 0
            all_durations = []
            all_errors = {}

            for metrics in self._metrics_storage.values():
                system_metrics.total_executions += metrics.total_executions
                system_metrics.total_failed_executions += metrics.failed_executions
                total_exec_time += int(
                    metrics.avg_duration_ms * metrics.total_executions
                )

                if metrics.avg_duration_ms > 0:
                    all_durations.append(
                        (metrics.automation_id, int(metrics.avg_duration_ms))
                    )

                for error, count in metrics.common_errors.items():
                    all_errors[error] = all_errors.get(error, 0) + count

            if system_metrics.total_executions > 0:
                system_metrics.avg_execution_time_ms = (
                    total_exec_time / system_metrics.total_executions
                )
                system_metrics.overall_success_rate = (
                    system_metrics.total_executions
                    - system_metrics.total_failed_executions
                ) / system_metrics.total_executions

            system_metrics.total_execution_time_ms = total_exec_time

            # Find slowest and most frequent
            if all_durations:
                all_durations.sort(key=lambda x: x[1], reverse=True)
                system_metrics.slowest_automations = [
                    (aid, dur) for aid, dur in all_durations[:5]
                ]

            system_metrics.most_common_error = (
                max(all_errors, key=all_errors.get) if all_errors else None
            )

            return system_metrics

        except Exception as e:
            _LOGGER.error(f"Error getting system metrics: {e}")
            return SystemPerformanceMetrics()

    async def identify_optimization_opportunities(
        self, automation_id: str
    ) -> list[str]:
        """Generate optimization suggestions.

        Args:
            automation_id: Automation ID

        Returns:
            List of optimization suggestions
        """
        _LOGGER.debug(f"Identifying optimization opportunities for {automation_id}")

        try:
            suggestions = []
            metrics = await self.get_execution_metrics(automation_id)

            if metrics.avg_duration_ms > 5000:
                suggestions.append(
                    f"Automation is slow ({metrics.avg_duration_ms}ms avg). Consider optimizing conditions or actions."
                )

            if metrics.failure_rate > 0.1:
                suggestions.append(
                    f"High failure rate ({metrics.failure_rate * 100:.1f}%). Review error logs and conditions."
                )

            if metrics.failure_rate > 0.2 and metrics.last_error:
                suggestions.append(
                    f"Common error: '{metrics.last_error}'. Address root cause."
                )

            if (
                metrics.total_executions > 100
                and metrics.max_duration_ms > metrics.avg_duration_ms * 2
            ):
                suggestions.append(
                    "High variance in execution time. Check for conditional delays or race conditions."
                )

            return suggestions

        except Exception as e:
            _LOGGER.error(f"Error identifying opportunities: {e}")
            return []

    def calculate_performance_rank(
        self,
        automation_id: str,
        metric: Literal["speed", "frequency", "reliability"] = "speed",
    ) -> int:
        """Calculate performance percentile (0-100).

        Args:
            automation_id: Automation ID
            metric: Metric to rank by

        Returns:
            Percentile rank (0-100)
        """
        try:
            if automation_id not in self._metrics_storage or not self._metrics_storage:
                return 50

            metrics = self._metrics_storage[automation_id]
            all_metrics = list(self._metrics_storage.values())

            if metric == "speed":
                # Rank by avg duration (lower is better)
                durations = [
                    m.avg_duration_ms for m in all_metrics if m.avg_duration_ms > 0
                ]
                if not durations or metrics.avg_duration_ms == 0:
                    return 50

                sorted_durations = sorted(durations)
                position = sorted_durations.index(metrics.avg_duration_ms)
                return int(
                    (len(sorted_durations) - position) / len(sorted_durations) * 100
                )

            elif metric == "frequency":
                # Rank by execution count
                counts = [m.total_executions for m in all_metrics]
                if not counts:
                    return 50

                sorted_counts = sorted(counts, reverse=True)
                if metrics.total_executions not in sorted_counts:
                    return 50

                position = sorted_counts.index(metrics.total_executions)
                return int((len(sorted_counts) - position) / len(sorted_counts) * 100)

            elif metric == "reliability":
                # Rank by success rate
                rates = [m.success_rate for m in all_metrics]
                if not rates:
                    return 50

                sorted_rates = sorted(rates, reverse=True)
                if metrics.success_rate not in sorted_rates:
                    return 50

                position = sorted_rates.index(metrics.success_rate)
                return int((len(sorted_rates) - position) / len(sorted_rates) * 100)

            return 50

        except Exception as e:
            _LOGGER.error(f"Error calculating rank: {e}")
            return 50

    async def export_metrics(
        self,
        automation_ids: list[str],
        format: Literal["csv", "json", "pdf"] = "json",
    ) -> bytes:
        """Export metrics in specified format.

        Args:
            automation_ids: List of automation IDs
            format: Export format

        Returns:
            Exported data as bytes
        """
        _LOGGER.debug(
            f"Exporting metrics for {len(automation_ids)} automations (format={format})"
        )

        try:
            import json

            if format == "json":
                data = {}
                for auto_id in automation_ids:
                    if auto_id in self._metrics_storage:
                        data[auto_id] = self._metrics_storage[auto_id].to_dict()

                return json.dumps(data, indent=2).encode("utf-8")

            elif format == "csv":
                import io

                output = io.StringIO()
                output.write(
                    "automation_id,total_executions,successful,failed,success_rate,avg_duration_ms\n"
                )

                for auto_id in automation_ids:
                    if auto_id in self._metrics_storage:
                        m = self._metrics_storage[auto_id]
                        output.write(
                            f"{auto_id},{m.total_executions},{m.successful_executions},"
                            f"{m.failed_executions},{m.success_rate:.2f},{m.avg_duration_ms:.0f}\n"
                        )

                return output.getvalue().encode("utf-8")

            else:  # pdf
                # Simple PDF-like text export
                output = "PERFORMANCE METRICS REPORT\n"
                output += "=" * 60 + "\n\n"

                for auto_id in automation_ids:
                    if auto_id in self._metrics_storage:
                        m = self._metrics_storage[auto_id]
                        output += f"Automation: {auto_id}\n"
                        output += f"  Total Executions: {m.total_executions}\n"
                        output += f"  Success Rate: {m.success_rate * 100:.1f}%\n"
                        output += f"  Avg Duration: {m.avg_duration_ms:.0f}ms\n"
                        output += "\n"

                return output.encode("utf-8")

        except Exception as e:
            _LOGGER.error(f"Error exporting metrics: {e}")
            return b""
