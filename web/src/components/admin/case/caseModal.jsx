import React, {useEffect, useState} from "react";
import {Button, Divider, Input, InputNumber, message, Modal, Spin} from "antd";
import FormLabel from "@/components/admin/formLabel";
import ImageUpload from "@/components/admin/imageUpload";
import axiosInstance from "@/utils/axios";
import TextArea from "antd/es/input/TextArea";
import LabelPanel from "@/components/admin/labelPanel";
import dynamic from "next/dynamic";
const WangEditor = dynamic(
    () => import('@/components/admin/wangEditor.jsx'),
    {ssr: false}
)
const CaseModal = ({isOpen, onRequestClose, initialItem}) => {
    const [currentItem, setCurrentItem] = useState(initialItem || {});
    const [imageList, setImageList] = useState([]);
    const [loading, setLoading] = useState(false);
    const divRef = React.useRef(null);

    useEffect(() => {
        setCurrentItem(initialItem || {});

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

        if (divRef.current) {
            divRef.current.scrollTop = 0; // 滚动到 0
        }

    }, [initialItem]);


    const handleInputChange = (name, value) => {
        setCurrentItem((prev) => ({...prev, [name]: value}));
    };

    const handleImageUploadChange = (imageUrlList) => {
        let cover = (imageUrlList && imageUrlList.length > 0) ? imageUrlList.join("#") : null;
        setCurrentItem((prev) => ({...prev, cover: cover}));
    };

    const handleHtmlChange = (value) => {
        setCurrentItem((prev) => ({...prev, description: value}));
    };

    const handleSave = async () => {
        try {
            const post_url = currentItem.id ? '/myapp/admin/case/update' : '/myapp/admin/case/create';
            const formData = new FormData();
            if (currentItem.id) {
                formData.append('id', currentItem.id);
            }
            if(!currentItem.title){
                message.error('标题不能为空')
                return;
            }
            if (!currentItem.cover) {
                message.error('封面不能为空')
                return;
            }
            formData.append('title', currentItem.title || '');
            formData.append('client', currentItem.client || '');
            formData.append('cover', currentItem.cover || '');
            formData.append('description', currentItem.description || '');
            formData.append('seo_title', currentItem.seo_title || '');
            formData.append('seo_keywords', currentItem.seo_keywords || '');
            formData.append('seo_description', currentItem.seo_description || '');
            setLoading(true);
            const {code, msg, data} = await axiosInstance.post(post_url, formData);
            if (code === 0) {
                message.success("操作成功")
                onRequestClose(true);
            } else {
                message.error(msg || '网络异常')
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

            <Spin spinning={loading} tip="">
                <div className="flex flex-col">
                    <div ref={divRef}  className="max-h-[70vh] overflow-y-auto">
                        <div className="">
                            <div className="flex flex-col gap-4 pt-4 pb-0">
                                <div className="flex flex-row gap-4">
                                    <FormLabel title="标题" required={true}></FormLabel>
                                    <Input placeholder="请输入标题" value={currentItem.title}
                                           onChange={(e) => handleInputChange("title", e.target.value)}
                                           style={{width: 600}}/>
                                </div>
                                <div className="flex flex-row gap-4">
                                    <FormLabel title="客户" ></FormLabel>
                                    <Input placeholder="请输入" value={currentItem.client}
                                           onChange={(e) => handleInputChange("client", e.target.value)}
                                           style={{width: 600}}/>
                                </div>
                                <div className="flex flex-row gap-4">
                                    <FormLabel title="封面图" required={true}></FormLabel>
                                    <ImageUpload maxCount={1}
                                                 accept="image/*"
                                                 imageList={imageList}
                                                 onImageUploadChange={handleImageUploadChange}/>
                                </div>

                            </div>

                            <Divider/>

                            <LabelPanel title="案例详情"></LabelPanel>
                            <div className="flex flex-col gap-4 px-2 py-2">
                                <WangEditor htmlText={currentItem.description} onHtmlResult={handleHtmlChange}/>
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

export default CaseModal;