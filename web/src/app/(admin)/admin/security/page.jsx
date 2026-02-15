'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function SecurityPage() {
  const router = useRouter();
  
  useEffect(() => {
    // 重定向到安全事件页面
    router.push('/admin/security/events');
  }, []);
  
  return null;
}