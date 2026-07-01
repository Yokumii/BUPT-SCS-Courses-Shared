import { useEffect, useState } from 'react';
import { Card, Table, Button, Space, Select, Modal, message, Tag, Row, Col, Divider } from 'antd';
import { SettingOutlined, ThunderboltOutlined, ExclamationCircleOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { viewAllPileStatus, togglePile, viewQueuingVehicles, setSchedulingPolicy, reportFault, reportRecovery } from '../../api';

export default function PileManage() {
  const [piles, setPiles] = useState<any[]>([]);
  const [queueData, setQueueData] = useState<any[]>([]);
  const [queueModalVisible, setQueueModalVisible] = useState(false);
  const [selectedPile, setSelectedPile] = useState<string>('');
  const [faultStrategy, setFaultStrategy] = useState<string>('PRIORITY');

  const fetchPiles = async () => {
    try {
      const res = await viewAllPileStatus();
      setPiles(res.data);
    } catch {}
  };

  useEffect(() => { fetchPiles(); }, []);

  const handleToggle = async (pileId: number, currentStatus: string) => {
    const action = currentStatus === 'ONLINE' ? 'STOP' : 'START';
    try {
      await togglePile(pileId, action);
      message.success(`充电桩已${action === 'START' ? '启动' : '关闭'}`);
      fetchPiles();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '操作失败');
    }
  };

  const handleViewQueue = async (pileId: number, pileName: string) => {
    try {
      const res = await viewQueuingVehicles(pileId);
      setQueueData(res.data);
      setSelectedPile(pileName);
      setQueueModalVisible(true);
    } catch (err: any) {
      message.error(err.response?.data?.detail || '获取失败');
    }
  };

  const handlePolicyChange = async (mode: string) => {
    try {
      await setSchedulingPolicy(mode);
      message.success(`调度策略已切换为 ${mode}`);
    } catch (err: any) {
      message.error(err.response?.data?.detail || '切换失败');
    }
  };

  const handleFault = async (pileId: number) => {
    try {
      await reportFault(pileId, faultStrategy);
      message.warning(`已上报故障，采用${faultStrategy === 'PRIORITY' ? '优先级调度' : '时间顺序调度'}`);
      fetchPiles();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '上报失败');
    }
  };

  const handleRecover = async (pileId: number) => {
    try {
      await reportRecovery(pileId);
      message.success('故障已恢复并完成同类型队列重调度');
      fetchPiles();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '恢复失败');
    }
  };

  const statusConfig: Record<string, { color: string; label: string }> = {
    ONLINE: { color: 'green', label: '运行中' },
    OFFLINE: { color: 'default', label: '已关闭' },
    FAULT: { color: 'red', label: '故障' },
  };

  const columns = [
    { title: '充电桩编号', dataIndex: 'name', key: 'name', render: (v: string) => <span style={{ fontWeight: 600, fontSize: 15 }}>{v}</span> },
    { title: '类型', dataIndex: 'pile_type', key: 'pile_type', render: (v: string) => <Tag color={v === 'FAST' ? 'gold' : 'green'}>{v === 'FAST' ? '快充' : '慢充'}</Tag> },
    { title: '功率', dataIndex: 'power', key: 'power', render: (v: number) => `${v} 度/小时` },
    { title: '当前状态', dataIndex: 'status', key: 'status', render: (v: string) => <Tag color={statusConfig[v]?.color}>{statusConfig[v]?.label}</Tag> },
    {
      title: '当前占用车辆', key: 'current_vehicle', width: 210,
      render: (_: any, record: any) => record.current_user_id ? (
        <Space direction="vertical" size={2}>
          <span><Tag color="green">充电中</Tag>{record.current_username} (ID: {record.current_user_id})</span>
          <span style={{ color: '#666', fontSize: 12 }}>排队号 {record.current_queue_code} · 请求 {record.current_requested_kwh} 度</span>
        </Space>
      ) : <Tag color="default">空闲/未占用</Tag>
    },
    { title: '等待车辆数', dataIndex: 'queue_size', key: 'queue_size', render: (v: number) => `${v} 辆` },
    { title: '累计充电次数', dataIndex: 'accum_charge_count', key: 'accum_charge_count', render: (v: number) => `${v} 次` },
    { title: '累计充电总时长', dataIndex: 'accum_duration', key: 'accum_duration', render: (v: number) => `${v.toFixed(2)} 小时` },
    { title: '累计充电总电量', dataIndex: 'accum_kwh', key: 'accum_kwh', render: (v: number) => `${v.toFixed(2)} 度` },
    {
      title: '操作', key: 'actions', width: 330,
      render: (_: any, record: any) => (
        <Space size={4} wrap>
          <Button size="small" type={record.status === 'ONLINE' ? 'default' : 'primary'} onClick={() => handleToggle(record.id, record.status)}>{record.status === 'ONLINE' ? '关闭' : '启动'}</Button>
          <Button size="small" onClick={() => handleViewQueue(record.id, record.name)}>队列详情</Button>
          {record.status === 'ONLINE' && <Button size="small" danger icon={<ExclamationCircleOutlined />} onClick={() => handleFault(record.id)}>模拟故障</Button>}
          {record.status === 'FAULT' && <Button size="small" type="primary" icon={<CheckCircleOutlined />} onClick={() => handleRecover(record.id)}>恢复</Button>}
        </Space>
      ),
    },
  ];

  const queueColumns = [
    { title: '用户ID', dataIndex: 'user_id', key: 'user_id', width: 90 },
    { title: '用户名', dataIndex: 'username', key: 'username' },
    { title: '车辆电池总容量', dataIndex: 'battery_capacity', key: 'battery_capacity', render: (v: number) => v ? `${v} 度` : '未填写' },
    { title: '请求充电量', dataIndex: 'requested_kwh', key: 'requested_kwh', render: (v: number) => `${v} 度` },
    { title: '排队号', dataIndex: 'queue_code', key: 'queue_code', render: (v: string) => <Tag color="blue">{v}</Tag> },
    { title: '排队时长', dataIndex: 'waiting_duration', key: 'waiting_duration' },
  ];

  return (
    <div>
      <Card className="interactive-card page-enter" style={{ borderRadius: 16, marginBottom: 24 }}>
        <Row align="middle" gutter={[24, 16]}>
          <Col xs={24} md={15}><Space direction="vertical" size={8}><span style={{ fontSize: 20, fontWeight: 800, color: '#1a3d7c' }}>调度策略说明</span><span style={{ color: '#666' }}>BASELINE：单车最短完成时间；MIN_SINGLE：多空位同时叫号，总完成时长最短；MIN_BATCH：满站批量调度，不区分快慢充桩类型。</span></Space></Col>
          <Col xs={24} md={9}><img src="/illustrations/queue-flow.svg" alt="调度流程示意" style={{ width: '100%' }} /></Col>
        </Row>
      </Card>

      <Card title={<Space><SettingOutlined />充电桩管理</Space>} extra={<Space wrap><span style={{ color: '#666', fontSize: 13 }}>调度策略:</span><Select defaultValue="BASELINE" style={{ width: 180 }} onChange={handlePolicyChange}><Select.Option value="BASELINE">基线调度</Select.Option><Select.Option value="MIN_SINGLE">单次最短调度</Select.Option><Select.Option value="MIN_BATCH">批量最短调度</Select.Option></Select><span style={{ color: '#666', fontSize: 13 }}>故障重调度:</span><Select value={faultStrategy} style={{ width: 170 }} onChange={setFaultStrategy}><Select.Option value="PRIORITY">优先级调度</Select.Option><Select.Option value="TIME_ORDER">时间顺序调度</Select.Option></Select><Divider type="vertical" /><Button onClick={fetchPiles}>刷新</Button></Space>} className="interactive-card page-enter">
        <Table dataSource={piles} columns={columns} rowKey="id" pagination={false} size="middle" scroll={{ x: 1420 }} />
      </Card>

      <Modal title={<Space><ThunderboltOutlined />{selectedPile} 等候服务车辆信息</Space>} open={queueModalVisible} onCancel={() => setQueueModalVisible(false)} footer={null} width={860}>
        {queueData.length > 0 ? <Table dataSource={queueData} columns={queueColumns} rowKey="queue_code" pagination={false} size="small" /> : <div style={{ textAlign: 'center', padding: 32, color: '#999' }}>当前无排队车辆</div>}
      </Modal>
    </div>
  );
}
