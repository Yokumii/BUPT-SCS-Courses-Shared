import { useState } from 'react';
import { Form, Input, Button, message, Space, Typography } from 'antd';
import { useNavigate, Link } from 'react-router-dom';
import { UserOutlined, LockOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { login } from '../../api';

const { Title, Text } = Typography;

export default function Login() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      const res = await login(values.username, values.password);
      const data = res.data;
      sessionStorage.setItem('token', data.access_token);
      sessionStorage.setItem('userId', String(data.user_id));
      sessionStorage.setItem('username', data.username);
      sessionStorage.setItem('role', data.role);
      message.success('登录成功');
      if (data.role === 'ADMINISTRATOR') {
        navigate('/admin/dashboard');
      } else {
        navigate('/customer/charging');
      }
    } catch (err: any) {
      message.error(err.response?.data?.detail || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex', minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f2744 0%, #1a3d7c 40%, #2d5dab 100%)',
    }}>
      {/* Left branding panel */}
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column',
        justifyContent: 'center', alignItems: 'center', padding: 48,
        position: 'relative', overflow: 'hidden',
      }}>
        <div className="hero-orb" style={{ width: 180, height: 180, left: 52, top: 56 }} />
        <div className="hero-orb" style={{ width: 120, height: 120, right: 90, bottom: 82 }} />
        <div className="animate__animated animate__fadeInLeft" style={{ textAlign: 'center', maxWidth: 480, position: 'relative', zIndex: 1 }}>
          <img
            src="/bupt_logo.png"
            alt="BUPT"
            style={{
              width: 78, height: 78, borderRadius: 18,
              background: '#fff', padding: 8,
              boxShadow: '0 8px 24px rgba(0,0,0,0.22)',
              marginBottom: 18,
            }}
          />
          <Title level={2} style={{ color: '#fff', marginBottom: 8 }}>
            智能充电桩调度计费系统
          </Title>
          <Text style={{ color: 'rgba(255,255,255,0.72)', fontSize: 15 }}>
            北京邮电大学 · 软件工程课程项目
          </Text>
          <img
            className="floating-illustration"
            src="/illustrations/charging-hero.svg"
            alt="智能充电站插图"
            style={{ width: '100%', maxWidth: 430, marginTop: 24, filter: 'drop-shadow(0 18px 26px rgba(0,0,0,0.22))' }}
          />
          <div style={{ marginTop: 22 }}>
            <div style={{ display: 'flex', gap: 16, justifyContent: 'center' }}>
              {[
                { num: '5', label: '充电桩' },
                { num: '3', label: '调度策略' },
                { num: '14', label: '核心用例' },
              ].map(item => (
                <div key={item.label} className="stagger-card soft-panel" style={{ textAlign: 'center', borderRadius: 16, padding: '12px 18px', minWidth: 92 }}>
                  <div style={{ color: '#1a3d7c', fontSize: 26, fontWeight: 800 }}>{item.num}</div>
                  <div style={{ color: '#4b5563', fontSize: 12, marginTop: 4 }}>{item.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Right login form */}
      <div style={{
        width: 440, display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: '#fff', borderRadius: '24px 0 0 24px',
        boxShadow: '-8px 0 32px rgba(0,0,0,0.2)',
      }}>
        <div className="animate__animated animate__fadeInRight" style={{ width: 320, padding: '40px 0' }}>
          <div style={{ marginBottom: 36 }}>
            <Title level={3} style={{ marginBottom: 4, color: '#1a3d7c' }}>欢迎回来</Title>
            <Text type="secondary">登录您的充电桩管理账户</Text>
          </div>

          <Form layout="vertical" onFinish={onFinish} size="large">
            <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
              <Input
                prefix={<UserOutlined style={{ color: '#bbb' }} />}
                placeholder="用户名"
                style={{ borderRadius: 8, height: 44 }}
              />
            </Form.Item>
            <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
              <Input.Password
                prefix={<LockOutlined style={{ color: '#bbb' }} />}
                placeholder="密码"
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
                登 录
              </Button>
            </Form.Item>
            <div style={{ textAlign: 'center' }}>
              <Text type="secondary">还没有账号？</Text>
              <Link to="/register" style={{ marginLeft: 4 }}>立即注册</Link>
            </div>
          </Form>

          <div style={{ marginTop: 48, textAlign: 'center' }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              管理员默认账号: admin / admin123
            </Text>
          </div>
        </div>
      </div>
    </div>
  );
}
