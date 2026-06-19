'use client';

import React, { useEffect } from 'react';
import { initFetchInterceptor } from '@/lib/fetch';

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    initFetchInterceptor();
  }, []);

  return <>{children}</>;
}
