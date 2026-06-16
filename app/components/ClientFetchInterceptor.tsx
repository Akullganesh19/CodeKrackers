'use client';

import { installGlobalFetchInterceptor } from '@/lib/fetch';

// Execute the interceptor setup at the module level
// This ensures it runs as soon as this file is loaded,
// before any child components mount and fire off their fetch calls.
if (typeof window !== 'undefined') {
  installGlobalFetchInterceptor();
}

export function ClientFetchInterceptor() {
  return null;
}
