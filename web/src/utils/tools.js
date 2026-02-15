import {headers} from "next/headers";


const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    const formatted = date.toLocaleDateString('en-US', options);
    return formatted;
}

const getIp = () => {
    try {
        const h = headers();
        // 检查h是否是Promise
        if (h instanceof Promise) {
            // 如果是Promise，返回默认值
            return 'unknown';
        }
        // 检查h是否有get方法
        if (typeof h.get === 'function') {
            const xff = h.get('x-forwarded-for');
            const realIp = h.get('x-real-ip');
            const clientIp = xff?.split(',')[0].trim() || realIp || 'unknown';
            return clientIp;
        } else {
            // 在客户端或headers()返回非预期对象时返回默认值
            return 'unknown';
        }
    } catch (error) {
        // 捕获任何错误，确保函数不会崩溃
        return 'unknown';
    }
}

export {formatDate, getIp}