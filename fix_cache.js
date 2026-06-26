const fs = require('fs');
const content = fs.readFileSync('app/sms-scanner/page.tsx', 'utf8');

// The code currently has:
// prefetchCache.current[trimmedText] = fetchPromise;
// If the promise fails, we should delete it from the cache.

let newContent = content.replace(
  "prefetchCache.current[trimmedText] = fetchPromise;",
  `prefetchCache.current[trimmedText] = fetchPromise;

      // Don't cache failures so users can retry
      fetchPromise.then(res => {
        if (!res.ok) delete prefetchCache.current[trimmedText];
      });`
);

fs.writeFileSync('app/sms-scanner/page.tsx', newContent);
console.log('Fixed cache');
