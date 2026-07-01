import { useEffect, useState } from 'react';
import { Card, Form, Select, InputNumber, Button, message, Descriptions, Space, Tag, Row, Col, Statistic, Alert } from 'antd';
import { ThunderboltOutlined, ClockCircleOutlined, CheckCircleOutlined, SyncOutlined } from '@ant-design/icons';
import { submitChargingRequest, modifyMode, modifyAmount, cancelCharging, viewQueueNumber, endCharging, getMe, advanceDemoTime } from '../../api';

export default function ChargingRequest() {
  const [loading, setLoading] = useState(false);
  const [activeRequest, setActiveRequest] = useState<any>(null);
  const [newKwh, setNewKwh] = useState<number | null>(null);
  const [balance, setBalance] = useState<number>(0);

  const fetchBalance = async () => {
    try {
      const res = await getMe();
      setBalance(res.data.balance || 0);
    } catch {
      setBalance(0);
    }
  };

  const fetchStatus = async () => {
    try {
      const res = await viewQueueNumber();
      setActiveRequest(res.data);
      setNewKwh(res.data.kwh);
    } catch {
      setActiveRequest(null);
    }
  };

  useEffect(() => { fetchBalance(); fetchStatus(); }, []);

  const onSubmit = async (values: { mode: string; kwh: number }) => {
    if (balance <= 0) {
      message.warning('账户余额不足，请先充值');
      return;
    }
    setLoading(true);
    try {
      const res = await submitChargingRequest(values.mode, values.kwh);
      message.success(`充电请求已提交，排队号: ${res.data.queue_code}`);
      setActiveRequest(res.data);
      setNewKwh(values.kwh);
      fetchStatus();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '提交失败');
    } finally {
      setLoading(false);
    }
  };

  const onModifyMode = async (newMode: string) => {
    try {
      const res = await modifyMode(newMode);
      message.success(`充电模式已修改，新排队号: ${res.data.queue_code}`);
      fetchStatus();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '修改失败');
    }
  };

  const onModifyAmount = async () => {
    if (!newKwh || newKwh <= 0) {
      message.warning('请输入有效充电量');
      return;
    }
    try {
      await modifyAmount(newKwh);
      message.success('请求充电量已修改，排队号保持不变');
      fetchStatus();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '修改失败');
    }
  };

  const onCancel = async () => {
    try {
      await cancelCharging();
      message.success('充电已取消');
      setActiveRequest(null);
    } catch (err: any) {
      message.error(err.response?.data?.detail || '取消失败');
    }
  };

  const onEnd = async () => {
    try {
      const res = await endCharging();
      message.success(`充电结束，费用: ¥${res.data.total_fee}`);
      fetchBalance();
      setActiveRequest(null);
    } catch (err: any) {
      message.error(err.response?.data?.detail || '结束失败');
    }
  };

  const onAdvanceTime = async (minutes: number) => {
    try {
      const res = await advanceDemoTime(minutes);
      setBalance(res.data.balance || 0);
      if (res.data.generated_count > 0) {
        message.success(`已快进 ${minutes} 分钟，生成详单 ${res.data.bill_ids.map((id: number) => `#${id}`).join(', ')}，余额已更新`);
      } else {
        message.success(`已快进 ${minutes} 分钟，当前模拟时间: ${res.data.current_time.slice(0, 19).replace('T', ' ')}`);
      }
      fetchStatus();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '快进失败');
    }
  };

  const statusConfig: Record<string, { color: string; icon: React.ReactNode; text: string }> = {
    WAITING: { color: 'orange', icon: <ClockCircleOutlined />, text: '等候区排队中' },
    QUEUED: { color: 'blue', icon: <SyncOutlined spin />, text: '充电区桩队列中' },
    CHARGING: { color: 'green', icon: <ThunderboltOutlined />, text: '正在充电' },
    ENDED: { color: 'default', icon: <CheckCircleOutlined />, text: '已完成' },
    CANCELLED: { color: 'red', icon: null, text: '已取消' },
  };

  return (
    <div style={{ maxWidth: 960, margin: '0 auto' }}>
      <Row gutter={[24, 24]}>
        <Col span={8} className="stagger-card">
          <Card className="interactive-card" style={{ textAlign: 'center' }}>
            <Statistic title="快充电桩" value={3} suffix="台" prefix={<ThunderboltOutlined style={{ color: '#faad14' }} />} />
            <Tag color="gold" style={{ marginTop: 8 }}>30 度/时 · 排队号 F 开头</Tag>
          </Card>
        </Col>
        <Col span={8} className="stagger-card">
          <Card className="interactive-card" style={{ textAlign: 'center' }}>
            <Statistic title="慢充电桩" value={2} suffix="台" prefix={<ThunderboltOutlined style={{ color: '#52c41a' }} />} />
            <Tag color="green" style={{ marginTop: 8 }}>10 度/时 · 排队号 T 开头</Tag>
          </Card>
        </Col>
        <Col span={8} className="stagger-card">
          <Card className="interactive-card" style={{ textAlign: 'center' }}>
            <Statistic title="账户余额" value={balance} precision={2} prefix="¥" valueStyle={{ color: balance > 0 ? '#52c41a' : '#ff4d4f' }} />
            <Tag color={balance > 0 ? 'green' : 'red'} style={{ marginTop: 8 }}>{balance > 0 ? '可提交充电请求' : '余额不足，请先充值'}</Tag>
          </Card>
        </Col>

        <Col span={24} className="page-enter">
          <Card className="interactive-card" style={{ borderRadius: 16, overflow: 'hidden' }}>
            <Row align="middle" gutter={[24, 16]}>
              <Col xs={24} md={13}>
                <Space direction="vertical" size={8}>
                  <span style={{ color: '#1a3d7c', fontSize: 20, fontWeight: 700 }}>提交或修改充电请求</span>
                  <span style={{ color: '#666' }}>等候区可修改充电模式和充电量；进入充电区后不可修改，可取消后重新排队。</span>
                </Space>
              </Col>
              <Col xs={24} md={11} style={{ textAlign: 'right' }}>
                <img src="/illustrations/station-map.svg" alt="充电站布局示意" style={{ width: '100%', maxWidth: 360 }} />
              </Col>
            </Row>
          </Card>
        </Col>

        <Col span={24} className="page-enter">
          <Card title={<Space><ThunderboltOutlined />提交充电请求</Space>} className="interactive-card">
            <Alert type={balance > 0 ? 'info' : 'warning'} showIcon style={{ marginBottom: 16 }} message={balance > 0 ? '等候区容量和充电桩队列容量由系统参数控制；提交后系统会根据最短完成时长策略自动叫号。' : '当前余额小于等于 0，后端会拒绝提交充电请求，请先到账户充值页充值。'} />
            <Form layout="inline" onFinish={onSubmit} style={{ gap: 12 }}>
              <Form.Item name="mode" label="充电模式" rules={[{ required: true, message: '请选择' }]}>
                <Select style={{ width: 150 }} placeholder="选择模式">
                  <Select.Option value="FAST">快充 FAST</Select.Option>
                  <Select.Option value="TRICKLE">慢充 TRICKLE</Select.Option>
                </Select>
              </Form.Item>
              <Form.Item name="kwh" label="本次请求充电量" rules={[{ required: true, message: '请输入' }]}>
                <InputNumber min={1} max={200} placeholder="度" addonAfter="度" style={{ width: 160 }} />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit" loading={loading} disabled={balance <= 0}>提交请求</Button>
              </Form.Item>
              <Form.Item>
                <Button onClick={fetchStatus}>刷新当前请求</Button>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        {activeRequest && (
          <Col span={24}>
            <Card title={<Space><SyncOutlined spin={activeRequest.status === 'CHARGING'} />当前充电请求</Space>} className={`interactive-card ${activeRequest.status === 'CHARGING' ? 'pulse-charging' : ''}`}>
              <Descriptions column={3} bordered size="small">
                <Descriptions.Item label="排队号"><span style={{ fontSize: 18, fontWeight: 700, color: '#1a3d7c' }}>{activeRequest.code || activeRequest.queue_code}</span></Descriptions.Item>
                <Descriptions.Item label="状态"><Tag color={statusConfig[activeRequest.status]?.color} icon={statusConfig[activeRequest.status]?.icon}>{statusConfig[activeRequest.status]?.text}</Tag></Descriptions.Item>
                <Descriptions.Item label="充电模式"><Tag color={activeRequest.mode === 'FAST' ? 'gold' : 'green'}>{activeRequest.mode === 'FAST' ? '快充' : '慢充'}</Tag></Descriptions.Item>
                <Descriptions.Item label="请求充电量">{activeRequest.kwh ?? '-'} 度</Descriptions.Item>
                <Descriptions.Item label="修改规则" span={2}>{activeRequest.status === 'WAITING' ? '当前在等候区，允许修改模式和充电量' : '已进入充电区，不允许修改请求，可取消或结束'}</Descriptions.Item>
              </Descriptions>

              {activeRequest.status === 'WAITING' && (
                <Card size="small" title="等候区修改请求" style={{ marginTop: 16 }}>
                  <Space wrap>
                    <Button onClick={() => onModifyMode(activeRequest.mode === 'FAST' ? 'TRICKLE' : 'FAST')}>切换为{activeRequest.mode === 'FAST' ? '慢充' : '快充'}并重新取号</Button>
                    <InputNumber min={1} max={200} value={newKwh ?? activeRequest.kwh} onChange={(v) => setNewKwh(v)} addonAfter="度" />
                    <Button onClick={onModifyAmount}>修改充电量（排队号不变）</Button>
                  </Space>
                </Card>
              )}

              <Card size="small" title="演示时间快进" style={{ marginTop: 16 }}>
                <Space wrap>
                  <Button onClick={() => onAdvanceTime(10)}>快进 10 分钟</Button>
                  <Button onClick={() => onAdvanceTime(30)}>快进 30 分钟</Button>
                  <Button onClick={() => onAdvanceTime(60)}>快进 1 小时</Button>
                  <span style={{ color: '#999' }}>用于快速触发充满或余额耗尽强制退出</span>
                </Space>
              </Card>

              <Space style={{ marginTop: 16 }}>
                {activeRequest.status === 'CHARGING' && <Button type="primary" onClick={onEnd}>结束充电</Button>}
                <Button danger onClick={onCancel}>取消充电</Button>
                <Button onClick={() => { fetchStatus(); fetchBalance(); }}>刷新状态</Button>
              </Space>
            </Card>
          </Col>
        )}
      </Row>
    </div>
  );
}
