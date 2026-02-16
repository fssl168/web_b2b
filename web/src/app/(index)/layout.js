

import {Roboto, Open_Sans, Lato, Nunito, Merriweather, Montserrat } from 'next/font/google';
import "@/styles/globals.css";
import api from "@/utils/axiosApi";
import ThemeScript from '@/components/index/sections/ThemeScript';
import CopyrightYear from '@/components/index/CopyrightYear';

export const revalidate = 0

// 预加载所有字体
const lato = Lato({ subsets: ["latin"], weight: ['400','700'] });
const openSans = Open_Sans({ subsets: ["latin"], weight: ['500', '600', '700'] });

// 定义不同模板的字体配置
const fontConfigs = {
    '001': lato,
    '002': lato,
    '003': lato,
    '004': lato,
    '005': openSans,
    '006': openSans,
    '007': openSans,
    '008': openSans,
    '009': openSans,
    '010': openSans,
    '011': openSans,
};

// 获取当前模板的字体
const getTemplateFont = () => {
    const templateId = process.env.NEXT_PUBLIC_TEMPLATE_ID || '001';
    return fontConfigs[templateId] || lato; // 默认使用 Lato
};

export const metadata = {
    icons: [{rel: "icon", url: "/favicon.ico"}],
}

// 生成内联样式，确保主题变量优先设置
const getInitialThemeStyles = () => {
    const templateId = process.env.NEXT_PUBLIC_TEMPLATE_ID || '001';
    return `
        :root {
            --main-color-light: var(--main-color-light-${templateId});
            --main-color-normal: var(--main-color-normal-${templateId});
            --main-color-deep: var(--main-color-deep-${templateId});
        }
    `;
};

export default async function RootLayout({children}) {
    const {navSectionData, footerSectionData} = await getSectionData();
    
    // 获取模板id
    const templateId = process.env.NEXT_PUBLIC_TEMPLATE_ID;
    
    // 获取当前模板的字体
    const font = getTemplateFont();
    
    // 检查网站状态
    const isWebsiteDown = navSectionData?.basicSite?.status === "2";
    
    // 如果网站状态为关闭
    if (isWebsiteDown) {
        return (
            <html lang="en" suppressHydrationWarning>
                <head>
                    <title>Website Under Maintenance</title>
                    {/* 内联样式优先设置主题变量 */}
                    <style dangerouslySetInnerHTML={{ __html: getInitialThemeStyles() }} />
                    {/* 优先加载主题脚本 */}
                    <ThemeScript />
                </head>
                <body className={`${font.className} bg-gray-50 overflow-x-hidden flex items-center justify-center min-h-screen`}>
                    <div className="max-w-md w-full mx-auto bg-white rounded-md shadow-lg p-8 text-center">
                        {navSectionData?.basicSite?.site_logo && (
                            <div className="flex justify-center mb-6">
                                <img 
                                    src={`${process.env.NEXT_PUBLIC_BASE_URL}/upload/img/${navSectionData.basicSite.site_logo}`} 
                                    alt="Website Logo" 
                                    className="h-16 w-auto" 
                                />
                            </div>
                        )}
                        
                        <h1 className="text-2xl font-bold text-gray-800 mb-4">Website Under Maintenance</h1>
                        <p className="text-gray-600 mb-6">
                            {navSectionData?.basicSite?.closeMessage || "We are currently performing scheduled maintenance. Please check back later."}
                        </p>
                        
                        <div className="mt-8 text-gray-500 text-sm">
                            <CopyrightYear siteName={navSectionData?.basicSite?.site_name} />
                        </div>
                    </div>
                </body>
            </html>
        );
    }
    
    // 动态导入对应模板
    const IndexLayoutTemplateModule = await import(`@/templates/${templateId}/indexLayoutTemplate`);
    const IndexLayoutTemplate = IndexLayoutTemplateModule.default;
    
    return (
        <html lang="en" suppressHydrationWarning>
            <head>
                {/* 内联样式优先设置主题变量 */}
                <style dangerouslySetInnerHTML={{ __html: getInitialThemeStyles() }} />
                {/* 优先加载主题脚本 */}
                <ThemeScript />
            </head>
            <body className={`${font.className} bg-white overflow-x-hidden`}>
                <IndexLayoutTemplate 
                    navSectionData={navSectionData} 
                    footerSectionData={footerSectionData}
                >
                    {children}
                </IndexLayoutTemplate>
            </body>
        </html>
    );
}

// 服务端获取数据
async function getSectionData() {
    try {
        // 调用API获取实际数据
        const data = await api.getSectionData();
        return data;
    } catch (err) {
        // 如果出错，返回默认值
        return {
            "navSectionData": {
                "basicSite": {
                    "site_gaid": "",
                    "site_logo": ""
                },
                "basicGlobal": {
                    "global_facebook": "",
                    "global_twitter": "",
                    "global_instagram": "",
                    "global_linkedin": "",
                    "global_youtube": "",
                    "global_whatsapp": ""
                },
                "navigationItems": [
                    {
                        "type": "link",
                        "name": "首页",
                        "href": "/"
                    },
                    {
                        "type": "link",
                        "name": "关于我们",
                        "href": "/about"
                    },
                    {
                        "type": "dropdown",
                        "name": "产品中心",
                        "href": "/product",
                        "subItems": [
                            {
                                "name": "产品分类1",
                                "href": "/product/category1"
                            },
                            {
                                "name": "产品分类2",
                                "href": "/product/category2"
                            },
                            {
                                "name": "产品分类3",
                                "href": "/product/category3"
                            }
                        ]
                    },
                    {
                        "type": "link",
                        "name": "新闻资讯",
                        "href": "/news"
                    },
                    {
                        "type": "link",
                        "name": "案例展示",
                        "href": "/case"
                    },
                    {
                        "type": "link",
                        "name": "常见问题",
                        "href": "/faq"
                    },
                    {
                        "type": "link",
                        "name": "下载中心",
                        "href": "/download"
                    },
                    {
                        "type": "link",
                        "name": "联系我们",
                        "href": "/contact"
                    }
                ]
            }, 
            "footerSectionData": {
                "navData": [
                    {
                        "type": "link",
                        "name": "首页",
                        "href": "/"
                    },
                    {
                        "type": "link",
                        "name": "关于我们",
                        "href": "/about"
                    },
                    {
                        "type": "link",
                        "name": "产品中心",
                        "href": "/product"
                    },
                    {
                        "type": "link",
                        "name": "新闻资讯",
                        "href": "/news"
                    },
                    {
                        "type": "link",
                        "name": "案例展示",
                        "href": "/case"
                    },
                    {
                        "type": "link",
                        "name": "常见问题",
                        "href": "/faq"
                    },
                    {
                        "type": "link",
                        "name": "下载中心",
                        "href": "/download"
                    },
                    {
                        "type": "link",
                        "name": "联系我们",
                        "href": "/contact"
                    }
                ],
                "categoryData": [
                    {
                        "id": "1",
                        "title": "产品分类1"
                    },
                    {
                        "id": "2",
                        "title": "产品分类2"
                    },
                    {
                        "id": "3",
                        "title": "产品分类3"
                    }
                ],
                "contactData": {
                    "global_email": "contact@example.com",
                    "global_phone": "1234567890",
                    "global_address": "北京市朝阳区",
                    "global_company_name": "示例公司"
                }
            }
        };
    }
}
