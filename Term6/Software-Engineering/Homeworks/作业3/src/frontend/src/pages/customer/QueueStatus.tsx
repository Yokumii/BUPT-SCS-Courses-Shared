import { useEffect, useState } from 'react';
import { Card, Descriptions, Statistic, Button, Space, Tag, Row, Col, Empty } from 'antd';
import { SyncOutlined, ThunderboltOutlined, ClockCircleOutlined, CarOutlined } from '@ant-design/icons';
import { viewQueueNumber, viewWaitingCount } from '../../api';

export default function QueueStatus() {
  const [queueInfo, setQueueInfo] = useState<any>(null);
  const [waitingCount, setWaitingCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const refresh = async () => {
    setLoading(true);
    try {
      const qRes = await viewQueueNumber();
      setQueueInfo(qRes.data);
      const wRes = await viewWaitingCount();
      setWaitingCount(wRes.data.waiting_count);
    } catch {
      setQueueInfo(null);
      setWaitingCount(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { refresh(); }, []);

  const statusConfig: Record<string, { color: string; text: string }> = {
    WAITING: { color: 'orange', text: '等候区排队中' },
    QUEUED: { color: 'blue', text: '充电区桩队列中' },
    CHARGING: { color: 'green', text: '正在充电' },
  };

  return (
    <div style={{ maxWidth: 760, margin: '0 auto' }}>
      <Row gutter={[24, 24]}>
        <Col span={24} className="page-enter">
          <Card className="interactive-card" style={{ borderRadius: 16, overflow: 'hidden' }}>
            <div style={{ background: 'linear-gradient(135deg, #1a3d7c 0%, #4a90d9 100%)', margin: -24, marginBottom: 24, padding: '32px 24px', color: '#fff' }}>
              <Space><CarOutlined style={{ fontSize: 24 }} /><span style={{ fontSize: 18, fontWeight: 600 }}>我的排队状态</span></Space>
              <Button ghost size="small" icon={<SyncOutlined spin={loading} />} onClick={refresh} style={{ float: 'right', borderColor: 'rgba(255,255,255,0.5)' }}>刷新</Button>
            </div>

            {queueInfo ? (
              <Row gutter={24}>
                <Col span={8} style={{ textAlign: 'center' }}>
                  <div style={{ width: 100, height: 100, borderRadius: '50%', background: 'linear-gradient(135deg, #e8f0fe 0%, #f5f9ff 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 12px', border: '3px solid #1a3d7c' }}>
                    <span style={{ fontSize: 28, fontWeight: 800, color: '#1a3d7c' }}>{queueInfo.code}</span>
                  </div>
                  <Tag color={statusConfig[queueInfo.status]?.color}>{statusConfig[queueInfo.status]?.text || queueInfo.status}</Tag>
                </Col>
                <Col span={16}>
                  <Descriptions column={1} size="small" bordered>
                    <Descriptions.Item label="排队号码">{queueInfo.code}</Descriptions.Item>
                    <Descriptions.Item label="充电模式"><Tag color={queueInfo.mode === 'FAST' ? 'gold' : 'green'} icon={<ThunderboltOutlined />}>{queueInfo.mode === 'FAST' ? '快充 (30度/时)' : '慢充 (10度/时)'}</Tag></Descriptions.Item>
                    <Descriptions.Item label="请求充电量">{queueInfo.kwh} 度</Descriptions.Item>
                    <Descriptions.Item label="当前状态">{queueInfo.status === 'CHARGING' ? <Tag color="green" icon={<SyncOutlined spin />}>正在充电</Tag> : <Tag color="blue" icon={<ClockCircleOutlined />}>等待中</Tag>}</Descriptions.Item>
                  </Descriptions>

                  {waitingCount !== null && (
                    <div style={{ marginTop: 16 }}>
                      <Statistic title="本充电模式下前车等待数量" value={waitingCount} suffix="辆" valueStyle={{ color: waitingCount === 0 ? '#52c41a' : '#1a3d7c', fontSize: 32 }} prefix={<CarOutlined />} />
                      {waitingCount === 0 && queueInfo.status !== 'CHARGING' && <Tag color="green" style={{ marginTop: 8 }}>即将开始充电</Tag>}
                    </div>
                  )}
                </Col>
              </Row>
            ) : (
              <Empty description="当前无活跃充电请求" image={Empty.PRESENTED_IMAGE_SIMPLE} />
            )}
          </Card>
        </Col>

        <Col span={24} className="page-enter"><Card className="interactive-card" style={{ borderRadius: 14 }}><img src="/illustrations/queue-flow.svg" alt="充电流程示意" style={{ width: '100%' }} /></Card></Col>

        <Col span={24} className="page-enter">
          <Card className="interactive-card" title="计费标准" size="small">
            <Row gutter={16}>{[
              { label: '峰时', time: '10-15, 18-21', rate: '1.0', color: '#ff4d4f' },
              { label: '平时', time: '7-10, 15-18, 21-23', rate: '0.7', color: '#faad14' },
              { label: '谷时', time: '23-次日7', rate: '0.4', color: '#52c41a' },
              { label: '服务费', time: '全时段', rate: '0.8', color: '#1890ff' },
            ].map(item => <Col span={6} key={item.label}><div style={{ textAlign: 'center', padding: '8px 0' }}><Tag color={item.color}>{item.label}</Tag><div style={{ fontSize: 18, fontWeight: 700, margin: '4px 0', color: item.color }}>¥{item.rate}/度</div><div style={{ fontSize: 11, color: '#999' }}>{item.time}</div></div></Col>)}</Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
}
