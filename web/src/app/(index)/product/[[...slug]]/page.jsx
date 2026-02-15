import api from "@/utils/axiosApi";
import {getIp} from "@/utils/tools";

// 定义获取数据的函数
async function getSectionData(params) {
    try {
        // 调用API获取实际数据
        console.log('发送API请求，参数:', params);
        const response = await api.get('/myapp/index/thing/section', {
            params: params
        });
        
        // 检查响应数据结构
        console.log('收到API响应:', response);
        // 注意：axiosApi.js中的响应拦截器已经将响应处理为response.data
        // 所以后端返回的整个对象应该直接是{code, msg, total, data}的结构
        
        // 检查响应是否成功
        if (response.code !== 0) {
            console.error('API请求失败:', response.msg);
            throw new Error(response.msg || 'API请求失败');
        }
        
        // 提取实际数据
        const actualData = response.data || {};
        
        // 返回实际数据，如果数据不完整则使用默认值
        return {
            bannerData: actualData.bannerData || {},
            categoryData: actualData.categoryData || [
                {"id": "1", "title": "产品分类1"},
                {"id": "2", "title": "产品分类2"},
                {"id": "3", "title": "产品分类3"}
            ],
            productData: actualData.productData || [],
            featuredData: actualData.featuredData || [],
            total: response.total || actualData.total || 0,
            seoData: actualData.seoData || {
                seo_title: "Products",
                seo_description: "Products",
                seo_keywords: "Products"
            },
            siteName: actualData.siteName || "示例网站"
        };
    } catch (err) {
        console.error('获取产品数据失败:', err);
        return {
            bannerData: {},
            categoryData: [
                {"id": "1", "title": "产品分类1"},
                {"id": "2", "title": "产品分类2"},
                {"id": "3", "title": "产品分类3"}
            ],
            productData: [],
            featuredData: [],
            total: 0,
            seoData: {
                seo_title: "Products",
                seo_description: "Products",
                seo_keywords: "Products"
            },
            siteName: "示例网站"
        };
    }
}

export default async function Page({params, searchParams}) {
    // 解析slug参数 - params是一个Promise，需要使用await解包
    const resolvedParams = await params;
    const slug = resolvedParams?.slug || [];

    // 解析category和page
    let categoryId = null;
    let pageNumber = 1;
    let pageSize = 9;

    const id = process.env.NEXT_PUBLIC_TEMPLATE_ID;

    // 兼容模板
    if (['004', '005', '006', '007', '008', '009', '010'].includes(id)) {
        pageSize = 12;
    }

    // 解析不同的路由模式
    if (slug.length > 0) {
        if (slug[0] === 'category' && slug.length >= 2) {
            // 处理 /product/category/[id] 和 /product/category/[id]/page/[number]
            categoryId = slug[1];

            // 检查是否还有页码
            if (slug.length >= 4 && slug[2] === 'page') {
                pageNumber = parseInt(slug[3], 10) || 1;
            }
        } else if (slug[0] === 'page' && slug.length >= 2) {
            // 处理 /product/page/[number]
            pageNumber = parseInt(slug[1], 10) || 1;
        }
    }

    // 获取搜索参数
    const resolvedSearchParams = await searchParams;
    const searchQuery = resolvedSearchParams?.s || '';

    // 打印调试信息
    console.log('获取产品数据，参数:', {page: pageNumber, pageSize: pageSize, categoryId, searchQuery});

    const urlParams = {page: pageNumber, pageSize: pageSize, categoryId, searchQuery}
    const {bannerData, categoryData, productData, featuredData, total} = await getSectionData(urlParams)

    // 获取模板id
    const templateId = process.env.NEXT_PUBLIC_TEMPLATE_ID;

    // 准备传递给模板的props
    const templateProps = {
        bannerData,
        categoryId,
        pageNumber,
        total,
        pageSize,
        categoryData,
        productData,
        featuredData,
        searchQuery
    };

    // 动态导入对应模板
    const ProductTemplateModule = await import(`@/templates/${templateId}/productTemplate`);
    const ProductTemplate = ProductTemplateModule.default;
    
    return <ProductTemplate {...templateProps} />;
}

export async function generateMetadata({params}) {
    // 使用函数获取案例详情数据
    const data = await getSectionData({page: 1, pageSize: 9});

    // 从详情数据中提取信息
    const {seo_title, seo_description, seo_keywords} = data.seoData;
    const siteName = data.siteName;

    // 返回动态生成的metadata
    return {
        title: seo_title || 'Products',
        description: seo_description || 'Products',
        keywords: seo_keywords || 'Products',
        // Open Graph
        openGraph: {
            title: seo_title || 'Products',
            description: seo_description || 'Products',
            url: process.env.NEXT_PUBLIC_BASE_URL,
            siteName: siteName,
            image: '',
            type: 'website',
        },
        // Twitter
        twitter: {
            card: 'summary',
            title: seo_title || siteName || 'Products',
            description: seo_description || siteName || 'Products',
            image: '',
        },
        robots: {
            index: true,
            follow: true,
        },
    };
}