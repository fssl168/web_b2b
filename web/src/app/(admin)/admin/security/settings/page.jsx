'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button, Card, Switch, Table, Tag, Space, Badge, Alert, message, App, Input, Modal, Descriptions, List, Avatar } from 'antd';
import { LockOutlined, MobileOutlined, KeyOutlined, SafetyOutlined, EyeOutlined, EyeInvisibleOutlined, ReloadOutlined, CheckCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import axiosInstance from '@/utils/axios';
import dayjs from 'dayjs';

const { Password } = Input;

const SecuritySettingsPage = () => {
  const { message: antdMessage, modal } = App.useApp();
  const router = useRouter();
  
  // 状态管理
  const [securityOverview, setSecurityOverview] = useState(null);
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);
  const [twoFactorMethod, setTwoFactorMethod] = useState('email');
  const [hasEmail, setHasEmail] = useState(false);
  const [verifying2FA, setVerifying2FA] = useState(false);
  const [verificationCode, setVerificationCode] = useState('');
  const [showVerificationModal, setShowVerificationModal] = useState(false);
  const [tempToken, setTempToken] = useState('');
  const [emailMasked, setEmailMasked] = useState('');

  // 获取安全概览
  const fetchSecurityOverview = async () => {
    try {
      const response = await axiosInstance.get('/myapp/admin/security/overview');
      if (response.code === 0) {
        setSecurityOverview(response.data);
        setTwoFactorEnabled(response.data.two_factor.enabled);
        setTwoFactorMethod(response.data.two_factor.method);
        setHasEmail(!!response.data.two_factor.has_email);
      }
    } catch (error) {
      console.error('Failed to fetch security overview:', error);
    }
  };

  // 获取设备列表
  const fetchDevices = async () => {
    try {
      const response = await axiosInstance.get('/myapp/admin/security/devices');
      if (response.code === 0) {
        setDevices(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch devices:', error);
    }
  };

  // 启用双因素认证
  const handleEnable2FA = async () => {
    if (!hasEmail) {
      antdMessage.error('请先设置邮箱地址');
      return;
    }

    try {
      setLoading(true);
      const response = await axiosInstance.post('/myapp/admin/security/2fa/enable', {
        method: 'email'
      });
      
      if (response.code === 0) {
        antdMessage.success('双因素认证已启用');
        fetchSecurityOverview();
      } else {
        antdMessage.error(response.msg);
      }
    } catch (error) {
      console.error('Failed to enable 2FA:', error);
      antdMessage.error('启用失败');
    } finally {
      setLoading(false);
    }
  };

  // 禁用双因素认证
  const handleDisable2FA = async () => {
    modal.confirm({
      title: '确认禁用双因素认证',
      icon: <ExclamationCircleOutlined />,
      content: '禁用后，您的账户安全性将降低。确定要禁用吗？',
      onOk: async () => {
        try {
          setLoading(true);
          const response = await axiosInstance.post('/myapp/admin/security/2fa/disable');
          
          if (response.code === 0) {
            antdMessage.success('双因素认证已禁用');
            fetchSecurityOverview();
          } else {
            antdMessage.error(response.msg);
          }
        } catch (error) {
          console.error('Failed to disable 2FA:', error);
          antdMessage.error('禁用失败');
        } finally {
          setLoading(false);
        }
      },
    });
  };

  // 发送验证码
  const handleSendVerificationCode = async () => {
    try {
      const response = await axiosInstance.post('/myapp/admin/security/2fa/send');
      if (response.code === 0) {
        antdMessage.success(response.msg);
      } else {
        antdMessage.error(response.msg);
      }
    } catch (error) {
      console.error('Failed to send verification code:', error);
      antdMessage.error('发送失败');
    }
  };

  // 信任设备
  const handleTrustDevice = async (deviceId, trust) => {
    try {
      const response = await axiosInstance.post('/myapp/admin/security/device/trust', {
        device_id: deviceId,
        trust: trust
      });
      
      if (response.code === 0) {
        antdMessage.success(trust ? '设备已设为可信' : '设备已设为不可信');
        fetchDevices();
      } else {
        antdMessage.error(response.msg);
      }
    } catch (error) {
      console.error('Failed to trust device:', error);
      antdMessage.error('操作失败');
    }
  };

  // 撤销设备
  const handleRevokeDevice = async (deviceId, deviceName) => {
    modal.confirm({
      title: '确认撤销设备',
      icon: <ExclamationCircleOutlined />,
      content: `确定要撤销设备 "${deviceName}" 吗？该设备将被强制下线。`,
      onOk: async () => {
        try {
          const response = await axiosInstance.post('/myapp/admin/security/device/revoke', {
            device_id: deviceId
          });
          
          if (response.code === 0) {
            antdMessage.success('设备已撤销');
            fetchDevices();
          } else {
            antdMessage.error(response.msg);
          }
        } catch (error) {
          console.error('Failed to revoke device:', error);
          antdMessage.error('操作失败');
        }
      },
    });
  };

  // 刷新数据
  const handleRefresh = () => {
    fetchSecurityOverview();
    fetchDevices();
  };

  // 初始加载
  useEffect(() => {
    fetchSecurityOverview();
    fetchDevices();
  }, []);

  // 设备类型映射
  const deviceTypeMap = {
    desktop: { text: '桌面设备', color: 'blue' },
    mobile: { text: '移动设备', color: 'green' },
    tablet: { text: '平板设备', color: 'orange' },
    unknown: { text: '未知设备', color: 'gray' }
  };

  // 设备表格列
  const deviceColumns = [
    {
      title: '设备名称',
      dataIndex: 'device_name',
      key: 'device_name',
      render: (text, record) => (
        <Space>
          <Avatar icon={<MobileOutlined />} />
          <span>{text}</span>
          {record.is_current && (
            <Tag color="green">当前设备</Tag>
          )}
        </Space>
      ),
    },
    {
      title: '设备类型',
      dataIndex: 'device_type',
      key: 'device_type',
      render: (text) => {
        const typeInfo = deviceTypeMap[text] || deviceTypeMap.unknown;
        return <Tag color={typeInfo.color}>{typeInfo.text}</Tag>;
      },
    },
    {
      title: '最后登录',
      dataIndex: 'last_login_time',
      key: 'last_login_time',
      render: (text) => text ? dayjs(text).format('YYYY-MM-DD HH:mm:ss') : '-',
    },
    {
      title: '最后IP',
      dataIndex: 'last_login_ip',
      key: 'last_login_ip',
    },
    {
      title: '登录次数',
      dataIndex: 'login_count',
      key: 'login_count',
    },
    {
      title: '状态',
      dataIndex: 'is_trusted',
      key: 'is_trusted',
      render: (text) => (
        <Tag color={text ? 'green' : 'orange'}>
          {text ? '可信' : '不可信'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button 
            size="small" 
            onClick={() => handleTrustDevice(record.device_id, !record.is_trusted)}
          >
            {record.is_trusted ? '设为不可信' : '设为可信'}
          </Button>
          <Button 
            size="small" 
            danger
            onClick={() => handleRevokeDevice(record.device_id, record.device_name)}
          >
            撤销
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">安全设置</h1>
        <Button 
          icon={<ReloadOutlined />}
          onClick={handleRefresh}
        >
          刷新
        </Button>
      </div>

      {/* 安全概览卡片 */}
      <Card className="mb-6">
        <Descriptions title="安全概览" bordered>
          <Descriptions.Item label="双因素认证">
            {twoFactorEnabled ? (
              <Badge status="success" text="已启用" />
            ) : (
              <Badge status="default" text="未启用" />
            )}
          </Descriptions.Item>
          <Descriptions.Item label="密码状态">
            {securityOverview?.password?.is_expired ? (
              <Badge status="error" text="已过期" />
            ) : (
              <Badge status="success" text="正常" />
            )}
          </Descriptions.Item>
          <Descriptions.Item label="密码剩余天数">
            {securityOverview?.password?.days_remaining || 0} 天
          </Descriptions.Item>
          <Descriptions.Item label="活跃设备数">
            {devices.filter(d => d.is_active).length} 台
          </Descriptions.Item>
        </Descriptions>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 双因素认证设置 */}
        <Card 
          title={<><SafetyOutlined /> 双因素认证</>} 
          variant="outlined"
        >
          {!hasEmail ? (
            <Alert 
              message="需要设置邮箱" 
              description="请先在个人资料中设置邮箱地址，才能启用双因素认证。" 
              type="warning" 
              showIcon 
              action={
                <Button size="small" type="primary" onClick={() => router.push('/admin/user')}>
                  去设置
                </Button>
              }
            />
          ) : (
            <div>
              <div className="flex items-center justify-between mb-4">
                <span>启用双因素认证</span>
                <Switch 
                  checked={twoFactorEnabled} 
                  onChange={(checked) => {
                    if (checked) {
                      handleEnable2FA();
                    } else {
                      handleDisable2FA();
                    }
                  }}
                  loading={loading}
                />
              </div>
              
              {twoFactorEnabled && (
                <div className="mt-4 space-y-4">
                  <Alert 
                    message="双因素认证已启用" 
                    description="登录时需要输入邮箱验证码，提高账户安全性。" 
                    type="success" 
                    showIcon 
                  />
                  <div className="flex space-x-2">
                    <Button 
                      type="default" 
                      onClick={handleSendVerificationCode}
                    >
                      发送测试验证码
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </Card>

        {/* 密码策略信息 */}
        <Card 
          title={<><KeyOutlined /> 密码策略</>} 
          variant="outlined"
        >
          <List
            size="small"
            dataSource={[
              { title: '密码长度', value: '至少8个字符' },
              { title: '密码复杂度', value: '包含大小写字母、数字、特殊字符' },
              { title: '密码过期', value: '90天' },
              { title: '密码历史', value: '不能使用最近5次密码' },
              { title: '过期提醒', value: '过期前7天' },
            ]}
            renderItem={(item) => (
              <List.Item>
                <List.Item.Meta
                  avatar={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                  title={item.title}
                  description={item.value}
                />
              </List.Item>
            )}
          />
          
          {securityOverview?.password?.should_warn && !securityOverview?.password?.is_expired && (
            <Alert 
              message="密码即将过期" 
              description={`您的密码将在 ${securityOverview.password.days_remaining} 天后过期，请及时修改。`} 
              type="warning" 
              showIcon 
              className="mt-4"
            />
          )}
          
          {securityOverview?.password?.is_expired && (
            <Alert 
              message="密码已过期" 
              description="请立即修改密码，否则将无法登录。" 
              type="error" 
              showIcon 
              className="mt-4"
              action={
                <Button size="small" type="primary">
                  立即修改
                </Button>
              }
            />
          )}
        </Card>
      </div>

      {/* 设备管理 */}
      <Card 
        title={<><MobileOutlined /> 设备管理</>} 
        variant="outlined"
        className="mt-6"
      >
        <Table
          columns={deviceColumns}
          dataSource={devices}
          rowKey="device_id"
          pagination={{ pageSize: 5 }}
          locale={{ emptyText: '暂无登录设备记录' }}
        />
        <div className="mt-4 text-gray-500 text-sm">
          <p>• 可信设备：登录时不会触发额外验证</p>
          <p>• 不可信设备：可能会触发额外的安全验证</p>
          <p>• 撤销设备：将强制该设备下线</p>
        </div>
      </Card>

      {/* 安全建议 */}
      <Card 
        title={<><ExclamationCircleOutlined /> 安全建议</>} 
        variant="outlined"
        className="mt-6"
      >
        <List
          size="small"
          dataSource={[
            '启用双因素认证提高账户安全性',
            '定期修改密码，避免使用重复密码',
            '只在可信设备上登录',
            '注意保护邮箱账号安全',
            '定期检查登录设备列表，及时撤销可疑设备',
          ]}
          renderItem={(item) => (
            <List.Item>
              <ExclamationCircleOutlined style={{ color: '#fa8c16', marginRight: 8 }} />
              {item}
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

export default SecuritySettingsPage;