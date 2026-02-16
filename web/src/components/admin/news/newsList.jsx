'use client';
import React, {useEffect, useState} from 'react';
import {Button, ConfigProvider, Modal, Pagination, Popconfirm, Space, Spin, Table, Tabs, Tag, App} from 'antd';
import {useDispatch, useSelector} from "react-redux";
import Search from "antd/es/input/Search";
import axios from "axios";
import axiosInstance from "@/utils/axios";
import NewsModal from "@/components/admin/news/newsModal";

export default function NewsList() {
    const { message } = App.useApp();
    const adminApp = useSelector((state) => state.adminSetting);
    const dispatch = useDispatch();
    const [dataList, setDataList] = useState([]);
    const [loading, setLoading] = useState(false);
    const [selectedRowKeys, setSelectedRowKeys] = useState([]);
    const [searchValue, setSearchValue] = useState('');

    // 分页变量
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [total, setTotal] = useState(0);

    const columns = [
        {
            title: '标题',
            dataIndex: 'title',
            key: 'title',
            width: '320px',
            textWrap: 'word-break',
        },
        {
            title: '来源',
            dataIndex: 'source',
            key: 'source',
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
                keyword: searchValue
            };
            const {code, total, data} = await axiosInstance.get('/myapp/admin/news/list', {params});
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
    }, [page, searchValue])


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
            const {code, data} = await axiosInstance.post('/myapp/admin/news/delete', {ids: selected_ids.join(',')});
            if (code === 0) {
                message.success("删除成功")
                if (selected_ids.length === dataList.length && page > 1) {
                    setPage(page - 1);
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

    const onSearch = (value, _e, info) => {
        console.log(info?.source, value);
        setPage(1)
        setSearchValue(value || '')
    }

    const handleChangePage = (page, pageSize) => {
        setPage(page);
        setPageSize(pageSize);
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
                                    <Button disabled={!selectedRowKeys.length > 0}>删除</Button>
                                </Popconfirm>
                                <Search
                                    placeholder="搜索"
                                    allowClear
                                    onSearch={onSearch}
                                    style={{
                                        width: 200,
                                        marginLeft: 'auto',
                                    }}
                                />
                            </div>
                            <Table columns={columns}
                                   dataSource={dataList}
                                   size="middle"
                                   rowSelection={rowSelection}
                                   rowKey={(record) => record.id}
                                   pagination={false}
                                   scroll={{x: 'max-content'}}
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


            <NewsModal
                isOpen={modalIsOpen}
                onRequestClose={closeModal}
                initialItem={currentItem}
            />

        </>
    );
};