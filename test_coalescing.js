const fs = require('fs');

async function run() {
  const code = fs.readFileSync('app/components/PhantomProvider.tsx', 'utf8');
  console.log("Implementation checked:", code.includes('inFlightRequests.has(cacheKey)') && code.includes('inFlightRequests.set(cacheKey, fetchPromise)'));
}
run();
