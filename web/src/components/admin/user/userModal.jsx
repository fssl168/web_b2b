'use client';
import React, {useEffect, useState} from "react";
import {Button, Divider, Input, InputNumber, message, Modal, Select, Spin, App} from "antd";
import FormLabel from "@/components/admin/formLabel";
import axiosInstance from "@/utils/axios";
import TextArea from "antd/es/input/TextArea";


const UserModal = ({isOpen, onRequestClose, initialItem}) => {
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
            const post_url = currentItem.id ? '/myapp/admin/user/update' : '/myapp/admin/user/create';
            const formData = new FormData();
            if (currentItem.id) {
                formData.append('id', currentItem.id);
            }
            if(!currentItem.username){
                antdMessage.error('用户名不能为空');
                return;
            }
            if(!currentItem.role){
                antdMessage.error('角色不能为空');
                return;
            }
            if(!currentItem.password && !currentItem.id){
                antdMessage.error('密码不能为空');
                return;
            }
            formData.append('username', currentItem.username || '');
            if (currentItem.password) {
                formData.append('password', currentItem.password);
            }
            formData.append('role', currentItem.role || '');
            formData.append('email', currentItem.email || '');
            formData.append('mobile', currentItem.mobile || '');
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
            title={'新增'}
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
                                           onChange={(e) => handleInputChange("username", e.target.value)}
                                           style={{width: 400}}/>
                                </div>
                                <div className="flex flex-row gap-4">
                                    <FormLabel title="密码" required={currentItem.id ? false : true}></FormLabel>
                                    <Input.Password placeholder={currentItem.id ? "留空表示不修改密码" : "请输入"} value={currentItem.password}
                                           onChange={(e) => handleInputChange("password", e.target.value)}
                                           style={{width: 400}}/>
                                </div>
                                <div className="flex flex-row gap-4">
                                    <FormLabel title="角色" required={true}></FormLabel>
                                    <Select
                                        placeholder="请选择角色"
                                        value={currentItem.role}
                                        style={{ width: 200 }}
                                        onChange={(value)=>handleSelectChange('role', value)}
                                        options={[
                                            { value: '1', label: '管理员' },
                                            { value: '3', label: '演示员' },
                                        ]}
                                    />
                                </div>
                                <div className="flex flex-row gap-4">
                                    <FormLabel title="邮箱" required={false}></FormLabel>
                                    <Input placeholder="请输入邮箱地址" value={currentItem.email}
                                           onChange={(e) => handleInputChange("email", e.target.value)}
                                           style={{width: 400}}/>
                                </div>
                                <div className="flex flex-row gap-4">
                                    <FormLabel title="手机号" required={false}></FormLabel>
                                    <Input placeholder="请输入手机号" value={currentItem.mobile}
                                           onChange={(e) => handleInputChange("mobile", e.target.value)}
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

export default UserModal;