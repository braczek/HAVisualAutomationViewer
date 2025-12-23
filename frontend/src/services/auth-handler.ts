/**
 * Authentication Handler for Visual AutoView
 * Handles authentication challenges including mobile app support
 */

/**
 * Mobile-specific authentication handler
 * Some Home Assistant mobile apps have specific requirements
 */
export class MobileAuthHandler {
  private static readonly DEBUG = true;

  static log(message: string, data?: any) {
    if (this.DEBUG) {
      console.log(`[Mobile Auth] ${message}`, data || '');
    }
  }

  static error(message: string, data?: any) {
    console.error(`[Mobile Auth] ${message}`, data || '');
  }

  /**
   * Check if running in a mobile app context
   */
  static isMobileApp(): boolean {
    const userAgent = navigator.userAgent.toLowerCase();
    
    // Check for known mobile HA apps
    const isMobile = 
      userAgent.includes('ha-mobile') ||
      userAgent.includes('homeassistant-mobile') ||
      userAgent.includes('companion') ||
      /android|iphone|ipod|ipad/i.test(userAgent);

    this.log('Mobile app detected:', isMobile);
    return isMobile;
  }

  /**
   * Handle CORS issues specific to mobile apps
   */
  static handleCorsError(_error: any): void {
    const isMobile = this.isMobileApp();
    
    if (isMobile) {
      this.error(
        'CORS error detected in mobile app. ' +
        'This typically means the backend needs CORS headers. ' +
        'The server should return: Access-Control-Allow-Origin: *'
      );
    }
  }

  /**
   * Get auth headers for mobile requests
   */
  static getAuthHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Try to get token and add to headers
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
      this.log('Auth headers prepared with Bearer token');
    } else {
      this.error('No authentication token found');
    }

    return headers;
  }

  /**
   * Get authentication token from all possible sources
   */
  static getToken(): string | null {
    // Try window.hass first (HA panel context)
    try {
      const hass = (window as any).hass;
      if (hass?.auth?.accessToken) {
        this.log('Token found in window.hass.auth.accessToken');
        return hass.auth.accessToken;
      }
    } catch (e) {
      this.log('Could not access window.hass.auth', e);
    }

    // Try connection object
    try {
      const connection = (window as any).hass?.connection;
      if (connection?.auth?.access_token) {
        this.log('Token found in window.hass.connection.auth.access_token');
        return connection.auth.access_token;
      }
    } catch (e) {
      this.log('Could not access window.hass.connection', e);
    }

    // Try localStorage
    try {
      const tokens = JSON.parse(localStorage.getItem('hassTokens') || '{}');
      if (tokens.access_token) {
        this.log('Token found in localStorage.hassTokens');
        return tokens.access_token;
      }
    } catch (e) {
      this.log('Could not access localStorage.hassTokens', e);
    }

    // Try URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token') || urlParams.get('access_token');
    if (token) {
      this.log('Token found in URL parameters');
      return token;
    }

    this.error('No authentication token found in any source');
    return null;
  }

  /**
   * Check if authentication is valid
   */
  static async checkAuth(): Promise<boolean> {
    const token = this.getToken();
    if (!token) {
      this.error('No token available for auth check');
      return false;
    }

    try {
      // Try to call a simple endpoint to validate auth
      const response = await fetch('/api/visualautoview/health', {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (response.status === 401 || response.status === 403) {
        this.error('Authentication failed: server returned 401/403');
        return false;
      }

      if (response.ok) {
        this.log('Authentication check passed');
        return true;
      }

      this.error(`Authentication check failed: ${response.status}`);
      return false;
    } catch (error) {
      this.error('Authentication check failed with error:', error);
      return false;
    }
  }

  /**
   * Get diagnostics info for debugging
   */
  static getDiagnostics(): Record<string, any> {
    const hass = (window as any).hass;
    const connection = (window as any).hass?.connection;
    
    return {
      userAgent: navigator.userAgent,
      isMobileApp: this.isMobileApp(),
      hasToken: !!this.getToken(),
      hasHass: !!hass,
      hasConnection: !!connection,
      hasConnectionAuth: !!connection?.auth,
      url: window.location.href,
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Log diagnostics for debugging authentication issues
   */
  static logDiagnostics(): Record<string, any> {
    const diags = this.getDiagnostics();
    this.log('Diagnostics:', diags);
    return diags;
  }
}

/**
 * Initialize auth handler on module load
 */
export function initializeAuthHandler(): void {
  if (MobileAuthHandler.isMobileApp()) {
    console.log('[Auth] Mobile app context detected. Initializing mobile auth handler.');
    MobileAuthHandler.logDiagnostics();
  } else {
    console.log('[Auth] Desktop context detected.');
  }
}
