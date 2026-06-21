'use client';

import { setupFetchInterceptor } from '@/lib/fetch';

// Initialize the fetch interceptor on the client side before React renders
setupFetchInterceptor();

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
