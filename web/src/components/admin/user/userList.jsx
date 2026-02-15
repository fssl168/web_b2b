'use client';
import React, {useEffect, useState} from 'react';
import {Button, ConfigProvider, message, Modal, Pagination, Popconfirm, Space, Spin, Table, Tabs, Tag} from 'antd';
import {useDispatch, useSelector} from "react-redux";
import Search from "antd/es/input/Search";
import axios from "axios";
import axiosInstance from "@/utils/axios";
import UserModal from "@/components/admin/user/userModal";
import PasswordModal from "@/components/admin/user/passwordModal";

export default function UserList() {
    const adminApp = useSelector((state) => state.adminSetting);
    const dispatch = useDispatch();
    const [loading, setLoading] = useState(false);


    const columns = [
        {
            title: 'ID',
            dataIndex: 'id',
            key: 'id',
            width: '90px',
            textWrap: 'word-break',
            ellipsis: true,
            render: (text) => <div>{text}</div>,
        },
        {
            title: '账号',
            dataIndex: 'username',
            key: 'username',
            width: '220px',
            textWrap: 'word-break',
            ellipsis: true,
        },
        {
            title: '邮箱',
            dataIndex: 'email',
            key: 'email',
            width: '220px',
            textWrap: 'word-break',
            ellipsis: true,
            render: (text) => <div>{text || '-'}</div>,
        },
        {
            title: '手机号',
            dataIndex: 'mobile',
            key: 'mobile',
            width: '150px',
            textWrap: 'word-break',
            ellipsis: true,
            render: (text) => <div>{text || '-'}</div>,
        },
        {
            title: '角色',
            dataIndex: 'role',
            key: 'role',
            render: (text) => <div>{text==='1'? '管理员':'演示账号'}</div>,
        },
        {
            title: '操作',
            key: 'action',
            fixed: 'right',
            align: 'center',
            width: '250px',
            textWrap: 'word-break',
            ellipsis: true,
            render: (_, item) => (
                <Space size="middle">
                    <a className="text-adminPrimaryColor" onClick={() => openModal(item)}>编辑</a>
                    <a className="text-adminPrimaryColor" onClick={() => openPasswordModal(item)}>修改密码</a>
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

    const fetchData = async () => {
        try {
            setLoading(true);
            const {code, data} = await axiosInstance.get('/myapp/admin/user/list');
            if (code === 0) {
                setData(data)
            } else {
                message.error("数据获取失败")
            }
            setLoading(false);
        } catch (err) {
            console.log(err)
        }
    }

    useEffect(() => {
        fetchData();
    }, [])


    const [data, setData] = useState([]);
    const [modalIsOpen, setModalIsOpen] = useState(false);
    const [passwordModalIsOpen, setPasswordModalIsOpen] = useState(false);
    const [currentItem, setCurrentItem] = useState(null);

    const openModal = (item) => {
        setModalIsOpen(true);
        setCurrentItem(item)
    };

    const closeModal = (shouldRefresh) => {
        setModalIsOpen(false);
        setCurrentItem(null);
        if (shouldRefresh) {
            fetchData();
        }
    };

    const openPasswordModal = (item) => {
        setPasswordModalIsOpen(true);
        setCurrentItem(item)
    };

    const closePasswordModal = (shouldRefresh) => {
        setPasswordModalIsOpen(false);
        setCurrentItem(null);
        if (shouldRefresh) {
            fetchData();
        }
    };

    const deleteRecord = async (item) => {
        try {
            const {code, msg, data} = await axiosInstance.post('/myapp/admin/user/delete', {id: item.id});
            if (code === 0) {
                message.success("删除成功")
                fetchData();
            } else {
                message.error(msg || "删除失败")
            }
        } catch (err) {
            console.log(err)
        }
    }

    return (
        <>

            <div className="bg-white">
                <div>
                    <Spin spinning={loading} tip="">
                        <div className="px-4 py-4 flex flex-col gap-4">
                            <div className="flex flex-row gap-4">
                                <Button type="primary" onClick={() => openModal({sort: 0})}>新增</Button>
                            </div>
                            <Table columns={columns}
                                   dataSource={data}
                                   size="middle"
                                   rowKey={(record) => record.id}
                                   pagination={false}
                            />
                        </div>
                    </Spin>
                </div>
            </div>


            <UserModal
                isOpen={modalIsOpen}
                onRequestClose={closeModal}
                initialItem={currentItem}
            />


            <PasswordModal
                isOpen={passwordModalIsOpen}
                onRequestClose={closePasswordModal}
                initialItem={currentItem}
            />
        </>
    );
};