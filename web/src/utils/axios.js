import axios from 'axios';

// 创建 axios 实例
const axiosInstance = axios.create({
    baseURL: process.env.NEXT_PUBLIC_BASE_URL,
    timeout: 15000, // 设置请求超时时间
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: false, // 暂时禁用携带cookie，避免跨域问题
});

// 从cookie中获取token
function getCookie(name) {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith(`${name}=`))
        ?.split('=')[1];
    return cookieValue ? decodeURIComponent(cookieValue) : null;
}

// 设置cookie
function setCookie(name, value, days = 1) {
    const expires = new Date(Date.now() + days * 86400000).toUTCString();
    document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; secure; SameSite=Strict`;
}

// 删除cookie
function deleteCookie(name) {
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

// 请求拦截器
axiosInstance.interceptors.request.use(
    (config) => {
        // 在发送请求之前添加 token 等信息
        if (typeof window !== 'undefined') {
            const token = getCookie('admintoken'); // 从cookie中获取token
            config.headers.admintoken = token || '';
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 响应拦截器
axiosInstance.interceptors.response.use(
    (response) => {
        // 可以在这里对响应数据进行处理
        return response.data; // 返回数据部分
    },
    (error) => {
        const { response } = error;
        if (response) {
            // 处理 401 错误
            if (response.status === 401 || response.status === 403) {
                // 可以在这里执行登出等操作
                console.error('未授权，请重新登录');
                deleteCookie('admintoken');
                deleteCookie('username');
                // 例如，重定向到登录页面
                let bp = process.env.NEXT_PUBLIC_BASE_PATH || ''
                window.location.href = bp + '/adminLogin';
            }
            // 处理其他响应错误
            return Promise.reject(response.data); // 返回错误信息
        }
        // 处理网络错误
        return Promise.reject(error);
    }
);

// 导出cookie操作函数
export { getCookie, setCookie, deleteCookie };
export default axiosInstance;