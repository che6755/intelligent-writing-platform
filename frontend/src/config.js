const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export function getWebSocketUrl(path) {
  const apiUrl = new URL(API_BASE_URL, window.location.origin);
  const protocol = apiUrl.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${apiUrl.host}${path}`;
}

export { API_BASE_URL };
