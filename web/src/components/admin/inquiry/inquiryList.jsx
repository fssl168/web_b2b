'use client';
import React, {useEffect, useState} from 'react';
import {Button, Modal, Pagination, Popconfirm, Space, Spin, Table, App} from 'antd';
import {useDispatch, useSelector} from "react-redux";
import axiosInstance from "@/utils/axios";

export default function InquiryList() {
    const { message } = App.useApp();
    const adminApp = useSelector((state) => state.adminSetting);
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);
    const [dataList, setDataList] = useState([]);

    // 分页变量
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [total, setTotal] = useState(0);


    const columns = [
        {
            title: '客户姓名',
            dataIndex: 'name',
            key: 'name',
            width: '120px',
            textWrap: 'word-break',
            ellipsis: true,
        },
        {
            title: '客户电话',
            dataIndex: 'tel',
            key: 'tel',
            width: '120px',
            textWrap: 'word-break',
            ellipsis: true,
        },
        {
            title: 'Email',
            dataIndex: 'email',
            key: 'email',
            width: '150px',
            textWrap: 'word-break',
            ellipsis: true,
        },
        {
            title: '消息内容',
            dataIndex: 'message',
            key: 'message',
            width: '200px',
            textWrap: 'word-break',
        },
        {
            title: '所属IP',
            dataIndex: 'ip',
            key: 'ip',
            width: '120px',
            textWrap: 'word-break',
            ellipsis: true,
        },
        {
            title: '时间',
            dataIndex: 'create_time',
            key: 'create_time',
            width: '150px',
            textWrap: 'word-break',
            ellipsis: true,
        },
        {
            title: '操作',
            key: 'action',
            align: 'center',
            width: '120px',
            textWrap: 'word-break',
            ellipsis: true,
            render: (_, item) => (
                <Space size="middle">

                    <Popconfirm
                        title="确定删除？"
                        okText="确定"
                        cancelText="取消"
                        onConfirm={() => deleteRecord(item)}
                    >
                        <a className="text-adminPrimaryColor">删除</a>
                    </Popconfirm>
                </Space>
            ),
        },
    ];

    const fetchData = async (page, pageSize) => {
        try {
            setLoading(true);
            const params = {
                page: page,
                pageSize: pageSize,
            };
            const {code, total, data} = await axiosInstance.get('/myapp/admin/inquiry/list', {params});
            if (code === 0) {
                setDataList(data)
                setTotal(total)
                setPage(page);
                setPageSize(pageSize);
            } else {
                message.error("数据获取失败")
            }
            setLoading(false);
        } catch (err) {
            console.log(err)
            message.error("网络异常")
            setLoading(false);
        }
    }

    useEffect(() => {
        fetchData(page, pageSize);
    }, [])

    const deleteRecord = async (item) => {
        try {
            const {code, data} = await axiosInstance.post('/myapp/admin/inquiry/delete', {ids: item.id + ''});
            if (code === 0) {
                message.success("删除成功")
                if (dataList.length === 1 && page > 1) {
                    fetchData(page - 1, pageSize);
                } else {
                    fetchData(page, pageSize);
                }
            } else {
                message.error("删除失败")
            }
        } catch (err) {
            console.log(err)
        }
    }

    const handleChangePage = (page, pageSize) => {
        fetchData(page, pageSize);
    }

    return (
        <>

            <div className="bg-white">
                <div>
                    <Spin spinning={loading} tip="">
                        <div className=" px-4 py-4 flex flex-col gap-4">
                            <div className="flex flex-row gap-4">
                            </div>
                            <Table columns={columns}
                                   dataSource={dataList}
                                   size="middle"
                                   rowKey={(record) => record.id}
                                   pagination={false}
                                   className=""/>
                            <div className="p-4">
                                <Pagination align='end'
                                            current={page}
                                            pageSize={pageSize}
                                            total={total}
                                            showTotal={(total) => `共 ${total} 条`}
                                            onChange={handleChangePage}
                                />
                            </div>
                        </div>
                    </Spin>
                </div>
            </div>

        </>
    );
};