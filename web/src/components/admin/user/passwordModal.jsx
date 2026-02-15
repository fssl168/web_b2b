'use client';
import React, {useEffect, useState} from "react";
import {Button, Divider, Input, InputNumber, message, Modal, Select, Spin, App} from "antd";
import FormLabel from "@/components/admin/formLabel";
import axiosInstance from "@/utils/axios";
import TextArea from "antd/es/input/TextArea";


const PasswordModal = ({isOpen, onRequestClose, initialItem}) => {
    const { message: antdMessage } = App.useApp();
    const [currentItem, setCurrentItem] = useState(initialItem || {});
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        setCurrentItem(initialItem || {});

        // 密码清空
        setCurrentItem((prev) => ({...prev, password: ''}));
    }, [initialItem]);


    const handleInputChange = (name, value) => {
        setCurrentItem((prev) => ({...prev, [name]: value}));
    };

    const handleSelectChange = (name, value) => {
        console.log('value----', value)
        setCurrentItem((prev) => ({...prev, [name]: value}));
    };

    const handleSave = async () => {
        try {
            const post_url = '/myapp/admin/user/updatePwd';
            const formData = new FormData();
            if (currentItem.id) {
                formData.append('id', currentItem.id);
            }
            if (!currentItem.password) {
                antdMessage.error('不能为空')
                return;
            }
            if (!currentItem.newPassword1) {
                antdMessage.error('不能为空')
                return;
            }
            if (!currentItem.newPassword2) {
                antdMessage.error('不能为空')
                return;
            }
            formData.append('password', currentItem.password || '');
            formData.append('newPassword1', currentItem.newPassword1 || '');
            formData.append('newPassword2', currentItem.newPassword2 || '');
            setLoading(true);
            const {code, msg, data} = await axiosInstance.post(post_url, formData);
            if (code === 0) {
                antdMessage.success("操作成功")
                onRequestClose(true);
            } else {
                antdMessage.error(msg || '网络异常')
            }
            setLoading(false);
        } catch (err) {
            console.log(err)
            setLoading(false)
        }
    };

    console.log('current-----------', currentItem)


    return (
        <Modal
            title={'修改密码'}
            centered
            open={isOpen}
            onCancel={() => onRequestClose(false)}
            footer={null}
            width={600}
        >

            <Spin spinning={loading} tip="">
                <div className="flex flex-col">
                    <div className="">
                        <div className="">
                            <div className="flex flex-col gap-4 pt-4 pb-0">
                                <div className="flex flex-row gap-4">
                                    <FormLabel title="用户名" required={true}></FormLabel>
                                    <Input placeholder="请输入" value={currentItem.username}
                                           disabled
                                           onChange={(e) => handleInputChange("username", e.target.value)}
                                           style={{width: 400}}/>
                                </div>
                                <div className="flex flex-row gap-4">
                                    <FormLabel title="原密码" required={true}></FormLabel>
                                    <Input.Password placeholder="请输入" value={currentItem.password}
                                                    onChange={(e) => handleInputChange("password", e.target.value)}
                                                    style={{width: 400}}/>
                                </div>
                                <div className="flex flex-row gap-4">
                                    <FormLabel title="新密码" required={true}></FormLabel>
                                    <Input.Password placeholder="请输入" value={currentItem.newPassword1}
                                                    onChange={(e) => handleInputChange("newPassword1", e.target.value)}
                                                    style={{width: 400}}/>
                                </div>
                                <div className="flex flex-row gap-4">
                                    <FormLabel title="确认密码" required={true}></FormLabel>
                                    <Input.Password placeholder="请输入" value={currentItem.newPassword2}
                                                    onChange={(e) => handleInputChange("newPassword2", e.target.value)}
                                                    style={{width: 400}}/>
                                </div>

                            </div>

                            <Divider/>


                            <div className="flex flex-row gap-4 justify-start">
                                <Button type="primary" onClick={handleSave}>提交</Button>
                                <Button onClick={() => onRequestClose(false)}>取消</Button>
                            </div>
                        </div>
                    </div>
                </div>
            </Spin>
        </Modal>

    );
};

export default PasswordModal;