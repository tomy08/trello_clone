'use client'

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { isAuthenticated } from '../lib/auth';

const PUBLIC_ROUTES = ['/', '/login', '/signup'];

export default function AuthCheck() {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    isAuthenticated().then((authenticated) => {
      const isPublicRoute = PUBLIC_ROUTES.includes(pathname);
      
      if (authenticated && isPublicRoute) {
        router.push('/dashboard');
      } else if (!authenticated && !isPublicRoute) {
        router.push('/login');
      }
    });
  }, [router, pathname]);

  return null;
}