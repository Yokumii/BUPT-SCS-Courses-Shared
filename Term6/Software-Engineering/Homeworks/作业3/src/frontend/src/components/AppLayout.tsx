import { ReactNode } from 'react';
import { Layout, Menu, Avatar, Typography, Space, Button } from 'antd';
import {
  ThunderboltOutlined, DashboardOutlined, BarChartOutlined,
  UnorderedListOutlined, WalletOutlined, FileTextOutlined,
  TeamOutlined, SettingOutlined, LogoutOutlined, UserOutlined,
  CarOutlined, BellOutlined
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

const BUPT_LOGO = '/bupt_logo.png';

interface AppLayoutProps {
  children: ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const role = sessionStorage.getItem('role');
  const username = sessionStorage.getItem('username');
  const isAdmin = role === 'ADMINISTRATOR';

  const customerMenuItems = [
    { key: '/customer/charging', icon: <ThunderboltOutlined />, label: '充电服务' },
    { key: '/customer/queue', icon: <UnorderedListOutlined />, label: '排队状态' },
    { key: '/customer/bills', icon: <FileTextOutlined />, label: '充电详单' },
    { key: '/customer/recharge', icon: <WalletOutlined />, label: '账户充值' },
  ];

  const adminMenuItems = [
    { key: '/admin/dashboard', icon: <DashboardOutlined />, label: '运营概览' },
    { key: '/admin/piles', icon: <SettingOutlined />, label: '充电桩管理' },
    { key: '/admin/report', icon: <BarChartOutlined />, label: '运营报表' },
  ];

  const menuItems = isAdmin ? adminMenuItems : customerMenuItems;

  const handleLogout = () => {
    sessionStorage.clear();
    navigate('/login');
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        width={220}
        style={{
          background: 'linear-gradient(180deg, #1a3d7c 0%, #15325f 100%)',
          boxShadow: '2px 0 12px rgba(0,0,0,0.15)',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
          zIndex: 100,
        }}
      >
        <div style={{
          padding: '20px 16px',
          textAlign: 'center',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
        }}>
          <img
            src={BUPT_LOGO}
            alt="BUPT"
            style={{
              width: 52, height: 52, borderRadius: 10,
              background: '#fff', padding: 4,
              boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
              marginBottom: 8,
            }}
            onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
          />
          <div style={{ color: '#fff', fontSize: 14, fontWeight: 600, letterSpacing: 1 }}>
            智能充电桩系统
          </div>
          <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: 11, marginTop: 4 }}>
            北京邮电大学
          </div>
        </div>

        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          onClick={({ key }) => navigate(key)}
          items={menuItems}
          style={{
            background: 'transparent',
            borderRight: 'none',
            marginTop: 12,
          }}
          theme="dark"
        />

        <div style={{
          position: 'absolute',
          bottom: 0,
          width: '100%',
          padding: '16px',
          borderTop: '1px solid rgba(255,255,255,0.1)',
        }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Space>
              <Avatar size="small" icon={<UserOutlined />} style={{ background: '#4a90d9' }} />
              <Text style={{ color: '#fff', fontSize: 13 }}>{username || '用户'}</Text>
            </Space>
            <Button
              type="text"
              icon={<LogoutOutlined />}
              onClick={handleLogout}
              style={{ color: 'rgba(255,255,255,0.65)', width: '100%', textAlign: 'left', paddingLeft: 8 }}
            >
              退出登录
            </Button>
          </Space>
        </div>
      </Sider>

      <Layout style={{ marginLeft: 220 }}>
        <Header style={{
          background: '#fff',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
          position: 'sticky',
          top: 0,
          zIndex: 50,
          height: 56,
        }}>
          <Space>
            <CarOutlined style={{ fontSize: 18, color: '#1a3d7c' }} />
            <Text strong style={{ fontSize: 16, color: '#1a3d7c' }}>
              {isAdmin ? '管理员控制台' : '用户服务中心'}
            </Text>
          </Space>
          <Space>
            <BellOutlined style={{ fontSize: 16, color: '#666', cursor: 'pointer' }} />
          </Space>
        </Header>

        <Content style={{ padding: 24, background: 'transparent' }}>
          <div className="fade-in-up">
            {children}
          </div>
        </Content>
      </Layout>
    </Layout>
  );
}
