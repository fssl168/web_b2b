import axios from 'axios';

// 创建 axios 实例
const api = axios.create({
    // 在服务器端渲染时，使用 localhost 而不是 127.0.0.1
    baseURL: typeof window !== 'undefined' ? process.env.NEXT_PUBLIC_DJANGO_BASE_URL : 'http://localhost:8000',
    timeout: 15000, // 设置请求超时时间
    headers: {
        'Content-Type': 'application/json',
    },
    withCredentials: false, // 暂时禁用携带cookie
});

// 从cookie中获取token
function getCookie(name) {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith(`${name}=`))
        ?.split('=')[1];
    return cookieValue ? decodeURIComponent(cookieValue) : null;
}

// 请求拦截器
api.interceptors.request.use(
    (config) => {
        // 在发送请求之前添加 token 等信息
        if (typeof window !== 'undefined') {
            const token = getCookie('admintoken'); // 从cookie中获取token
            config.headers.ADMINTOKEN = token || '';
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 响应拦截器
api.interceptors.response.use(
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
                // 例如，重定向到登录页面
                if (typeof window !== 'undefined') {
                    let bp = process.env.NEXT_PUBLIC_BASE_PATH || ''
                    window.location.href = bp + '/adminLogin';
                }
            }
            // 处理其他响应错误
            return Promise.reject(response.data); // 返回错误信息
        }
        // 处理网络错误
        return Promise.reject({ code: 1, msg: '网络错误，请检查网络连接' });
    }
);


// API函数
const apiFunctions = {
    // 获取首页数据
    async getHomeData() {
        try {
            const response = await api.get('/myapp/index/home/section');
            return response.data || {};
        } catch (error) {
            console.error('获取首页数据失败:', error);
            return {};
        }
    },
    
    // 获取通用数据
    async getCommonData() {
        try {
            const response = await api.get('/myapp/index/common/section');
            return response.data || {};
        } catch (error) {
            console.error('获取通用数据失败:', error);
            return {};
        }
    },
    
    // 获取导航和页脚数据
    async getSectionData() {
        try {
            const response = await api.get('/myapp/index/common/section');
            const actualData = response.data || {};
            return {
                navSectionData: {
                    basicSite: actualData.basicSite || {
                        site_gaid: "",
                        site_logo: ""
                    },
                    basicGlobal: actualData.basicGlobal || {
                        global_facebook: "",
                        global_twitter: "",
                        global_instagram: "",
                        global_linkedin: "",
                        global_youtube: "",
                        global_whatsapp: ""
                    },
                    navigationItems: actualData.navigationItems || []
                },
                footerSectionData: {
                    navData: actualData.navData || [],
                    categoryData: actualData.categoryData || [],
                    contactData: actualData.contactData || {
                        global_email: "",
                        global_phone: "",
                        global_address: "",
                        global_company_name: ""
                    }
                }
            };
        } catch (error) {
            return {
                navSectionData: {
                    basicSite: {
                        site_gaid: "",
                        site_logo: ""
                    },
                    basicGlobal: {
                        global_facebook: "",
                        global_twitter: "",
                        global_instagram: "",
                        global_linkedin: "",
                        global_youtube: "",
                        global_whatsapp: ""
                    },
                    navigationItems: []
                },
                footerSectionData: {
                    navData: [],
                    categoryData: [],
                    contactData: {
                        global_email: "",
                        global_phone: "",
                        global_address: "",
                        global_company_name: ""
                    }
                }
            };
        }
    },
    
    // 导出axios实例
    axios: api
};

// 复制axios实例的方法到apiFunctions对象，确保与原始版本兼容
Object.assign(apiFunctions, api);

export default apiFunctions;