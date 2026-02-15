/** @type {import('next').NextConfig} */

const nextConfig = {
    basePath: '', // 设置统一前缀如/en
    assetPrefix: '', // 静态资源前缀
    reactStrictMode: false,
    env: {
        NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME: "da9h8exvs",
        NEXT_PUBLIC_CLOUDINARY_PRESET_NAME: "fi0lxkc1",
    },
    images: {
        remotePatterns: [
            {
                protocol: 'http',
                hostname: process.env.NEXT_PUBLIC_HOST || 'localhost',
                port: '',
                pathname: '/**',
            },
            {
                protocol: 'http',
                hostname: 'localhost',
                port: '8000',
                pathname: '/**',
            },
            {
                protocol: 'https',
                hostname: 'localhost',
                port: '',
                pathname: '/**',
            },
        ],
        unoptimized: true, // 禁用图片优化，避免私有IP限制
    },
    compiler: {
        removeConsole: process.env.NODE_ENV === 'production',
    },
    headers: async () => [
        {
            source: '/:path*',
            headers: [
                {
                    key: 'X-DNS-Prefetch-Control',
                    value: 'on'
                },
                {
                    key: 'Strict-Transport-Security',
                    value: 'max-age=63072000; includeSubDomains; preload'
                },
                {
                    key: 'X-XSS-Protection',
                    value: '1; mode=block'
                },
                {
                    key: 'X-Frame-Options',
                    value: 'SAMEORIGIN'
                },
                {
                    key: 'X-Content-Type-Options',
                    value: 'nosniff'
                }
            ]
        }
    ],
    poweredByHeader: false,
    compress: true,
};

export default nextConfig;
