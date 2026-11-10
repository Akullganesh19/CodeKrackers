'use client';

import { useEffect } from 'react';
import { setupPhantomFetch } from '@/utils/api-client';

export function PhantomInitializer() {
  useEffect(() => {
    setupPhantomFetch();
  }, []);

  return null;
}
