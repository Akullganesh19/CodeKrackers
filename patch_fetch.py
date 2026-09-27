import re

with open('backend/core/PhantomInfrastructure.tsx', 'r') as f:
    content = f.read()

# Fix unhandled promise rejection by adding .catch to backgroundPromise
content = content.replace(
'''      const backgroundPromise = originalFetch(input, init).then(res => {
        if (res.ok) {
          const cacheClone = res.clone();
          cacheClone.text().then(text => {
            cache.set(cacheKey, {
              data: text,
              timestamp: Date.now(),
              headers: res.headers
            });
          }).catch(() => {}); // Silent catch for background cache write
        }
        return res;
      }).finally(() => {
        inFlightRequests.delete(cacheKey);
      });''',
'''      const backgroundPromise = originalFetch(input, init).then(res => {
        if (res.ok) {
          const cacheClone = res.clone();
          cacheClone.text().then(text => {
            cache.set(cacheKey, {
              data: text,
              timestamp: Date.now(),
              headers: res.headers
            });
          }).catch(() => {}); // Silent catch for background cache write
        }
        return res;
      }).finally(() => {
        inFlightRequests.delete(cacheKey);
      });
      // Attach catch purely to prevent unhandled rejection since backgroundPromise is not awaited
      backgroundPromise.catch(() => {});'''
)

with open('backend/core/PhantomInfrastructure.tsx', 'w') as f:
    f.write(content)
