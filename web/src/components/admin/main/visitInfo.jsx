'use client';
import React, {useCallback, useEffect, useState} from 'react';
import {Button, message, Pagination, Popconfirm, Space, Spin, Table, Tag} from 'antd';
import {useDispatch, useSelector} from "react-redux";
import axiosInstance from "@/utils/axios";
import FaqModal from "@/components/admin/faq/faqModal";
import {ProfileOutlined} from "@ant-design/icons";
import {LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend} from 'recharts';
import {Flex, Radio} from 'antd';
import Image from "next/image";

export default function VisitInfo() {
    const adminApp = useSelector((state) => state.adminSetting);
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);

    const [data, setData] = useState([
        {day: '-', uv: 0, pv: 0},
    ]);

    useEffect(() => {
        fetchData(7)
    }, [])

    const fetchData = async (days) => {
        try {
            setLoading(true);
            const params = {days: days};
            const {code, data} = await axiosInstance.get('/myapp/admin/overview/count', {params: params});
            if (code === 0) {
                console.log('data', data)
                setData(data.visit_data);
            } else {
                message.error("数据获取失败")
            }
            setLoading(false);
        } catch (err) {
            console.log(err)
            setLoading(false);
        }
    }

    const handleRadioChange = (e) => {
        fetchData(e.target.value)
        console.log('radio checked', e.target.value);
    };


    const options = [
        {
            label: '最近7日',
            value: '7',
        },
        {
            label: '最近30日',
            value: '30',
        },
        {
            label: '最近90日',
            value: '90',
        },
    ];

    return (
        <>

            <div className="bg-white px-4 py-4 flex flex-col gap-4">
                <h2 className="flex flex-row items-center justify-center">
                    <Image
                        src="/admin/icon_visit.svg"
                        alt="访问统计"
                        width={20}
                        height={20}
                    />
                    <span className="ml-1 text-gray-500 ">访问统计</span>
                    <div className="ml-auto min-w-[290px]">
                        <Radio.Group
                            block
                            options={options}
                            defaultValue="7"
                            optionType="button"
                            buttonStyle="solid"
                            onChange={(e) => handleRadioChange(e)}
                        />
                    </div>
                </h2>
                <Spin spinning={loading} tip="">
                    <div className="w-full min-h-[200px]">
                        <ResponsiveContainer width='100%' aspect={4 / 1}>
                            <LineChart data={data} margin={{top: 15, right: 0, bottom: 15, left: 0}}>
                                <Line type="monotone" dataKey="uv" stroke="#82ca9d" animationDuration={500}/>
                                <Line type="monotone" dataKey="pv" stroke="#8884d8" animationDuration={500}/>
                                <CartesianGrid stroke="#ccc" strokeDasharray="5 5"/>
                                <XAxis dataKey="day" tick={{fontSize: "12px"}}/>
                                <YAxis tick={{fontSize: "12px"}}/>
                                <Tooltip tick={{fontSize: "12px"}}/>
                                <Legend wrapperStyle={{fontSize: "12px"}}/>
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </Spin>


            </div>


        </>
    );
};