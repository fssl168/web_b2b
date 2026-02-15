'use client'
import React from 'react';
import api from "@/utils/axiosApi";
import { useState, useRef } from 'react';
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle
} from "@/components/ui/alert-dialog";

// 过滤用户输入，防止XSS攻击
const sanitizeInput = (input) => {
    if (!input) return '';
    return input
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
};


const InquiryForm = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        tel: '',
        message: ''
    });
    const [loading, setLoading] = useState(false);
    const [alertState, setAlertState] = useState({
        open: false,
        title: '',
        description: '',
        variant: 'default' // 'default' or 'destructive'
    });

    const handleInputChange = (e) => {
        const { id, value } = e.target;
        setFormData({
            ...formData,
            [id]: value
        });
    };

    const showAlert = (title, description, variant = 'default') => {
        setAlertState({
            open: true,
            title,
            description,
            variant
        });
    };

    const closeAlert = () => {
        setAlertState(prev => ({ ...prev, open: false }));
    };

    const sendInquiryData = async (e) => {
        e.preventDefault();

        // 基本验证
        if (!formData.name || !formData.email || !formData.message) {
            showAlert('Validation Failed', 'Please fill in all required fields (Name, Email, and Message)', 'destructive');
            return;
        }

        // 邮箱格式验证
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData.email)) {
            showAlert('Validation Failed', 'Please enter a valid email address', 'destructive');
            return;
        }

        try {
            setLoading(true);
            const submitData = new FormData();
            // 过滤用户输入，防止XSS攻击
            submitData.append('name', sanitizeInput(formData.name));
            submitData.append('email', sanitizeInput(formData.email));
            submitData.append('message', sanitizeInput(formData.message));

            const { code, msg } = await api.post('/myapp/index/inquiry/create', submitData);

            if (code === 0) {
                showAlert('Submission Successful', 'We will contact you as soon as possible', 'default');
                // 重置表单
                setFormData({
                    name: '',
                    email: '',
                    tel: '',
                    message: ''
                });
            } else {
                showAlert('Submission Failed', msg || 'Please try again later', 'destructive');
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            showAlert('Submission Failed', 'Please check your network connection', 'destructive');
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <AlertDialog open={alertState.open} onOpenChange={closeAlert}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>
                            {alertState.title}
                        </AlertDialogTitle>
                        <AlertDialogDescription>
                            {alertState.description}
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogAction className="bg-mainColorNormal hover:bg-mainColorDeep text-white" onClick={closeAlert}>OK</AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>

            <div className="transform transition duration-300 hover:translate-y-[-5px]">
                <h2 className="text-xl font-bold mb-6 border-b border-gray-200 pb-2">Inquiry Form</h2>
                <form className="space-y-4" onSubmit={sendInquiryData}>
                    <div>
                        <label className="block text-sm mb-2 text-gray-600" htmlFor="name">
                            Name <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="text"
                            id="name"
                            value={formData.name}
                            onChange={handleInputChange}
                            className="w-full px-4 py-2 rounded-md bg-gray-50 text-gray-800 border border-gray-200 transition focus:outline-none"
                            placeholder="Your Name"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm mb-2 text-gray-600" htmlFor="email">
                            Email <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="email"
                            id="email"
                            value={formData.email}
                            onChange={handleInputChange}
                            className="w-full px-4 py-2 rounded-md bg-gray-50 text-gray-800 border border-gray-200 transition focus:outline-none"
                            placeholder="Your Email"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm mb-2 text-gray-600" htmlFor="message">
                            Message <span className="text-red-500">*</span>
                        </label>
                        <textarea
                            id="message"
                            value={formData.message}
                            onChange={handleInputChange}
                            className="w-full px-4 py-2 rounded-md bg-gray-50 text-gray-800 border border-gray-200 transition focus:outline-none"
                            placeholder="Your Message"
                            rows="4"
                            required
                        ></textarea>
                    </div>
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-mainColorNormal hover:bg-mainColorDeep text-white py-2 rounded-md transition duration-300 transform hover:translate-y-[-2px] hover:shadow-lg disabled:opacity-70 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Submitting...' : 'Submit'}
                    </button>
                </form>
            </div>
        </>
    );
};

export default InquiryForm;