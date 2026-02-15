'use client';
import React, {useEffect, useRef, useState} from 'react';
import {
    Button, Cascader,
    Divider,
    Input,
    Modal, Select, TreeSelect, App,
} from 'antd';
import LabelPanel from "@/components/admin/labelPanel";
import FormLabel from "@/components/admin/formLabel";
import axiosInstance from "@/utils/axios";
import ImageUpload from "@/components/admin/imageUpload";
import TextArea from "antd/es/input/TextArea";
import {Space} from "antd";
import dynamic from 'next/dynamic'
import PropertyPanel from "@/components/admin/product/propertyPanel";
import { Checkbox } from 'antd';
const CheckboxGroup = Checkbox.Group;

const WangEditor = dynamic(
    () => import('@/components/admin/wangEditor.jsx'),
    {ssr: false}
)

const ProductModal = ({isOpen, onRequestClose, initialItem}) => {
    const { message } = App.useApp();

    const [currentItem, setCurrentItem] = useState(initialItem || {})

    const [loading, setLoading] = useState(false);

    const divRef = React.useRef(null);

    const [categoryOptions, setCategoryOptions] = useState([]);

    // 为了制造Upload而用
    const [imageList, setImageList] = useState([]);

    const propertyRef = useRef(null);

    // 维度多选
    const plainOptions = [
        { label: '推荐', value: 'Recommend' },
        { label: '精选', value: 'Feature' },
    ];
    const [checkedList, setCheckedList] = useState([]);
    const handleCheckboxChanged = (name,value) => {
        setCheckedList(value);
        let valueText = value.join(",")
        setCurrentItem((prev) => ({...prev, [name]: valueText}));
    };

    const fetchCategoryData = async () => {
        try {
            const {code, msg, data} = await axiosInstance.get('/myapp/admin/category/list');
            if (code === 0) {
                setCategoryOptions(data);
            } else {
                message.error(msg || '网络异常')
            }
        } catch (err) {
            console.log(err)
        }
    };

    useEffect(() => {

        const handler = setTimeout(() => {

            // 制造适合Upload的数据格式
            if (initialItem?.cover?.length > 0) {
                setImageList(initialItem?.cover?.split("#").map((item) => ({
                    success: true,
                    name: item,
                    status: 'done',
                    url: process.env.NEXT_PUBLIC_BASE_URL + '/upload/img/' + item,
                })));
            } else {
                setImageList([]);
            }

            // 制造dimension的checkList
            if (initialItem?.dimension?.length > 0) {
                setCheckedList(initialItem?.dimension?.split(","));
            } else {
                setCheckedList([]);
            }

            // 初始化currentItem
            setCurrentItem(initialItem || {})
            if (divRef.current) {
                divRef.current.scrollTop = 0; // 滚动到 0
            }
            fetchCategoryData()
        }, 100); // 100ms延迟防抖

        // 清除实现防抖
        return () => {
            clearTimeout(handler);
        };
    }, [initialItem])

    const commit = () => {
        console.log("commit-->", currentItem);
        // todo 参数检查
        handleSave()
    }

    const handleSave = async () => {

        if (!currentItem.title) {
            message.error("请输入名称");
            return;
        }
        if (!currentItem.category) {
            message.error("请选择分类");
            return;
        }
        if (!currentItem.cover) {
            message.error("请上传图片");
            return;
        }

        if (!propertyRef.current.handleCheckSubmit()) {
            message.error("参数不能留空");
            return;
        }
        try {
            setLoading(true);
            const post_url = currentItem.id ? '/myapp/admin/thing/update' : '/myapp/admin/thing/create';
            const formData = new FormData();
            if (currentItem.id) {
                formData.append('id', currentItem.id);
            }
            formData.append('title', currentItem.title || '');
            formData.append('category', currentItem.category);
            formData.append('summary', currentItem.summary || '');
            formData.append('price', currentItem.price || '');
            formData.append('dimension', currentItem.dimension || '');
            formData.append('cover', currentItem.cover || '');
            formData.append('description', currentItem.description || '');
            formData.append('seo_title', currentItem.seo_title || '');
            formData.append('seo_description', currentItem.seo_description || '');
            formData.append('seo_keywords', currentItem.seo_keywords || '');
            formData.append('properties', currentItem.properties || '');
            formData.append('status', currentItem.status || '0');

            const {code, msg, data} = await axiosInstance.post(post_url, formData);
            if (code === 0) {
                message.success("操作成功")
                onRequestClose(true)
            } else {
                message.error(msg || '网络异常')
            }
            setLoading(false);
        } catch (err) {
            console.log(err)
            setLoading(false)
        }
    };


    // 更新子组件传来的值
    const handleInputChange = (name, value) => {
        setCurrentItem((prev) => ({...prev, [name]: value}));
    };

    const handleSelectChange = (name, value) => {
        console.log('value----', value)
        setCurrentItem((prev) => ({...prev, [name]: value}));
    };

    const handleTreeSelectChange = (name, value) => {
        setCurrentItem((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleImageUploadChange = (imageUrlList) => {
        let cover = (imageUrlList && imageUrlList.length > 0) ? imageUrlList.join("#") : null;
        setCurrentItem((prev) => ({...prev, cover: cover}));
    };

    const handleHtmlChange = (value) => {
        setCurrentItem((prev) => ({...prev, description: value}));
    };

    const handlePropertyChange = (value) => {
        setCurrentItem((prev) => ({...prev, properties: JSON.stringify(value || [])}));
    };

    const modalStyles = {
        mask: {
            backdropFilter: 'blur(10px)',
        },
    };

    console.log('currentItem----------->', currentItem)

    return (
        <Modal
            title={currentItem.id ? '编辑' : '新增'}
            centered
            open={isOpen}
            onCancel={() => onRequestClose(false)}
            footer={null}
            width={1100}
            styles={{
                mask: {
                    backdropFilter: 'blur(10px)',
                },
            }}
        >
            <div className="flex flex-col">
                <div>
                    <div ref={divRef} className="max-h-[75vh] overflow-y-auto">
                        <LabelPanel title="基本信息"></LabelPanel>
                        <div className="flex flex-col gap-6 px-2 py-2">
                            <div className="flex flex-row gap-4">
                                <FormLabel title="名称" required={true}></FormLabel>
                                <Input placeholder="请输入产品名称" value={currentItem.title}
                                       onChange={(e) => handleInputChange("title", e.target.value)}
                                       maxLength={100}
                                       style={{width: 300}}/>
                            </div>

                            <div className="flex flex-row gap-4">
                                <FormLabel title="分类" required={true}></FormLabel>
                                <TreeSelect
                                    styles={{ popup: { root: { maxHeight: 300, overflow: 'auto', minWidth: 300 } } }}
                                    style={{
                                        width: 300,
                                    }}
                                    placeholder="请选择"
                                    value={currentItem.category}
                                    placement='bottomLeft'
                                    allowClear
                                    fieldNames={{label: 'title', value: 'id', children: 'children'}}
                                    onChange={(value) => handleTreeSelectChange("category", value)}
                                    treeData={categoryOptions}
                                />
                            </div>
                            <div className="flex flex-row gap-4 items-center">
                                <FormLabel title="产品维度"></FormLabel>
                                <CheckboxGroup options={plainOptions} value={checkedList} onChange={(value)=>handleCheckboxChanged("dimension",value)} />
                            </div>
                            <div className="flex flex-row gap-4 items-center">
                                <FormLabel title="价格"></FormLabel>
                                <Input placeholder="选填" value={currentItem.price}
                                       onChange={(e) => handleInputChange("price", e.target.value)}
                                       style={{width: 300}}/>
                            </div>
                            <div className="flex flex-row gap-4">
                                <FormLabel title="摘要" required={true}></FormLabel>
                                <TextArea
                                    placeholder="请输入产品摘要"
                                    autoSize={{
                                        minRows: 3,
                                        maxRows: 6,
                                    }}
                                    showCount
                                    maxLength={500}
                                    value={currentItem.summary}
                                    onChange={(e) => handleInputChange("summary", e.target.value)}
                                    style={{width: 600}}
                                />
                            </div>
                            <div className="flex flex-row gap-4 min-h-[100px]">
                                <FormLabel title="图片" required={true}></FormLabel>
                                <ImageUpload maxCount={5}
                                             maxSize={5}
                                             accept="image/*"
                                             imageList={imageList}
                                             onImageUploadChange={handleImageUploadChange}/>
                            </div>
                            <div className="flex flex-row gap-4">
                                <FormLabel title="是否启用"></FormLabel>
                                <Select
                                    defaultValue="0"
                                    placeholder="请选择状态"
                                    value={currentItem.status}
                                    style={{ width: 400 }}
                                    onChange={(value)=>handleSelectChange('status', value)}
                                    options={[
                                        { value: '0', label: '是' },
                                        { value: '1', label: '否' },
                                    ]}
                                />
                            </div>
                        </div>
                        <Divider/>

                        <LabelPanel title="产品详情"></LabelPanel>
                        <div className="flex flex-col gap-4 px-2 py-2">
                            <WangEditor htmlText={currentItem.description} onHtmlResult={handleHtmlChange}/>
                        </div>

                        <Divider/>

                        <LabelPanel title="产品参数"></LabelPanel>
                        <div className="flex flex-col gap-4 px-2 py-2">
                            <PropertyPanel ref={propertyRef} properties={currentItem.properties}
                                           handlePropertyChange={handlePropertyChange}/>
                        </div>

                        <Divider/>

                        <LabelPanel title="SEO优化"></LabelPanel>
                        <div className="flex flex-col gap-4 px-2 py-2">
                            <div className="flex flex-row gap-4">
                                <FormLabel title="SEO标题"></FormLabel>
                                <Input placeholder="请输入SEO标题" value={currentItem.seo_title}
                                       onChange={(e) => handleInputChange("seo_title", e.target.value)}
                                       style={{width: 600}}/>
                            </div>
                            <div className="flex flex-row gap-4">
                                <FormLabel title="SEO关键词"></FormLabel>
                                <Input placeholder="请输入SEO关键词" value={currentItem.seo_keywords}
                                       onChange={(e) => handleInputChange("seo_keywords", e.target.value)}
                                       style={{width: 600}}/>
                            </div>
                            <div className="flex flex-row gap-4">
                                <FormLabel title="SEO描述"></FormLabel>
                                <TextArea
                                    placeholder="请输入SEO描述"
                                    autoSize={{
                                        minRows: 3,
                                        maxRows: 6,
                                    }}
                                    showCount
                                    maxLength={200}
                                    value={currentItem.seo_description}
                                    onChange={(e) => handleInputChange("seo_description", e.target.value)}
                                    style={{width: 600}}
                                />
                            </div>
                        </div>

                    </div>
                    <Divider/>

                    <div className="flex flex-row gap-4">
                        <Button loading={loading} type="primary" onClick={() => commit()}>提交</Button>
                        <Button onClick={() => onRequestClose(false)}>取消</Button>
                    </div>
                </div>

            </div>
        </Modal>
    );
};
export default ProductModal;