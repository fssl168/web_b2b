import React, {useState, useEffect} from 'react';
import {Button, Input, Spin, App, Modal, message as AntdMessage} from "antd";
import axiosInstance, { setCookie } from "@/utils/axios";
import {useRouter} from "next/navigation";
import { UserOutlined } from '@ant-design/icons';

const LoginPage = () => {
    const router = useRouter();
    const { message } = App.useApp();
    const [loading, setLoading] = useState(false);
    const [year, setYear] = useState(new Date().getFullYear());

    const [currentItem, setCurrentItem] = useState({
        username: "",
        password: "",
        captcha: ""
    });
    const [captchaKey, setCaptchaKey] = useState("");
    const [captchaUrl, setCaptchaUrl] = useState("");

    const [wechat, setWechat] = useState("");
    const [show2FAModal, setShow2FAModal] = useState(false);
    const [twoFactorCode, setTwoFactorCode] = useState("");
    const [tempToken, setTempToken] = useState("");
    const [emailMasked, setEmailMasked] = useState("");
    const [verifying2FA, setVerifying2FA] = useState(false);

    useEffect(() => {
        setYear(new Date().getFullYear());
        getInfo();
        refreshCaptcha();
    }, []);

    const refreshCaptcha = () => {
        const newKey = Date.now().toString();
        setCaptchaKey(newKey);
        const url = `${process.env.NEXT_PUBLIC_BASE_URL}/myapp/admin/captcha?key=${newKey}&t=${Date.now()}`;
        setCaptchaUrl(url);
    };

    const handleInputChange = (name, value) => {
        setCurrentItem((prev) => ({...prev, [name]: value}));
    };

    const verify2FA = async () => {
        if (!twoFactorCode) {
            message.error('验证码不能为空');
            return;
        }
        try {
            setVerifying2FA(true);
            const url = `${process.env.NEXT_PUBLIC_DJANGO_BASE_URL}/myapp/admin/verify-2fa-login`;
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    temp_token: tempToken,
                    code: twoFactorCode
                })
            });
            
            const {code, msg, data} = await response.json();
            if (code === 0) {
                message.success("登录成功");
                setCookie('admintoken', data.admin_token);
                setCookie('username', data.username);
                setShow2FAModal(false);
                // 添加短暂延迟，确保cookie被正确设置
                setTimeout(() => {
                    router.push('/admin/main');
                }, 100);
            } else {
                message.error(msg || '验证失败');
            }
            setVerifying2FA(false);
        } catch (err) {
            message.error('网络异常');
            setVerifying2FA(false);
        }
    };

    const login = async () => {
        if (currentItem.username.length === 0 || currentItem.password.length === 0) {
            message.error('用户名或密码不能为空');
            return;
        }
        if (currentItem.captcha.length === 0) {
            message.error('验证码不能为空');
            return;
        }
        try {
            setLoading(true);
            const url = `${process.env.NEXT_PUBLIC_DJANGO_BASE_URL}/myapp/admin/adminLogin`;
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: currentItem.username,
                    password: currentItem.password,
                    captcha_code: currentItem.captcha,
                    captcha_key: captchaKey
                })
            });
            
            const {code, msg, data} = await response.json();
            if (code === 0) {
                message.success("登录成功");
                setCookie('admintoken', data.admin_token);
                setCookie('username', data.username);
                // 添加短暂延迟，确保cookie被正确设置
                setTimeout(() => {
                    router.push('/admin/main');
                }, 100);
            } else if (code === 3) {
                // 需要双因素认证
                setTempToken(data.temp_token);
                setEmailMasked(data.email_masked);
                setShow2FAModal(true);
                message.info('请输入邮箱验证码');
            } else {
                message.error(msg || '网络异常');
                refreshCaptcha();
            }
            setLoading(false);
        } catch (err) {
            message.error('网络异常');
            refreshCaptcha();
            setLoading(false);
        }
    };

    const getInfo = async () => {
        if (typeof window === 'undefined') {
            return;
        }
        
        try {
            const url = `${process.env.NEXT_PUBLIC_DJANGO_BASE_URL}/myapp/admin/basicGlobal/listInfo`;
            const response = await fetch(url);
            const {code, msg, data} = await response.json();
            if(code === 0){
                setWechat(data.global_wechat);
            }
        } catch (err) {
            if (typeof window !== 'undefined') {
                message.error('网络异常');
            }
        }
    };

    const handleKeyPress = (e) => {
        if(e.key === 'Enter'){
            login();
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
        }} className="min-h-screen w-full flex flex-col items-center justify-center">
            <div className="absolute inset-0 z-0 overflow-hidden">
                <div className="absolute -top-10 -left-10 w-40 h-40 bg-blue-100 rounded-full opacity-50 blur-3xl hidden sm:block"></div>
                <div className="absolute top-1/3 -right-20 w-60 h-60 bg-indigo-100 rounded-full opacity-40 blur-3xl"></div>
                <div className="absolute -bottom-20 left-1/3 w-80 h-80 bg-cyan-100 rounded-full opacity-30 blur-3xl hidden sm:block"></div>
            </div>
            
            <div className="z-10 w-full max-w-sm px-4 sm:px-0">
                <div className="text-center mb-4">
                    <h1 className="text-lg sm:text-xl font-bold text-gray-800 tracking-wide mb-1">网站后台内容管理系统</h1>
                    <p className="text-gray-500 text-xs sm:text-sm">专业的企业官网内容管理平台</p>
                </div>
                
                <div className="bg-white/80 backdrop-blur-lg rounded shadow-md p-4 sm:p-6 border border-gray-100">
                    <div className="flex items-center justify-center h-10 sm:h-12 w-10 sm:w-12 bg-gradient-to-r from-blue-500 to-cyan-500 mx-auto mb-3 sm:mb-4 shadow-lg">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 sm:h-6 sm:w-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="square" strokeLinejoin="miter">
                            <rect x="3" y="11" width="18" height="11" rx="1" />
                            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                        </svg>
                    </div>
                    
                    <h2 className="text-base sm:text-lg font-semibold text-center mb-3 sm:mb-4 text-gray-800">管理员登录</h2>
                    
                    <div className="space-y-3 sm:space-y-4">
                        <div className="space-y-1">
                            <label className="block text-xs font-medium text-gray-700" htmlFor="username">
                                用户名
                            </label>
                            <Input 
                                prefix={<UserOutlined className="site-form-item-icon text-gray-400" />}
                                placeholder="请输入管理员用户名" 
                                value={currentItem.username}
                                onChange={(e) => handleInputChange("username", e.target.value)}
                                onKeyPress={handleKeyPress}
                                className="py-1"
                                size="middle"
                                style={{ borderRadius: '2px' }}
                            />
                        </div>
                        
                        <div className="space-y-1">
                            <label className="block text-xs font-medium text-gray-700" htmlFor="password">
                                密码
                            </label>
                            <Input.Password 
                                prefix={
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="square" strokeLinejoin="miter">
                                        <rect x="3" y="11" width="18" height="11" rx="1" />
                                        <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                                    </svg>
                                }
                                placeholder="请输入管理员密码"
                                value={currentItem.password}
                                onChange={(e) => handleInputChange("password", e.target.value)}
                                onKeyPress={handleKeyPress}
                                className="py-1"
                                size="middle"
                                style={{ borderRadius: '2px' }}
                            />
                        </div>

                        <div className="space-y-1">
                            <label className="block text-xs font-medium text-gray-700" htmlFor="captcha">
                                验证码
                            </label>
                            <div className="flex gap-2">
                                <Input
                                    placeholder="请输入验证码"
                                    value={currentItem.captcha}
                                    onChange={(e) => handleInputChange("captcha", e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    className="py-1 flex-1"
                                    size="middle"
                                    style={{ borderRadius: '2px' }}
                                />
                                <div
                                    className="h-8 w-24 sm:w-32 cursor-pointer"
                                    onClick={refreshCaptcha}
                                    title="点击刷新验证码"
                                >
                                    <img
                                        src={captchaUrl || null}
                                        alt="验证码"
                                        className="h-full w-full object-cover rounded"
                                        style={{ borderRadius: '2px' }}
                                    />
                                </div>
                            </div>
                            <p className="text-xs text-gray-400 mt-1">点击图片可刷新验证码</p>
                        </div>
                        
                        <div className="pt-3">
                            <Button 
                                loading={loading} 
                                type="primary" 
                                className="w-full h-8 sm:h-9 bg-gradient-to-r from-blue-500 to-cyan-500 border-0 shadow-md transition-all"
                                onClick={() => login()}
                                size="middle"
                                style={{ borderRadius: '2px' }}
                            >
                                {loading ? '登录中...' : '登录'}
                            </Button>
                        </div>
                    </div>
                </div>
                
                <div className="mt-4 sm:mt-6 text-center text-gray-500 text-xs">
                    <p>安全连接 | 管理员专用入口</p>
                    <p className="mt-1">© {year} 企业内容管理系统. 保留所有权利</p>
                    <p className="mt-1">技术支持微信: {wechat}</p>
                </div>
            </div>

            {/* 双因素认证模态框 */}
            <Modal
                title="双因素认证"
                open={show2FAModal}
                onCancel={() => setShow2FAModal(false)}
                footer={[
                    <Button key="cancel" onClick={() => setShow2FAModal(false)}>
                        取消
                    </Button>,
                    <Button
                        key="submit"
                        type="primary"
                        loading={verifying2FA}
                        onClick={verify2FA}
                    >
                        验证
                    </Button>
                ]}
            >
                <div className="space-y-4">
                    <p>验证码已发送至您的邮箱: <strong>{emailMasked}</strong></p>
                    <p className="text-sm text-gray-500">请查收邮件并输入6位验证码</p>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            验证码
                        </label>
                        <Input
                            placeholder="请输入6位验证码"
                            value={twoFactorCode}
                            onChange={(e) => setTwoFactorCode(e.target.value)}
                            maxLength={6}
                            style={{ width: '100%' }}
                        />
                    </div>
                </div>
            </Modal>
        </div>
    );
};

export default LoginPage;
