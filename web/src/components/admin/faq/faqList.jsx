'use client';
import React, {useCallback, useEffect, useState} from 'react';
import {Button, Pagination, Popconfirm, Space, Spin, Table, App} from 'antd';
import { message } from 'antd';
import {useDispatch, useSelector} from "react-redux";
import axiosInstance from "@/utils/axios";
import FaqModal from "@/components/admin/faq/faqModal";

export default function FaqList() {
    const adminApp = useSelector((state) => state.adminSetting);
    const dispatch = useDispatch();
    const [dataList, setDataList] = useState([]);
    const [loading, setLoading] = useState(false);
    const [selectedRowKeys, setSelectedRowKeys] = useState([]);
    const [searchValue, setSearchValue] = useState('');
    const { message } = App.useApp();

    // 分页变量
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [total, setTotal] = useState(0);

    const columns = [
        {
            title: 'FAQ问题',
            dataIndex: 'question',
            key: 'question',
            width: '400px',
            textWrap: 'word-break',
        },
        {
            title: 'FAQ答案',
            dataIndex: 'reply',
            key: 'reply',
            width: '400px',
            textWrap: 'word-break',
        },
        {
            title: '创建时间',
            dataIndex: 'create_time',
            key: 'create_time',
        },
        {
            title: '操作',
            key: 'action',
            align: 'center',
            width: '180px',
            render: (_, item) => (
                <Space size="middle">
                    <a className="text-adminPrimaryColor" onClick={() => openModal(item)}>编辑</a>
                    <Popconfirm
                        title="确定删除？"
                        okText="确定"
                        cancelText="取消"
                        onConfirm={() => deleteRecord([item.id])}
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
            const {code,total, data} = await axiosInstance.get('/myapp/admin/faq/list',{params});
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
        }
    }

    useEffect(() => {
        fetchData(page, pageSize);
    }, [])


    const [modalIsOpen, setModalIsOpen] = useState(false);
    const [currentItem, setCurrentItem] = useState(null);

    const openModal = (item) => {
        setModalIsOpen(true);
        setCurrentItem(item)
    };

    const closeModal = (shouldRefresh) => {
        setModalIsOpen(false);
        setCurrentItem(null);
        if (shouldRefresh) {
            fetchData(page, pageSize);
        }
    };

    const deleteRecord = async (selected_ids) => {
        try {
            const {code, data} = await axiosInstance.post('/myapp/admin/faq/delete', {ids: selected_ids.join(',')});
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

    const onSelectChange = (newSelectedRowKeys) => {
        console.log('selectedRowKeys changed: ', newSelectedRowKeys);
        setSelectedRowKeys(newSelectedRowKeys);
    };

    const rowSelection = {
        selectedRowKeys,
        onChange: onSelectChange,
    };


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
                                <Button type="primary" onClick={() => openModal({sort: 0})}>新增</Button>
                                <Popconfirm
                                    title="确定删除？"
                                    okText="确定"
                                    cancelText="取消"
                                    onConfirm={() => deleteRecord(selectedRowKeys)}
                                >
                                    <Button disabled={!selectedRowKeys.length > 0 }>删除</Button>
                                </Popconfirm>
                            </div>
                            <Table columns={columns}
                                   dataSource={dataList}
                                   size="middle"
                                   rowSelection={rowSelection}
                                   rowKey={(record) => record.id}
                                   pagination={false}
                                   scroll={{ x: 'max-content' }}
                                   showSizeChanger={false}
                            />

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


            <FaqModal
                isOpen={modalIsOpen}
                onRequestClose={closeModal}
                initialItem={currentItem}
            />

        </>
    );
};