import { useEffect, useState } from 'react';
import { Card, Table, Tag, Button, Statistic, Row, Col, Empty } from 'antd';
import { FileTextOutlined, ThunderboltOutlined, DollarOutlined } from '@ant-design/icons';
import { viewBills } from '../../api';

export default function BillHistory() {
  const [bills, setBills] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchBills = async () => {
    setLoading(true);
    try {
      const res = await viewBills();
      setBills(res.data);
    } catch {
      setBills([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchBills(); }, []);

  const totalFee = bills.reduce((s, b) => s + b.total_fee, 0);
  const totalKwh = bills.reduce((s, b) => s + b.charged_kwh, 0);
  const formatTime = (v: string) => v?.slice(0, 19).replace('T', ' ');

  const columns = [
    { title: '详单编号', dataIndex: 'id', key: 'id', width: 90, render: (v: number) => <Tag color="purple">#{v}</Tag> },
    { title: '详单生成时间', dataIndex: 'created_at', key: 'created_at', width: 170, render: formatTime },
    { title: '充电桩编号', dataIndex: 'pile_name', key: 'pile_name', width: 110, render: (v: string, r: any) => <Tag color="blue">{v || `#${r.pile_id}`}</Tag> },
    { title: '充电电量', dataIndex: 'charged_kwh', key: 'charged_kwh', width: 110, render: (v: number) => `${v.toFixed(2)} 度` },
    { title: '充电时长', dataIndex: 'duration', key: 'duration', width: 110, render: (v: number) => `${v.toFixed(2)} 小时` },
    { title: '启动时间', dataIndex: 'start_time', key: 'start_time', width: 170, render: formatTime },
    { title: '停止时间', dataIndex: 'end_time', key: 'end_time', width: 170, render: formatTime },
    { title: '充电费用', dataIndex: 'charge_fee', key: 'charge_fee', width: 100, render: (v: number) => `¥${v.toFixed(2)}` },
    { title: '服务费用', dataIndex: 'service_fee', key: 'service_fee', width: 100, render: (v: number) => `¥${v.toFixed(2)}` },
    { title: '总费用', dataIndex: 'total_fee', key: 'total_fee', width: 100, fixed: 'right' as const, render: (v: number) => <span style={{ fontWeight: 700, color: '#1a3d7c' }}>¥{v.toFixed(2)}</span> },
  ];

  return (
    <div>
      <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
        <Col span={8}><Card className="interactive-card"><Statistic title="充电总次数" value={bills.length} suffix="次" prefix={<ThunderboltOutlined style={{ color: '#1a3d7c' }} />} /></Card></Col>
        <Col span={8}><Card className="interactive-card"><Statistic title="累计充电量" value={totalKwh.toFixed(1)} suffix="度" prefix={<ThunderboltOutlined style={{ color: '#52c41a' }} />} /></Card></Col>
        <Col span={8}><Card className="interactive-card"><Statistic title="累计消费" value={totalFee.toFixed(2)} prefix={<DollarOutlined style={{ color: '#faad14' }} />} suffix="元" /></Card></Col>
      </Row>

      <Card title={<span><FileTextOutlined /> 充电详单列表</span>} extra={<Button onClick={fetchBills} loading={loading}>刷新</Button>} className="interactive-card page-enter">
        {bills.length > 0 ? <Table dataSource={bills} columns={columns} rowKey="id" loading={loading} pagination={{ pageSize: 8 }} size="small" scroll={{ x: 1320 }} /> : <Empty description="暂无充电详单" image={Empty.PRESENTED_IMAGE_SIMPLE} />}
      </Card>
    </div>
  );
}
