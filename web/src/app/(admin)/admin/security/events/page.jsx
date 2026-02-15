'use client';
import React, { useState, useEffect } from 'react';
import { Button, Table, Tag, Space, Badge, DatePicker, Input, Select, Card, Statistic, Row, Col, App } from 'antd';
import { SearchOutlined, ReloadOutlined, DownloadOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import axiosInstance from '@/utils/axios';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { Search } = Input;

const SecurityEventsPage = () => {
  const { modal } = App.useApp();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [searchText, setSearchText] = useState('');
  const [dateRange, setDateRange] = useState(null);
  const [incidentType, setIncidentType] = useState('');
  const [incidentLevel, setIncidentLevel] = useState('');

  // 统计数据
  const [stats, setStats] = useState({
    totalIncidents: 0,
    highLevelIncidents: 0,
    criticalIncidents: 0,
    todayIncidents: 0,
  });

  // 事件类型映射
  const incidentTypeMap = {
    'LOGIN_FAILURE': '登录失败',
    'LOGIN_SUCCESS': '登录成功',
    'PERMISSION_DENIED': '权限拒绝',
    'SQL_INJECTION_ATTEMPT': 'SQL注入尝试',
    'XSS_ATTEMPT': 'XSS攻击尝试',
    'CSRF_ATTEMPT': 'CSRF攻击尝试',
    'FILE_UPLOAD_VIOLATION': '文件上传违规',
    'BRUTE_FORCE_ATTEMPT': '暴力破解尝试',
    'UNAUTHORIZED_ACCESS': '未授权访问',
    'SUSPICIOUS_ACTIVITY': '可疑活动',
  };

  // 事件级别映射
  const incidentLevelMap = {
    'LOW': { text: '低', color: 'green' },
    'MEDIUM': { text: '中', color: 'blue' },
    'HIGH': { text: '高', color: 'orange' },
    'CRITICAL': { text: '严重', color: 'red' },
  };

  // 获取安全事件数据
  const fetchSecurityEvents = async () => {
    setLoading(true);
    try {
      const response = await axiosInstance.get('/myapp/admin/security/list', {
        params: {
          page,
          page_size: pageSize,
          search: searchText,
          start_date: dateRange ? dateRange[0].format('YYYY-MM-DD') : '',
          end_date: dateRange ? dateRange[1].format('YYYY-MM-DD') : '',
          incident_type: incidentType,
          incident_level: incidentLevel,
        },
      });
      
      if (response.code === 0) {
        setData(response.data.list || []);
        setTotal(response.data.total || 0);
      }
    } catch (error) {
      console.error('Failed to fetch security events:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取统计数据
  const fetchStats = async () => {
    try {
      const response = await axiosInstance.get('/myapp/admin/security/stats');
      if (response.code === 0) {
        setStats(response.data || stats);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  // 初始加载
  useEffect(() => {
    fetchSecurityEvents();
    fetchStats();
  }, [page, pageSize, searchText, dateRange, incidentType, incidentLevel]);

  // 刷新数据
  const handleRefresh = () => {
    fetchSecurityEvents();
    fetchStats();
  };

  // 下载报告
  const handleDownloadReport = () => {
    // 实现下载报告功能
    console.log('Download report');
  };

  // 表格列定义
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '事件类型',
      dataIndex: 'incident_type',
      key: 'incident_type',
      render: (text) => (
        <Tag color="blue">
          {incidentTypeMap[text] || text}
        </Tag>
      ),
    },
    {
      title: '事件级别',
      dataIndex: 'level',
      key: 'level',
      render: (text) => {
        const levelInfo = incidentLevelMap[text] || { text: text, color: 'default' };
        return (
          <Tag color={levelInfo.color}>
            {levelInfo.text}
          </Tag>
        );
      },
    },
    {
      title: '事件描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'IP地址',
      dataIndex: 'ip',
      key: 'ip',
      width: 150,
    },
    {
      title: '时间',
      dataIndex: 'create_time',
      key: 'create_time',
      width: 200,
      render: (text) => text ? dayjs(text).format('YYYY-MM-DD HH:mm:ss') : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record) => (
        <Space size="middle">
          <Button 
            size="small" 
            type="link" 
            onClick={() => showDetail(record)}
          >
            详情
          </Button>
        </Space>
      ),
    },
  ];

  // 显示详情
  const showDetail = (record) => {
    modal.info({
      title: '安全事件详情',
      width: 600,
      content: (
        <div className="space-y-2">
          <p><strong>事件类型:</strong> {incidentTypeMap[record.incident_type] || record.incident_type}</p>
          <p><strong>事件级别:</strong> {incidentLevelMap[record.level]?.text || record.level}</p>
          <p><strong>事件描述:</strong> {record.description}</p>
          <p><strong>IP地址:</strong> {record.ip}</p>
          <p><strong>用户:</strong> {record.username || 'anonymous'}</p>
          <p><strong>请求URL:</strong> {record.request_url || '-'}</p>
          <p><strong>请求方法:</strong> {record.request_method || '-'}</p>
          <p><strong>User-Agent:</strong> {record.user_agent || '-'}</p>
          <p><strong>时间:</strong> {record.create_time ? dayjs(record.create_time).format('YYYY-MM-DD HH:mm:ss') : '-'}</p>
        </div>
      ),
    });
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">安全事件管理</h1>
        <Space>
          <Button 
            type="primary" 
            icon={<ReloadOutlined />}
            onClick={handleRefresh}
          >
            刷新
          </Button>
          <Button 
            icon={<DownloadOutlined />}
            onClick={handleDownloadReport}
          >
            下载报告
          </Button>
        </Space>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} className="mb-6">
        <Col span={6}>
          <Card>
            <Statistic 
              title="总事件数" 
              value={stats.totalIncidents} 
              prefix={<ExclamationCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="高级事件" 
              value={stats.highLevelIncidents} 
              prefix={<Badge status="warning" />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="严重事件" 
              value={stats.criticalIncidents} 
              prefix={<Badge status="error" />}
              valueStyle={{ color: '#f5222d' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="今日事件" 
              value={stats.todayIncidents} 
              prefix={<Badge status="processing" />}
            />
          </Card>
        </Col>
      </Row>

      {/* 搜索和筛选 */}
      <Card className="mb-6">
        <Row gutter={16}>
          <Col span={8}>
            <Search
              placeholder="搜索事件描述"
              allowClear
              enterButton={<SearchOutlined />}
              size="middle"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              onSearch={() => setPage(1)}
            />
          </Col>
          <Col span={8}>
            <RangePicker
              style={{ width: '100%' }}
              value={dateRange}
              onChange={setDateRange}
            />
          </Col>
          <Col span={4}>
            <Select
              placeholder="事件类型"
              allowClear
              style={{ width: '100%' }}
              value={incidentType}
              onChange={setIncidentType}
            >
              {Object.entries(incidentTypeMap).map(([key, value]) => (
                <Option key={key} value={key}>{value}</Option>
              ))}
            </Select>
          </Col>
          <Col span={4}>
            <Select
              placeholder="事件级别"
              allowClear
              style={{ width: '100%' }}
              value={incidentLevel}
              onChange={setIncidentLevel}
            >
              {Object.entries(incidentLevelMap).map(([key, value]) => (
                <Option key={key} value={key}>{value.text}</Option>
              ))}
            </Select>
          </Col>
        </Row>
      </Card>

      {/* 事件列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={data}
          loading={loading}
          pagination={{
            current: page,
            pageSize: pageSize,
            total: total,
            onChange: (current, size) => {
              setPage(current);
              setPageSize(size);
            },
          }}
          rowKey="id"
        />
      </Card>
    </div>
  );
};

export default SecurityEventsPage;