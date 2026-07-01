import { useEffect, useState } from 'react';
import { Card, Table, Tag, Button, Space, Statistic, Row, Col } from 'antd';
import { DashboardOutlined, ThunderboltOutlined, ClockCircleOutlined, FireOutlined } from '@ant-design/icons';
import { viewAllPileStatus } from '../../api';

export default function Dashboard() {
  const [piles, setPiles] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchPiles = async () => {
    setLoading(true);
    try {
      const res = await viewAllPileStatus();
      setPiles(res.data);
    } catch {
      setPiles([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchPiles(); }, []);

  const statusConfig: Record<string, { color: string; label: string }> = {
    ONLINE: { color: 'green', label: '运行中' },
    OFFLINE: { color: 'default', label: '已关闭' },
    FAULT: { color: 'red', label: '故障' },
  };

  const columns = [
    {
      title: '编号', dataIndex: 'name', key: 'name',
      render: (v: string) => <span style={{ fontWeight: 600 }}>{v}</span>
    },
    {
      title: '类型', dataIndex: 'pile_type', key: 'pile_type',
      render: (v: string) => (
        <Tag color={v === 'FAST' ? 'gold' : 'green'} icon={<ThunderboltOutlined />}>
          {v === 'FAST' ? '快充 30kW' : '慢充 10kW'}
        </Tag>
      )
    },
    {
      title: '状态', dataIndex: 'status', key: 'status',
      render: (v: string) => <Tag color={statusConfig[v]?.color}><span className="status-dot" style={{ background: v === 'ONLINE' ? '#52c41a' : v === 'FAULT' ? '#ff4d4f' : '#bfbfbf' }} />{statusConfig[v]?.label}</Tag>
    },
    {
      title: '队列车辆', dataIndex: 'queue_size', key: 'queue_size',
      render: (v: number) => v > 0 ? <Tag color="blue">{v} 辆</Tag> : <span style={{ color: '#999' }}>空</span>
    },
    { title: '累计充电', dataIndex: 'accum_charge_count', key: 'accum_charge_count', render: (v: number) => `${v} 次` },
    { title: '累计时长', dataIndex: 'accum_duration', key: 'accum_duration', render: (v: number) => `${v.toFixed(1)} h` },
    { title: '累计电量', dataIndex: 'accum_kwh', key: 'accum_kwh', render: (v: number) => `${v.toFixed(1)} 度` },
  ];

  const onlineCount = piles.filter(p => p.status === 'ONLINE').length;
  const faultCount = piles.filter(p => p.status === 'FAULT').length;
  const totalQueue = piles.reduce((s, p) => s + p.queue_size, 0);
  const totalKwh = piles.reduce((s, p) => s + p.accum_kwh, 0);

  return (
    <div>
      <Card
        className="interactive-card page-enter"
        style={{ borderRadius: 16, marginBottom: 24, boxShadow: '0 4px 18px rgba(26,61,124,0.1)', overflow: 'hidden' }}
      >
        <Row align="middle" gutter={[24, 16]}>
          <Col xs={24} md={10}>
            <Space direction="vertical" size={8}>
              <span style={{ fontSize: 22, fontWeight: 800, color: '#1a3d7c' }}>运营调度总览</span>
              <span style={{ color: '#666' }}>管理员端对应 UC10-UC14，集中查看桩状态、队列、报表与调度策略。</span>
            </Space>
          </Col>
          <Col xs={24} md={14}>
            <img src="/illustrations/station-map.svg" alt="充电站运营布局" style={{ width: '100%' }} />
          </Col>
        </Row>
      </Card>

      <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
        <Col span={6} className="stagger-card">
          <Card className="interactive-card" style={{ borderRadius: 12, borderTop: '3px solid #52c41a', boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
            <Statistic
              title="在线桩数"
              value={onlineCount}
              suffix={`/ ${piles.length}`}
              valueStyle={{ color: '#52c41a' }}
              prefix={<DashboardOutlined />}
            />
          </Card>
        </Col>
        <Col span={6} className="stagger-card">
          <Card className="interactive-card" style={{ borderRadius: 12, borderTop: '3px solid #1890ff', boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
            <Statistic
              title="排队车辆"
              value={totalQueue}
              suffix="辆"
              valueStyle={{ color: '#1890ff' }}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6} className="stagger-card">
          <Card className="interactive-card" style={{ borderRadius: 12, borderTop: faultCount > 0 ? '3px solid #ff4d4f' : '3px solid #d9d9d9', boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
            <Statistic
              title="故障桩数"
              value={faultCount}
              valueStyle={{ color: faultCount > 0 ? '#ff4d4f' : '#999' }}
              prefix={<FireOutlined />}
            />
          </Card>
        </Col>
        <Col span={6} className="stagger-card">
          <Card className="interactive-card" style={{ borderRadius: 12, borderTop: '3px solid #faad14', boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
            <Statistic
              title="累计充电量"
              value={totalKwh.toFixed(1)}
              suffix="度"
              valueStyle={{ color: '#faad14' }}
              prefix={<ThunderboltOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card
        title={<Space><DashboardOutlined />充电桩状态概览</Space>}
        extra={<Button onClick={fetchPiles} loading={loading}>刷新</Button>}
        className="interactive-card page-enter"
        style={{ borderRadius: 12, boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}
      >
        <Table
          dataSource={piles}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={false}
          size="middle"
        />
      </Card>
    </div>
  );
}
