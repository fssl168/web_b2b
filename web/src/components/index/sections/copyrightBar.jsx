'use client';

import { useState, useEffect } from 'react';

export default function CopyrightBar({siteName='', classStyle=''}) {
    const [year, setYear] = useState('');
    
    useEffect(() => {
        // 只在客户端计算年份，避免hydration mismatch
        setYear(new Date().getFullYear().toString());
    }, []);
    
    return (
        <div className={classStyle}>
            Copyright © {year} • &nbsp;
            <a href="/" className="hover:text-mainColorNormal transition-colors">
                {siteName}
            </a>
            &nbsp;•&nbsp;
            Powered by
            &nbsp;
            <a target="_black" href="https://fktool.com/" className="hover:text-mainColorNormal transition-colors">
                FK
            </a>
        </div>
    )
}