"use client";

import { useEffect } from "react";
import "../lib/fetch";

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  // The fetch interceptor is evaluated as soon as the module is imported,
  // which happens on the client side because of the "use client" directive.
  return <>{children}</>;
}
