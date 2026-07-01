import { useState } from 'react';
import { Form, Input, Button, message, Typography, Space } from 'antd';
import { useNavigate, Link } from 'react-router-dom';
import { UserOutlined, LockOutlined, PhoneOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { register } from '../../api';

const { Title, Text } = Typography;

export default function Register() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values: { username: string; password: string; phone?: string }) => {
    setLoading(true);
    try {
      await register(values.username, values.password, values.phone);
      message.success('注册成功，请登录');
      navigate('/login');
    } catch (err: any) {
      message.error(err.response?.data?.detail || '注册失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex', minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f2744 0%, #1a3d7c 40%, #2d5dab 100%)',
    }}>
      {/* Left branding */}
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column',
        justifyContent: 'center', alignItems: 'center', padding: 48,
        position: 'relative', overflow: 'hidden',
      }}>
        <div className="hero-orb" style={{ width: 170, height: 170, left: 72, top: 70 }} />
        <div className="hero-orb" style={{ width: 110, height: 110, right: 92, bottom: 86 }} />
        <div className="animate__animated animate__fadeInLeft" style={{ textAlign: 'center', maxWidth: 470, position: 'relative', zIndex: 1 }}>
          <img
            src="/bupt_logo.png"
            alt="BUPT"
            style={{
              width: 76, height: 76, borderRadius: 18,
              background: '#fff', padding: 8,
              boxShadow: '0 8px 24px rgba(0,0,0,0.22)',
              marginBottom: 18,
            }}
          />
          <Title level={2} style={{ color: '#fff', marginBottom: 8 }}>
            加入智能充电服务
          </Title>
          <Text style={{ color: 'rgba(255,255,255,0.72)', fontSize: 15 }}>
            从申请充电、排队调度到自动计费，覆盖完整用户流程
          </Text>
          <img
            className="floating-illustration"
            src="/illustrations/charging-hero.svg"
            alt="智能充电站插图"
            style={{ width: '100%', maxWidth: 410, marginTop: 24, filter: 'drop-shadow(0 18px 26px rgba(0,0,0,0.22))' }}
          />
          <div style={{ marginTop: 18 }}>
            <Space direction="vertical" size={12} style={{ textAlign: 'left' }}>
              {['快充 30 度/时，慢充 10 度/时', '峰平谷分时计费，详单可追溯', '排队号与前车数随时查看'].map(text => (
                <div key={text} className="stagger-card soft-panel" style={{ color: '#1f2937', fontSize: 14, padding: '10px 14px', borderRadius: 14 }}>
                  <ThunderboltOutlined style={{ color: '#faad14', marginRight: 8 }} />
                  {text}
                </div>
              ))}
            </Space>
          </div>
        </div>
      </div>

      {/* Right form */}
      <div style={{
        width: 440, display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: '#fff', borderRadius: '24px 0 0 24px',
        boxShadow: '-8px 0 32px rgba(0,0,0,0.2)',
      }}>
        <div className="animate__animated animate__fadeInRight" style={{ width: 320, padding: '40px 0' }}>
          <div style={{ marginBottom: 36 }}>
            <Title level={3} style={{ marginBottom: 4, color: '#1a3d7c' }}>创建账户</Title>
            <Text type="secondary">填写信息注册充电桩服务</Text>
          </div>

          <Form layout="vertical" onFinish={onFinish} size="large">
            <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
              <Input
                prefix={<UserOutlined style={{ color: '#bbb' }} />}
                placeholder="用户名"
                style={{ borderRadius: 8, height: 44 }}
              />
            </Form.Item>
            <Form.Item name="password" rules={[{ required: true, min: 6, message: '密码至少 6 位' }]}>
              <Input.Password
                prefix={<LockOutlined style={{ color: '#bbb' }} />}
                placeholder="密码（至少6位）"
                style={{ borderRadius: 8, height: 44 }}
              />
            </Form.Item>
            <Form.Item name="phone">
              <Input
                prefix={<PhoneOutlined style={{ color: '#bbb' }} />}
                placeholder="手机号（选填）"
                style={{ borderRadius: 8, height: 44 }}
              />
            </Form.Item>
            <Form.Item style={{ marginBottom: 16 }}>
              <Button
                type="primary" htmlType="submit" loading={loading} block
                style={{
                  height: 44, borderRadius: 8, fontSize: 15, fontWeight: 600,
                  background: 'linear-gradient(135deg, #1a3d7c 0%, #2d5dab 100%)',
                  border: 'none', boxShadow: '0 4px 12px rgba(26,61,124,0.3)',
                }}
              >
                注 册
              </Button>
            </Form.Item>
            <div style={{ textAlign: 'center' }}>
              <Text type="secondary">已有账号？</Text>
              <Link to="/login" style={{ marginLeft: 4 }}>去登录</Link>
            </div>
          </Form>
        </div>
      </div>
    </div>
  );
}
