import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster, toast } from 'react-hot-toast';
import DealDetails from './pages/DealDetails';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Contacts from './pages/Contacts';
import Companies from './pages/Companies';
import Deals from './pages/Deals';
import Dashboard from './pages/Dashboard';
import RelatedDeals from './pages/RelatedDeals';
import NotFound from './pages/NotFound';

// Route Guards
function PublicRoute({ children }) {
  const token = localStorage.getItem('access');
  if (token) return <Navigate to="/" replace />; 
  return children;
}

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('access');
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

function App() {
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socket = new WebSocket(`${protocol}//${window.location.host}/ws/notifications/`);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'reminder_alert') {
        toast(
          (t) => (
            <div className="flex flex-col gap-1">
              <span className="font-bold text-base">{data.message.title}</span>
              <span className="text-sm opacity-90">{data.message.text}</span>
            </div>
          ),
        );
      } else {
        window.dispatchEvent(new CustomEvent('ws_message', { detail: data }));
      }
    };

    return () => socket.close();
  }, []);

  return (
    <BrowserRouter>
      <Toaster /> 

      <Routes>
        {/* Public Auth Routes */}
        <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
        <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

        {/* Protected Dashboard Routes wrapped in Layout */}
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<Dashboard />} />
          <Route path="contacts" element={<Contacts />} />
          <Route path="companies" element={<Companies />} />
          <Route path="deals" element={<Deals />} />
          <Route path="deals/:id" element={<DealDetails />} />
          <Route path="companies/:id/deals" element={<RelatedDeals />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;