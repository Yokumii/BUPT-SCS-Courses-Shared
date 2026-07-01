import { useState } from 'react';
import { Card, Select, Button, Space, InputNumber, message, Statistic, Row, Col, Divider, Empty, Table, Tag } from 'antd';
import { BarChartOutlined, ThunderboltOutlined, ClockCircleOutlined, DollarOutlined } from '@ant-design/icons';
import { viewReport } from '../../api';

export default function Report() {
  const [timeWindow, setTimeWindow] = useState('DAY');
  const [pileId, setPileId] = useState<number | undefined>(undefined);
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchReport = async () => {
    setLoading(true);
    try {
      const res = await viewReport(timeWindow, pileId);
      setReport(res.data);
    } catch (err: any) {
      message.error(err.response?.data?.detail || '获取报表失败');
    } finally {
      setLoading(false);
    }
  };

  const timeWindowLabel: Record<string, string> = { DAY: '日报表', WEEK: '周报表', MONTH: '月报表' };
  const summary = report?.summary;

  const columns = [
    { title: '时间', dataIndex: 'time_window', key: 'time_window', render: (v: string) => timeWindowLabel[v] || v },
    { title: '充电桩编号', dataIndex: 'pile_name', key: 'pile_name', render: (v: string, r: any) => <Tag color="blue">{v || `#${r.pile_id}`}</Tag> },
    { title: '累计充电次数', dataIndex: 'total_charge_count', key: 'total_charge_count', render: (v: number) => `${v} 次` },
    { title: '累计充电时长', dataIndex: 'total_duration', key: 'total_duration', render: (v: number) => `${v.toFixed(2)} 小时` },
    { title: '累计充电量', dataIndex: 'total_kwh', key: 'total_kwh', render: (v: number) => `${v.toFixed(2)} 度` },
    { title: '累计充电费用', dataIndex: 'total_charge_fee', key: 'total_charge_fee', render: (v: number) => `¥${v.toFixed(2)}` },
    { title: '累计服务费用', dataIndex: 'total_service_fee', key: 'total_service_fee', render: (v: number) => `¥${v.toFixed(2)}` },
    { title: '累计总费用', dataIndex: 'total_fee', key: 'total_fee', render: (v: number) => <strong style={{ color: '#1a3d7c' }}>¥{v.toFixed(2)}</strong> },
  ];

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto' }}>
      <Card title={<Space><BarChartOutlined />运营报表</Space>} className="interactive-card page-enter">
        <Space style={{ marginBottom: 24 }} size="middle" wrap>
          <Select value={timeWindow} onChange={setTimeWindow} style={{ width: 120 }}>
            <Select.Option value="DAY">日报表</Select.Option>
            <Select.Option value="WEEK">周报表</Select.Option>
            <Select.Option value="MONTH">月报表</Select.Option>
          </Select>
          <InputNumber placeholder="桩号（空=全部）" min={1} max={5} value={pileId} onChange={(v) => setPileId(v || undefined)} style={{ width: 160 }} />
          <Button type="primary" onClick={fetchReport} loading={loading}>查询报表</Button>
        </Space>

        <Divider />

        {report ? (
          <>
            <div style={{ marginBottom: 24 }}><span style={{ fontSize: 18, fontWeight: 600, color: '#1a3d7c' }}>{timeWindowLabel[report.time_window]}</span><span style={{ marginLeft: 12, color: '#999' }}>{report.pile_id ? `充电桩 #${report.pile_id}` : '全部充电桩'}</span></div>
            <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
              <Col span={6}><Card size="small"><Statistic title="累计充电次数" value={summary.total_charge_count} suffix="次" prefix={<ThunderboltOutlined />} /></Card></Col>
              <Col span={6}><Card size="small"><Statistic title="累计充电时长" value={summary.total_duration} precision={2} suffix="小时" prefix={<ClockCircleOutlined />} /></Card></Col>
              <Col span={6}><Card size="small"><Statistic title="累计充电量" value={summary.total_kwh} precision={2} suffix="度" prefix={<ThunderboltOutlined />} /></Card></Col>
              <Col span={6}><Card size="small"><Statistic title="累计总费用" value={summary.total_fee} precision={2} prefix={<DollarOutlined />} suffix="元" /></Card></Col>
            </Row>
            <Table dataSource={report.rows} columns={columns} rowKey="pile_id" pagination={false} bordered size="small" />
          </>
        ) : (
          <Empty description="点击查询按钮生成报表" image={Empty.PRESENTED_IMAGE_SIMPLE} />
        )}
      </Card>
    </div>
  );
}
