'use client';

import { useState, useEffect } from 'react';

const CopyrightYear = ({ siteName }) => {
    const [year, setYear] = useState('');
    
    useEffect(() => {
        // 只在客户端计算年份，避免hydration mismatch
        setYear(new Date().getFullYear().toString());
    }, []);
    
    return (
        <span>
            &copy; {year} {siteName || "Company Website"} | Technical Support
        </span>
    );
};

export default CopyrightYear;