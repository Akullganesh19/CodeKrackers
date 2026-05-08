/**
 * Decodes a JWT token without an external library.
 * JWT structure: header.payload.signature
 */
export function getDecodedToken() {
  if (typeof window === 'undefined') return null;
  
  const token = localStorage.getItem('vsdp_token');
  if (!token) return null;

  try {
    // Get the payload (middle part of the JWT)
    const base64Url = token.split('.')[1];
    let base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    // JWT base64URL often omits padding, but atob requires it in some environments
    const pad = base64.length % 4;
    if (pad) {
      base64 += '='.repeat(4 - pad);
    }
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );

    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error("Token decoding failed:", error);
    return null;
  }
}

export function hasRole(allowedRoles: string[]): boolean {
  const decoded = getDecodedToken();
  return decoded && allowedRoles.includes(decoded.role);
}

export function isTokenExpired(): boolean {
  const decoded = getDecodedToken();
  if (!decoded || !decoded.exp) return true;

  // JWT exp is in seconds, Date.now() is in milliseconds
  const currentTime = Math.floor(Date.now() / 1000);
  return decoded.exp < currentTime;
}

/**
 * Sets the session token in both localStorage and cookies.
 * Removes 'Secure' to ensure it works on localhost (HTTP).
 */
export function setSession(token: string) {
  if (typeof window !== 'undefined') {
    localStorage.setItem('vsdp_token', token);
    // Important: The cookie MUST be set for the middleware to see it.
    // We use path=/ to ensure it's available across the whole site.
    document.cookie = `vsdp_token=${token}; path=/; SameSite=Lax;`;
  }
}

/**
 * Checks if the user is fully authenticated (token + cookie + not expired).
 * Use this on your login page to prevent redirect loops.
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;
  const token = localStorage.getItem('vsdp_token');
  const hasCookie = document.cookie.includes('vsdp_token=');
  return !!token && hasCookie && !isTokenExpired();
}

export function logout() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('vsdp_token');
    // Clear cookie
    document.cookie = "vsdp_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax; path=/;";
    window.location.href = '/login';
  }
}

/**
 * Returns the time remaining until the token expires, in seconds.
 * Returns 0 if the token is expired or invalid.
 */
export function getTimeUntilTokenExpiry(): number {
  const decoded = getDecodedToken();
  if (!decoded || !decoded.exp) return 0;

  const currentTime = Math.floor(Date.now() / 1000);
  return Math.max(0, decoded.exp - currentTime);
}

/**
 * Attempts to refresh the JWT token by calling the backend.
 * If successful, updates localStorage and returns true.
 * If unsuccessful, logs out the user and returns false.
 */
export async function refreshToken(): Promise<boolean> {
  const currentToken = localStorage.getItem('vsdp_token');
  if (!currentToken) {
    logout();
    return false;
  }

  try {
    const response = await fetch('/api/v1/auth/refresh-token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${currentToken}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      if (data.access_token) {
        setSession(data.access_token);
        return true;
      }
    }
    // If response not ok or no access_token, something went wrong, so logout
    logout();
    return false;
  } catch (error) {
    console.error("Failed to refresh token:", error);
    logout();
    return false;
  }
}