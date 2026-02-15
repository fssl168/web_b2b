import '@wangeditor/editor/dist/css/style.css' // 引入 css

import React, {useState, useEffect} from 'react'
import {Editor, Toolbar} from '@wangeditor/editor-for-react'
import {message} from "antd";

// 参考 https://www.wangeditor.com/v5/menu-config.html

function WangEditor({htmlText, onHtmlResult}) {

    // 单个图片文件的最大体积限制(M)
    const maxImageFileSize = 10 * 1024 * 1024;

    // 单个视频的最大体积限制(M)
    const maxVideoFileSize = 500 * 1024 * 1024;

    // editor 实例
    const [editor, setEditor] = useState(null)

    // 编辑器内容
    const [html, setHtml] = useState(htmlText ? htmlText : '')

    useEffect(() => {
        setHtml(htmlText ? htmlText : '')
    }, [htmlText])

    const onHtmlChange = (html) => {
        setHtml(html)
        onHtmlResult(html)
    }

    // 工具栏配置
    const toolbarConfig = {}


    // 编辑器配置
    const editorConfig = {
        placeholder: '请输入产品详情...',
        MENU_CONF: {}
    }


    editorConfig.MENU_CONF['uploadImage'] = {
        server: process.env.NEXT_PUBLIC_BASE_URL + '/myapp/admin/cdn/uploadFile',
        fieldName: 'my-file',
        // 单个文件的最大体积限制
        maxFileSize: maxImageFileSize, // M
        // 最多可上传几个文件，默认为 100
        maxNumberOfFiles: 1,
        // 选择文件时的类型限制，默认为 ['image/*'] 。如不想限制，则设置为 []
        allowedFileTypes: ['image/*'],
        // 自定义上传参数，例如传递验证的 token 等。参数会被添加到 formData 中，一起上传到服务端。
        meta: {},
        // 将 meta 拼接到 url 参数中，默认 false
        metaWithUrl: false,
        // 自定义增加 http  header
        headers: {
            Accept: 'application/json',
            admintoken: localStorage.getItem("admintoken") || '',
        },
        // 跨域是否传递 cookie ，默认为 false
        withCredentials: false,
        // 超时时间，默认为 10 秒
        timeout: 15 * 1000,

        // 单个文件上传成功之后
        onSuccess(file, res) {
            // 移除调试信息输出
        },

        // 单个文件上传失败
        onFailed(file, res) {
            // 移除调试信息输出
            if(res){
                message.error(res.message || '上传失败');
            } else {
                message.error('上传失败');
            }
        },

        //上传错误，或者触发 timeout 超时
        onError(file, err, res) {
            // 移除调试信息输出，使用更友好的错误提示
            message.error('上传出错，请稍后重试');
        },

    }



    editorConfig.MENU_CONF['uploadVideo'] = {
        server: process.env.NEXT_PUBLIC_BASE_URL + '/myapp/admin/cdn/uploadFile',
        fieldName: 'my-file',
        // 单个文件的最大体积限制
        maxFileSize: maxVideoFileSize,
        // 最多可上传几个文件，默认为 100
        maxNumberOfFiles: 1,
        // 选择文件时的类型限制，默认为 ['video/*'] 。如不想限制，则设置为 []
        allowedFileTypes: ['video/*'],
        // 自定义上传参数，例如传递验证的 token 等。参数会被添加到 formData 中，一起上传到服务端。
        meta: {},
        // 将 meta 拼接到 url 参数中，默认 false
        metaWithUrl: false,
        // 自定义增加 http  header
        headers: {
            Accept: 'application/json',
            admintoken: localStorage.getItem("admintoken") || '',
        },
        // 跨域是否传递 cookie ，默认为 false
        withCredentials: false,
        // 超时时间，默认为 10 秒
        timeout: 90 * 1000, // 90 秒

        // 单个文件上传成功之后
        onSuccess(file, res) {
            // 移除调试信息输出
        },

        // 单个文件上传失败
        onFailed(file, res) {
            // 移除调试信息输出
            if(res){
                message.error(res.message || '上传失败');
            } else {
                message.error('上传失败');
            }
        },

        //上传错误，或者触发 timeout 超时
        onError(file, err, res) {
            // 移除调试信息输出，使用更友好的错误提示
            message.error('上传出错，请稍后重试');
        },
    }

    // 及时销毁 editor ，重要！
    useEffect(() => {
        return () => {
            if (editor == null) return
            editor.destroy()
            setEditor(null)
        }
    }, [editor])

    return (
        <>
            <div style={{border: '1px solid #ccc', zIndex: 100}}
                 onClick={()=> editor.focus()}>
                <Toolbar
                    editor={editor}
                    defaultConfig={toolbarConfig}
                    mode="default"
                    style={{borderBottom: '1px solid #ccc'}}
                />
                <Editor
                    defaultConfig={editorConfig}
                    value={html}
                    onCreated={setEditor}
                    onChange={(editor) => onHtmlChange(editor.getHtml())}
                    mode="default"
                    style={{minHeight: '500px', overflowY: 'hidden'}}
                />
            </div>
            {/*<div style={{marginTop: '15px'}}>{html}</div>*/}
        </>
    )
}

export default WangEditor
