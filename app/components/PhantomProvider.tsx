'use client'

import { initPhantomInfrastructure } from '@/lib/phantom'

// Initialize immediately outside React render cycle
initPhantomInfrastructure();

export function PhantomProvider({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
