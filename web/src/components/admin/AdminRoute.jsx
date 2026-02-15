'use client';
import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Spin } from 'antd';
import axios from 'axios';

export default function AdminRouteWrapper({ children }) {
    const router = useRouter();
    const [loading, setLoading] = useState(true);
    const [isVerified, setIsVerified] = useState(false);

    useEffect(() => {
        checkAccess();
    }, []);

    const checkAccess = async () => {
        try {
            // 验证token的有效性
            const token = document.cookie.split('; ').find(row => row.startsWith('admintoken='))?.split('=')[1];
            
            if (!token) {
                // 没有登录token，重定向到登录页面
                router.push('/adminLogin');
                return;
            }

            // 验证登录token
            const response = await axios.post(
                `${process.env.NEXT_PUBLIC_DJANGO_BASE_URL}/myapp/admin/verify-token`,
                {},
                {
                    headers: {
                        'Content-Type': 'application/json',
                        'admintoken': token
                    }
                }
            );

            if (response.data.success) {
                // 验证成功
                setIsVerified(true);
            } else {
                // 验证失败，重定向到登录页面
                router.push('/adminLogin');
            }
        } catch (error) {
            console.error('验证失败:', error);
            // 验证失败，重定向到登录页面
            router.push('/adminLogin');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <Spin size="large" />
            </div>
        );
    }

    if (!isVerified) {
        return null;
    }

    return children;
}
