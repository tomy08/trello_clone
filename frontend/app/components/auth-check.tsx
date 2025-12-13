'use client'

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '../lib/auth';

export default function AuthCheck() {
  const router = useRouter();

  useEffect(() => {
    isAuthenticated().then((authenticated) => {
      if (authenticated) {
        router.push('/dashboard');
      }
    });
  }, [router]);

  return null;
}