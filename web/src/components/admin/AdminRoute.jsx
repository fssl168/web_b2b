import { redirect } from 'next/navigation';
import { headers } from 'next/headers';

export async function AdminProtectedRoute() {
  // 从请求头中获取token
  const token = headers().get('admintoken');
  
  // 如果没有token，重定向到登录页面
  if (!token) {
    redirect('/adminLogin');
  }
  
  // 验证token的有效性
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/api/admin/verify-token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'admintoken': token
      }
    });
    
    if (!response.ok) {
      redirect('/adminLogin');
    }
    
    const data = await response.json();
    if (!data.success) {
      redirect('/adminLogin');
    }
  } catch (error) {
    redirect('/adminLogin');
  }
  
  return null;
}

export default async function AdminRouteWrapper({ children }) {
  await AdminProtectedRoute();
  return children;
}