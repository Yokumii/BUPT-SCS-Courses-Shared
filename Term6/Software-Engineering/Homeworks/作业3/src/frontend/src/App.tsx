import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import Login from './pages/customer/Login';
import Register from './pages/customer/Register';
import ChargingRequest from './pages/customer/ChargingRequest';
import QueueStatus from './pages/customer/QueueStatus';
import BillHistory from './pages/customer/BillHistory';
import Recharge from './pages/customer/Recharge';
import Dashboard from './pages/admin/Dashboard';
import PileManage from './pages/admin/PileManage';
import Report from './pages/admin/Report';
import AppLayout from './components/AppLayout';

type Role = 'CUSTOMER' | 'ADMINISTRATOR';

function ProtectedRoute({ children, requiredRole }: { children: React.ReactNode; requiredRole: Role }) {
  const token = sessionStorage.getItem('token');
  const role = sessionStorage.getItem('role') as Role | null;
  if (!token) return <Navigate to="/login" replace />;
  if (role !== requiredRole) {
    return <Navigate to={role === 'ADMINISTRATOR' ? '/admin/dashboard' : '/customer/charging'} replace />;
  }
  return <AppLayout>{children}</AppLayout>;
}

function App() {
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#1a3d7c',
          colorLink: '#2d5dab',
          borderRadius: 8,
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif',
        },
        components: {
          Card: { borderRadiusLG: 12 },
          Button: { borderRadius: 6 },
        }
      }}
    >
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/customer/charging" element={<ProtectedRoute requiredRole="CUSTOMER"><ChargingRequest /></ProtectedRoute>} />
          <Route path="/customer/queue" element={<ProtectedRoute requiredRole="CUSTOMER"><QueueStatus /></ProtectedRoute>} />
          <Route path="/customer/bills" element={<ProtectedRoute requiredRole="CUSTOMER"><BillHistory /></ProtectedRoute>} />
          <Route path="/customer/recharge" element={<ProtectedRoute requiredRole="CUSTOMER"><Recharge /></ProtectedRoute>} />
          <Route path="/admin/dashboard" element={<ProtectedRoute requiredRole="ADMINISTRATOR"><Dashboard /></ProtectedRoute>} />
          <Route path="/admin/piles" element={<ProtectedRoute requiredRole="ADMINISTRATOR"><PileManage /></ProtectedRoute>} />
          <Route path="/admin/report" element={<ProtectedRoute requiredRole="ADMINISTRATOR"><Report /></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
