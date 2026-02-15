import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';

export default async function Page() {
  // 从cookie中获取token
  const cookieStore = await cookies();
  const token = cookieStore.get('admintoken')?.value;
  
  // 如果没有token，重定向到登录页面
  if (!token) {
    redirect('/adminLogin');
  }
  
  // 验证token的有效性
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_DJANGO_BASE_URL}/myapp/admin/verify-token`, {
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
  
  // 验证通过，重定向到主页面
  redirect('/admin/main');
  
  return null;
}