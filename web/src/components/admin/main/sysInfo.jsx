'use client';
import React, {useCallback, useEffect, useState} from 'react';
import {Button, message, Pagination, Popconfirm, Space, Spin, Table} from 'antd';
import {useDispatch, useSelector} from "react-redux";
import axiosInstance from "@/utils/axios";
import FaqModal from "@/components/admin/faq/faqModal";
import {ProfileOutlined} from "@ant-design/icons";
import Image from "next/image";

export default function SysInfo() {
    const adminApp = useSelector((state) => state.adminSetting);
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);
    const [selectedRowKeys, setSelectedRowKeys] = useState([]);
    const [searchValue, setSearchValue] = useState('');

    useEffect(() => {
        // fetchData()
    }, [])

    const fetchData = async () => {
        try {
            setLoading(true);
            const {code, data} = await axiosInstance.get('/myapp/admin/overview/sysInfo',);
            if (code === 0) {
                console.log('data',data)
            } else {
                message.error("数据获取失败")
            }
            setLoading(false);
        } catch (err) {
            console.log(err)
        }
    }

    const tdStyle = "border border-gray-200 bg-gray-50 pl-8 py-4 w-1/6";
    const tdStyleValue = "border border-gray-200 pl-8 py-3 w-2/6";

    const data = [
        { id: 1, name1: '系统名称：', name2: '外贸后台管理系统', name3: '系统版本：', name4: '1.0.2'},
        { id: 2, name1: '操作系统', name2: 'Linux', name3: '系统平台', name4: 'x86_64'},
        { id: 3, name1: 'Python版本', name2: '3.8', name3: '数据库', name4: 'MySQL57'},
        { id: 4, name1: '网站框架', name2: 'Javascript', name3: '系统语言', name4: 'CN'},
        { id: 5, name1: '负载均衡', name2: 'nginx', name3: '技术支持', name4: 'ByteSoft'},
    ];

    return (
        <>

            <div className="bg-white px-4 py-4 flex flex-col gap-4">
                <h2 className="flex flex-row">
                    <Image
                        src="/admin/icon_sys.svg"
                        alt="系统信息"
                        width={20}
                        height={20}
                    />
                    <span className="ml-1 text-gray-500">系统信息</span>
                </h2>
                <div className=" flex flex-row gap-4">

                    <table className="border border-gray-200 text-[12px] text-gray-600 w-full">

                        <tbody>
                        {data.map((item) => (
                            <tr key={item.id}>
                                <td  className={tdStyle}>{item.name1}</td>
                                <td  className={tdStyleValue}>{item.name2}</td>
                                <td  className={tdStyle}>{item.name3}</td>
                                <td  className={tdStyleValue}>{item.name4}</td>
                            </tr>
                        ))}
                        </tbody>

                    </table>
                </div>
            </div>


        </>
    );
};