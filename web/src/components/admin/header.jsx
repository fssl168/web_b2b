'use client';
import "@/styles/globals.css";
import {DownOutlined} from "@ant-design/icons";
import {useDispatch, useSelector} from "react-redux";
import {setCollapsed} from "@/redux/adminSettingSlice";
import React, {useEffect, useState} from "react";
import Image from "next/image";
import {Dropdown} from "antd";
import {useRouter} from "next/navigation";
import Link from "next/link";
import { getCookie } from "@/utils/axios";

const Header = () => {
    const router = useRouter();

    const adminApp = useSelector((state) => state.adminSetting);
    const dispatch = useDispatch();

    const [username, setUsername] = useState('-');
    const [role, setRole] = useState('');

    useEffect(() => {
        if (typeof window !== 'undefined') {
            let username = getCookie('username') || '';
            setUsername(username);
            let userRole = getCookie('role') || '';
            setRole(userRole);
        }
    }, []);

    const toggleSideBar = () => {
        let collapsed = adminApp.collapsed;
        dispatch(setCollapsed(!collapsed));
    }

    const logout = () => {
        localStorage.removeItem('admintoken');
        localStorage.removeItem('username');
        router.push("/adminLogin")
    }

    const goHome = () => {
    }

    const items = [
        {
            key: '1',
            label: (
                <a>
                    退出
                </a>
            ),
        },
    ];

    const handleMenuClick = (e) => {
        if (e.key === '1') {
            logout();
        }
    };

    return (
        <>
            <div className="h-14 px-4 flex flex-row items-center bg-white border-b border-b-gray-300 ">
                <Image
                    src="/admin/menu.png"
                    alt="menu"
                    width={26}
                    height={26}
                    className="cursor-pointer"
                    onClick={toggleSideBar}
                />
                <div className="flex flex-row gap-2 items-center justify-center ml-auto pr-4">
                    <Link className="flex flex-row gap-1 mr-4 cursor-pointer"
                          href="/"
                          target="_blank"
                    >
                        <Image
                            src="/admin/icon_home.svg"
                            alt="home"
                            width={20}
                            height={20}
                            className="cursor-pointer"
                        />
                        <div className="text-[14px] text-gray-900">网站首页</div>
                    </Link>
                    <div className="flex flex-col items-end">
                            <div className={"ml-2 leading-[14px] text-gray-700 text-[12px]"}>{username}</div>
                            <div className={"ml-2 leading-[14px] text-gray-400 text-[11px]"}>{role === '3' ? '演示账号' : '超级管理员'}</div>
                        </div>

                    <Dropdown
                        menu={{
                            items,
                            onClick: handleMenuClick,
                        }}
                    >
                        <div size="4" className="cursor-pointer flex flex-row gap-1">
                            <Image
                                src="/admin/icon_avatar.svg"
                                alt="avatar"
                                width={38}
                                height={38}
                            />
                            <DownOutlined style={{ fontSize: '10px', color: '#aaa' }}/>
                        </div>
                    </Dropdown>

                </div>
            </div>
        </>
    )


};

export default Header;
