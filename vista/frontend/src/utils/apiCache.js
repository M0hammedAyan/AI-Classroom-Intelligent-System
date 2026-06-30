/**
 * Simple in-memory API response cache with TTL.
 * Prevents redundant fetches when navigating between pages.
 */

const cache = new Map();
const DEFAULT_TTL = 30000; // 30 seconds

export function cachedFetch(url, options = {}, ttl = DEFAULT_TTL) {
  const key = `${url}|${JSON.stringify(options.headers || {})}`;
  const now = Date.now();

  // Return cached if still valid
  const cached = cache.get(key);
  if (cached && (now - cached.timestamp) < ttl) {
    return Promise.resolve(cached.data);
  }

  // Fetch fresh
  return fetch(url, options).then(async (res) => {
    if (res.ok) {
      const data = await res.json();
      cache.set(key, { data, timestamp: now });
      return data;
    }
    throw new Error(`HTTP ${res.status}`);
  });
}

export function invalidateCache(pattern) {
  if (!pattern) {
    cache.clear();
    return;
  }
  for (const key of cache.keys()) {
    if (key.includes(pattern)) {
      cache.delete(key);
    }
  }
}

export function clearCache() {
  cache.clear();
}
