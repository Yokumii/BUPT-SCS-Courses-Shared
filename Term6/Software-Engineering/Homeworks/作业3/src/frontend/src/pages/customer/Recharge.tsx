import { useEffect, useState } from 'react';
import { Card, InputNumber, Button, message, Space, Statistic, Row, Col, Tag, List, Radio, Divider } from 'antd';
import { WalletOutlined, CreditCardOutlined, AlipayCircleOutlined, WechatOutlined } from '@ant-design/icons';
import { getMe, recharge } from '../../api';

export default function Recharge() {
  const [amount, setAmount] = useState<number>(100);
  const [balance, setBalance] = useState<number>(0);
  const [payMethod, setPayMethod] = useState<string>('alipay');
  const [loading, setLoading] = useState(false);
  const [records, setRecords] = useState<Array<{ amount: number; time: string; method: string }>>(
    JSON.parse(localStorage.getItem('rechargeRecords') || '[]')
  );

  const quickAmounts = [50, 100, 200, 500];

  const fetchBalance = async () => {
    try {
      const res = await getMe();
      setBalance(res.data.balance || 0);
    } catch {
      setBalance(0);
    }
  };

  useEffect(() => { fetchBalance(); }, []);

  const handleRecharge = async () => {
    if (!amount || amount <= 0) {
      message.warning('请输入有效金额');
      return;
    }
    setLoading(true);
    try {
      const res = await recharge(amount);
      setBalance(res.data.balance || 0);
      const record = {
        amount,
        time: new Date().toLocaleString('zh-CN'),
        method: payMethod === 'alipay' ? '支付宝' : payMethod === 'wechat' ? '微信支付' : '银行卡',
      };
      const newRecords = [record, ...records].slice(0, 20);
      setRecords(newRecords);
      localStorage.setItem('rechargeRecords', JSON.stringify(newRecords));
      message.success(`充值成功！当前后端余额 ¥${Number(res.data.balance || 0).toFixed(2)}`);
    } catch (err: any) {
      message.error(err.response?.data?.detail || '充值失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <Row gutter={[24, 24]}>
        <Col span={24}>
          <Card style={{ background: 'linear-gradient(135deg, #1a3d7c 0%, #4a90d9 100%)', border: 'none', borderRadius: 16, boxShadow: '0 8px 24px rgba(26, 61, 124, 0.3)' }}>
            <Row align="middle">
              <Col flex="auto">
                <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: 14, marginBottom: 8 }}><WalletOutlined /> 后端账户余额</div>
                <Statistic value={balance} precision={2} prefix="¥" valueStyle={{ color: '#fff', fontSize: 36, fontWeight: 700 }} />
                <div style={{ color: 'rgba(255,255,255,0.75)', marginTop: 8 }}>余额小于等于 0 时不能提交充电请求；充电中余额耗尽会自动结束并生成详单。</div>
              </Col>
              <Col><Button onClick={fetchBalance}>刷新余额</Button></Col>
            </Row>
          </Card>
        </Col>

        <Col span={24}>
          <Card title="账户充值" style={{ borderRadius: 12, boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
            <div style={{ marginBottom: 20 }}>
              <div style={{ marginBottom: 8, color: '#666' }}>快捷金额</div>
              <Space size={12}>{quickAmounts.map(v => <Button key={v} type={amount === v ? 'primary' : 'default'} size="large" onClick={() => setAmount(v)} style={{ width: 100, height: 44, borderRadius: 8, fontWeight: amount === v ? 600 : 400 }}>¥{v}</Button>)}</Space>
            </div>

            <div style={{ marginBottom: 20 }}>
              <div style={{ marginBottom: 8, color: '#666' }}>自定义金额</div>
              <InputNumber min={1} max={10000} value={amount} onChange={(v) => setAmount(v || 0)} prefix="¥" size="large" style={{ width: 200, borderRadius: 8 }} />
            </div>

            <Divider />

            <div style={{ marginBottom: 20 }}>
              <div style={{ marginBottom: 12, color: '#666' }}>支付方式（演示）</div>
              <Radio.Group value={payMethod} onChange={(e) => setPayMethod(e.target.value)} size="large">
                <Space direction="vertical" size={12}>
                  <Radio value="alipay" style={{ fontSize: 15 }}><AlipayCircleOutlined style={{ color: '#1677ff', fontSize: 20, marginRight: 8 }} />支付宝</Radio>
                  <Radio value="wechat" style={{ fontSize: 15 }}><WechatOutlined style={{ color: '#07c160', fontSize: 20, marginRight: 8 }} />微信支付</Radio>
                  <Radio value="card" style={{ fontSize: 15 }}><CreditCardOutlined style={{ color: '#faad14', fontSize: 20, marginRight: 8 }} />银行卡</Radio>
                </Space>
              </Radio.Group>
            </div>

            <Button type="primary" size="large" block loading={loading} onClick={handleRecharge} style={{ height: 48, borderRadius: 8, fontSize: 16, fontWeight: 600 }}>确认充值 ¥{(amount || 0).toFixed(2)}</Button>
          </Card>
        </Col>

        <Col span={24}>
          <Card title="充值记录（本机演示历史）" style={{ borderRadius: 12, boxShadow: '0 2px 12px rgba(0,0,0,0.06)' }}>
            {records.length === 0 ? <div style={{ textAlign: 'center', color: '#999', padding: 24 }}>暂无充值记录</div> : <List dataSource={records} renderItem={(item) => <List.Item><List.Item.Meta title={<span>充值 <Tag color="green">+¥{item.amount.toFixed(2)}</Tag></span>} description={`${item.time} · ${item.method}`} /></List.Item>} />}
          </Card>
        </Col>
      </Row>
    </div>
  );
}
