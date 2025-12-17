/**
 * Frontend Utility Functions
 */

/**
 * Format milliseconds to human-readable time string
 */
export function formatTime(ms: number): string {
  if (ms < 1000) {
    return `${Math.round(ms)}ms`;
  } else if (ms < 60000) {
    return `${(ms / 1000).toFixed(2)}s`;
  } else {
    return `${(ms / 60000).toFixed(2)}m`;
  }
}

/**
 * Format percentage value
 */
export function formatPercent(value: number, decimals = 1): string {
  return `${value.toFixed(decimals)}%`;
}

/**
 * Truncate text to specified length
 */
export function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.substring(0, length - 3) + '...';
}

/**
 * Debounce function for search/filter inputs
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout>;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };

    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Get color for automation status
 */
export function getStatusColor(status: 'success' | 'failure' | 'warning'): string {
  const colors = {
    success: '#4CAF50',
    failure: '#F44336',
    warning: '#FFC107',
  };
  return colors[status];
}

/**
 * Get badge class for metric status
 */
export function getBadgeClass(metric: number, thresholds: { warning: number; danger: number }): string {
  if (metric >= thresholds.danger) return 'danger';
  if (metric >= thresholds.warning) return 'warning';
  return 'success';
}

/**
 * Parse automation entity ID
 */
export function parseEntityId(entityId: string): { domain: string; name: string } {
  const [domain, ...nameParts] = entityId.split('.');
  return {
    domain,
    name: nameParts.join('.'),
  };
}

/**
 * Generate unique ID
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Deep clone object
 */
export function deepClone<T>(obj: T): T {
  return JSON.parse(JSON.stringify(obj));
}

/**
 * Get initials from name
 */
export function getInitials(name: string): string {
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .toUpperCase()
    .substring(0, 2);
}

/**
 * Sort array by property
 */
export function sortBy<T>(array: T[], property: keyof T, ascending = true): T[] {
  return [...array].sort((a, b) => {
    const aVal = a[property];
    const bVal = b[property];

    if (aVal < bVal) return ascending ? -1 : 1;
    if (aVal > bVal) return ascending ? 1 : -1;
    return 0;
  });
}

/**
 * Group array by property
 */
export function groupBy<T>(array: T[], property: keyof T): Record<string, T[]> {
  return array.reduce(
    (groups, item) => {
      const key = String(item[property]);
      if (!groups[key]) {
        groups[key] = [];
      }
      groups[key].push(item);
      return groups;
    },
    {} as Record<string, T[]>
  );
}

/**
 * Validate email address
 */
export function isValidEmail(email: string): boolean {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

/**
 * Convert camelCase to space-separated
 */
export function toTitleCase(str: string): string {
  return str
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, (str) => str.toUpperCase())
    .trim();
}
