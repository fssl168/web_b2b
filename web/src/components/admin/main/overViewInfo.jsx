'use client';
import React, {useCallback, useEffect, useState} from 'react';
import {Button, message, Pagination, Popconfirm, Space, Spin, Table} from 'antd';
import {useDispatch, useSelector} from "react-redux";
import axiosInstance from "@/utils/axios";
import Image from 'next/image';

export default function OverViewInfo() {

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            const {code, data} = await axiosInstance.get('/myapp/admin/overview/dataCount');
            if (code === 0) {
                setData(data)
            } else {
                message.error("数据获取失败")
            }
        } catch (err) {
            console.log(err)
        }
    }


    const [data, setData] = useState({});

    const cardStyle = "rounded-lg bg-gradient-to-b from-[#e1e5f5] to-[#e1e5f5]  h-[100px] p-4 flex-1 flex flex-col gap-3";
    const labelStyle = "text-[#001e30] text-[14px] font-light";
    const valueStyle = "text-adminPrimaryColor text-2xl font-light ";

    return (
        <>

            <div className="bg-white px-4 py-4 flex flex-col gap-4">
                <h2 className="flex flex-row">
                    <Image
                        src="/admin/icon_data.svg"
                        alt="数据统计"
                        width={20}
                        height={20}
                    />
                    <span className="ml-1 text-gray-500">数据统计</span>
                </h2>
                <div className=" flex flex-row gap-4">
                    <div
                        className={cardStyle}>
                        <div className={labelStyle}>今日询盘</div>
                        <div className={valueStyle}>{data.inquiry_count || '0'}</div>
                    </div>
                    <div
                        className={cardStyle}>
                        <div className={labelStyle}>今日访客</div>
                        <div className={valueStyle}>{data.visit_count || '0'}</div>
                    </div>
                    <div
                        className={cardStyle}>
                        <div className={labelStyle}>产品数</div>
                        <div className={valueStyle}>{data.product_count || '0'}</div>
                    </div>
                    <div
                        className={cardStyle}>
                        <div className={labelStyle}>新闻数</div>
                        <div className={valueStyle}>{data.news_count || '0'}</div>
                    </div>
                    <div
                        className={cardStyle}>
                        <div className={labelStyle}>案例数</div>
                        <div className={valueStyle}>{data.case_count || '0'}</div>
                    </div>
                </div>
            </div>


        </>
    );
};