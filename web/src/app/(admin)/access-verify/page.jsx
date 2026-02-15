'use client';
import React, { useState } from 'react';
import { Button, Input, message, Spin } from 'antd';
import axios from 'axios';
import { useRouter } from 'next/navigation';

export default function AccessVerify() {
    const router = useRouter();
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [year, setYear] = useState(new Date().getFullYear());

    const handlePasswordChange = (e) => {
        setPassword(e.target.value);
    };

    const verifyAccess = async () => {
        if (!password) {
            message.error('请输入访问密码');
            return;
        }

        setLoading(true);

        try {
            const response = await axios.post(
                `${process.env.NEXT_PUBLIC_DJANGO_BASE_URL}/myapp/admin/verify-access`,
                { password },
                {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    withCredentials: true, // 确保cookie被发送
                }
            );

            if (response.data.code === 0) {
                message.success('访问验证成功，正在跳转...');
                // 验证成功后，跳转到后台登录页面
                setTimeout(() => {
                    router.push('/adminLogin');
                }, 1000);
            } else {
                message.error(response.data.msg || '访问验证失败');
            }
        } catch (error) {
            console.error('访问验证失败:', error);
            message.error('访问验证失败，请稍后重试');
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            verifyAccess();
        }
    };

    const bgImage = "linear-gradient(to right, #92fe9d 0%, #00c9ff 100%)";

    return (
        <div
            style={{
                backgroundImage: `${bgImage}`,
                backgroundSize: "cover",
                backgroundPosition: "center",
                backgroundRepeat: "no-repeat",
            }} className="min-h-screen w-full flex flex-col items-center justify-center"
        >
            {/* 背景装饰元素 */}
            <div className="absolute inset-0 z-0 overflow-hidden">
                <div className="absolute -top-10 -left-10 w-40 h-40 bg-blue-100 rounded-full opacity-50 blur-3xl hidden sm:block"></div>
                <div className="absolute top-1/3 -right-20 w-60 h-60 bg-indigo-100 rounded-full opacity-40 blur-3xl"></div>
                <div className="absolute -bottom-20 left-1/3 w-80 h-80 bg-cyan-100 rounded-full opacity-30 blur-3xl hidden sm:block"></div>
            </div>

            <div className="z-10 w-full max-w-sm px-4 sm:px-0">
                {/* 品牌标识 */}
                <div className="text-center mb-4">
                    <h1 className="text-lg sm:text-xl font-bold text-gray-800 tracking-wide mb-1">网站后台访问验证</h1>
                    <p className="text-gray-500 text-xs sm:text-sm">请输入访问密码以继续</p>
                </div>

                {/* 验证卡片 */}
                <div className="bg-white/80 backdrop-blur-lg rounded shadow-md p-4 sm:p-6 border border-gray-100">
                    <div className="flex items-center justify-center h-10 sm:h-12 w-10 sm:w-12 bg-gradient-to-r from-blue-500 to-cyan-500 mx-auto mb-3 sm:mb-4 shadow-lg">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 sm:h-6 sm:w-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="square" strokeLinejoin="miter">
                            <path d="M12 15v2"></path>
                            <path d="M12 3a6 6 0 0 1 6 6v3a6 6 0 1 1-12 0V9a6 6 0 0 1 6-6z"></path>
                        </svg>
                    </div>

                    <h2 className="text-base sm:text-lg font-semibold text-center mb-3 sm:mb-4 text-gray-800">访问验证</h2>

                    <div className="space-y-3 sm:space-y-4">
                        <div className="space-y-1">
                            <label className="block text-xs font-medium text-gray-700" htmlFor="password">
                                访问密码
                            </label>
                            <Input.Password
                                prefix={
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="square" strokeLinejoin="miter">
                                        <path d="M12 15v2"></path>
                                        <path d="M12 3a6 6 0 0 1 6 6v3a6 6 0 1 1-12 0V9a6 6 0 0 1 6-6z"></path>
                                    </svg>
                                }
                                placeholder="请输入后台访问密码"
                                value={password}
                                onChange={handlePasswordChange}
                                onKeyPress={handleKeyPress}
                                className="py-1"
                                size="middle"
                                style={{ borderRadius: '2px' }}
                            />
                        </div>

                        <div className="pt-3">
                            <Button
                                loading={loading}
                                type="primary"
                                className="w-full h-8 sm:h-9 bg-gradient-to-r from-blue-500 to-cyan-500 border-0 shadow-md transition-all"
                                onClick={verifyAccess}
                                size="middle"
                                style={{ borderRadius: '2px' }}
                            >
                                {loading ? '验证中...' : '验证访问'}
                            </Button>
                        </div>
                    </div>
                </div>

                {/* 底部信息 */}
                <div className="mt-4 sm:mt-6 text-center text-gray-500 text-xs">
                    <p>安全连接 | 后台访问验证</p>
                    <p className="mt-1">© {year} 企业内容管理系统. 保留所有权利</p>
                </div>
            </div>
        </div>
    );
}
