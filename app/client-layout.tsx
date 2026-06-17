'use client';
import '@/lib/fetch'; // Initialize request coalescing
import React from 'react';

export default function ClientLayout({ children }: { children: React.ReactNode }) {
    return <>{children}</>;
}
