1. **Identify the missing infrastructure:** The app uses naive `fetch` everywhere. Multiple components on the same page (or even just separate pages that the user navigates between) could be fetching the same data repeatedly. We can build an intelligent caching layer, specifically a `phantomFetch` mechanism that:
   - Coalesces requests (so if two components ask for the same data at the same time, only 1 network request is made).
   - Implements a Stale-While-Revalidate (SWR) pattern: Return cached data instantly if available (improving felt latency to 0), but refresh it in the background silently.
   - Provides TTL caching.

2. **Create `app/lib/fetch.ts`:**
   Implement `phantomFetch`, a drop-in replacement for the native `fetch` API.

3. **Update endpoints to use `phantomFetch`:**
   Modify `app/dashboard/page.tsx` and `app/analytics/page.tsx` (which fetch things like `/api/analytics/dashboard-summary`) to use `phantomFetch`. This is the "hot path".

4. **Verify Correctness:**
   Ensure `npm run build` succeeds and the SWR cache mechanism degrades gracefully.

5. **Update journal and open PR.**
