import {cache, Suspense} from 'react';
import api from "@/utils/axiosApi";
import {getIp} from "@/utils/tools";

// 使用React的缓存机制优化API调用
const getNewsDetailCached = cache(async (id) => {    // 这里应该是从API获取数据
    try {
        const params = {
            id: id,
        }
        const headers = {
            'Content-Type': 'application/json',
            'x-forwarded-for': getIp()
        };
        const {code, msg, data} = await api.get('/myapp/index/news/detail', {headers, params});
        if (code === 0) {
            return data;
        } else {
            console.error(`获取数据错误: ${msg}`);
            return null;
        }
    } catch (err) {
        console.error("获取数据失败:", err);
        return null;
    }
})

export async function generateMetadata({params}) {
    // 读取路由参数
    const {id} = await params;

    // 使用缓存的函数获取案例详情数据
    const data = await getNewsDetailCached(id);

    // 从详情数据中提取信息
    if (!data || !data.detailData) {
        return {
            title: 'News Not Found',
            description: 'The requested news article was not found.',
            keywords: 'news, not found',
            // Open Graph
            openGraph: {
                title: 'News Not Found',
                description: 'The requested news article was not found.',
                url: process.env.NEXT_PUBLIC_BASE_URL,
                siteName: 'B2B外贸演示站',
                image: '',
                type: 'website',
            },
            // Twitter
            twitter: {
                card: 'summary',
                title: 'News Not Found',
                description: 'The requested news article was not found.',
                image: '',
            },
            robots: {
                index: false,
                follow: false,
            },
        };
    }

    const {seo_title, seo_description, seo_keywords, title} = data.detailData;
    const siteName = data.siteName;

    // 返回动态生成的metadata
    return {
        title: seo_title || title,
        description: seo_description || title,
        keywords: seo_keywords || title,
        // Open Graph
        openGraph: {
            title: seo_title || title,
            description: seo_description || title,
            url: process.env.NEXT_PUBLIC_BASE_URL,
            siteName: siteName,
            image: '',
            type: 'website',
        },
        // Twitter
        twitter: {
            card: 'summary',
            title: seo_title || siteName || title,
            description: seo_description || siteName || title,
            image: '',
        },
        robots: {
            index: true,
            follow: true,
        },
    };
}


export default async function Page({params}) {
    const {id} = await params;
    const data = await getNewsDetailCached(id);

    // 获取模板id
    const templateId = process.env.NEXT_PUBLIC_TEMPLATE_ID;

    if (!data || !data.detailData) {
        return <div className="container mx-auto px-4 py-12">
            <h1 className="text-3xl font-bold text-center mb-6">News Not Found</h1>
            <p className="text-center text-gray-600">The requested news article was not found.</p>
        </div>;
    }

    const {detailData, categoryData, recommendData} = data;

    // 分享链接构建
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL;
    const articleUrl = `${baseUrl}/news/${id}`;
    const encodedUrl = encodeURIComponent(articleUrl);
    const encodedTitle = encodeURIComponent(detailData.title);
    const encodedSummary = encodeURIComponent(`Check out this article: ${detailData.title}`);

    // 社交媒体分享链接
    const shareLinks = {
        facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
        twitter: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`,
        linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`
    };

    // 准备传递给模板的props
    const templateProps = {
        detailData,
        categoryData,
        recommendData,
        shareLinks
    };

    // 动态导入对应模板
    const NewsDetailTemplateModule = await import(`@/templates/${templateId}/newsDetailTemplate`);
    const NewsDetailTemplate = NewsDetailTemplateModule.default;
    
    return <NewsDetailTemplate {...templateProps} />;
}