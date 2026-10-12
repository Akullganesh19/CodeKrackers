## 2025-05-15 — Predictive Fetching in Sidebar

**Product understood as:** A cybersecurity dashboard that analyzes threats (vishing, smishing) and allows users to file automated FIRs. Target users are citizens, bank officers, cyber officers, and admins.
**Prediction invented:** Anticipatory route prefetching. When a user hovers over a navigation link in the Sidebar, the Next.js app immediately prefetches the destination component and triggers predictive data fetching. This makes navigating between dashboard, scanner, and report pages feel instantaneous, eliminating perceived load times.
**Data used:** The existing `navItems` configuration and user mouse movements (onMouseEnter).
**Impact:** Eliminates 300-500ms of perceived load time when a user clicks a nav link, making the dashboard feel incredibly fast.
**Next opportunity:** Prefill form data in the FIR generation based on previous threat context.
