// 'use client';
import "@/styles/globals.css";
import {AntdRegistry} from '@ant-design/nextjs-registry';
import {ConfigProvider, App} from "antd";
import ReduxProvider from "@/redux/redux-provider";


export const metadata = {
    title: "后台管理",
    description: "后台管理系统",
    icons: [{rel: "icon", url: "/admin/ico.png"}],
}


export default function RootLayout({children}) {

    const adminPrimaryColor = '#3399cc';


    return (
        <ReduxProvider>
            <html lang="en">
            <body>

            <AntdRegistry>
                <ConfigProvider
                    wave={{ disabled: true }}
                    theme={{
                        token: {
                            colorPrimary: adminPrimaryColor,
                        },
                        components: {
                            Menu: {
                                itemBorderRadius: 0,
                                itemMarginInline: 0,
                                itemPaddingInline: 60,
                                darkItemBg: adminPrimaryColor, // 整体背景色
                                darkSubMenuItemBg: adminPrimaryColor, // 子菜单背景色
                                darkItemColor: '#fff', // 文字颜色
                                darkItemSelectedBg: '#2e8ab8', // 选中颜色
                                motionDurationSlow: '0.1s', // 动效速度
                            },
                            Tabs: {
                                colorPrimaryBorder: '#fff',// 描边
                                horizontalMargin: '0 0 0 0',
                            },
                            Table: {
                                headerBorderRadius: 0,
                                headerBg: '#fafafa',
                                headerColor: '#555',
                                borderRadius: 0,
                                colorBorderSecondary: '#f1f1f1',
                                borderColor: '#eee',
                                cellFontSizeMD:13, // middle尺寸的
                                cellPaddingBlockMD: 12,
                                cellPaddingInlineMD: 8,
                            },
                            Pagination: {
                                borderRadius: 0,
                            },
                            Button: {
                                borderRadius: 0,
                            },
                            Input: {
                                borderRadius: 0
                            },
                            Select: {
                                borderRadius: 0
                            },
                        },
                    }}
                >
                    <App>
                        {children}
                    </App>
                </ConfigProvider>
            </AntdRegistry>

            </body>
            </html>
        </ReduxProvider>
    );
}
