import api from "@/utils/axiosApi";
import {cache} from 'react';
import {getIp} from "@/utils/tools";

// 使用React的缓存机制优化API调用
const getCaseDetailCached = cache(async (id) => {
    try {
        const params = {id};
        const headers = {
            'Content-Type': 'application/json',
            'x-forwarded-for': getIp()
        };
        const {code, msg, data} = await api.get('/myapp/index/case/detail', {headers, params});
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
});

// 动态生成metadata
export async function generateMetadata({params}) {
    // 读取路由参数 (params is a Promise in Next.js 13+)
    const resolvedParams = await params;
    const {id} = resolvedParams;

    // 使用缓存的函数获取案例详情数据
    const data = await getCaseDetailCached(id);

    // 检查数据是否存在
    if (!data || !data.detailData) {
        return {
            title: 'Case Detail',
            description: 'Case Detail',
            keywords: 'Case Detail',
        };
    }

    // 从详情数据中提取信息
    const {seo_title, seo_description, seo_keywords, title} = data.detailData;

    // 返回动态生成的metadata
    return {
        title: seo_title || title || 'Case Detail',
        description: seo_description || title || 'Case Detail',
        keywords: seo_keywords || title || 'Case Detail',
    };
}

export default async function Page({params}) {
    // 读取路由参数 (params is a Promise in Next.js 13+)
    const resolvedParams = await params;
    const {id} = resolvedParams;

    // 使用相同的缓存函数获取数据
    const data = await getCaseDetailCached(id);

    if (!data) {
        return <div>Case not found</div>;
    }

    // 获取模板id
    const templateId = process.env.NEXT_PUBLIC_TEMPLATE_ID;

    // 准备传递给模板的props
    const templateProps = {
        detailData: data.detailData,
        categoryData: data.categoryData,
        recommendData: data.recommendData
    };

    // 动态导入对应模板
    const CaseDetailTemplateModule = await import(`@/templates/${templateId}/caseDetailTemplate`);
    const CaseDetailTemplate = CaseDetailTemplateModule.default;
    
    return <CaseDetailTemplate {...templateProps} />;
}