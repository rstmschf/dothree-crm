import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DealDetails from './pages/DealDetails';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Contacts from './pages/Contacts';
import Companies from './pages/Companies';
import Deals from './pages/Deals';
import Dashboard from './pages/Dashboard';
import RelatedDeals from './pages/RelatedDeals';

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
  return (
    <BrowserRouter>
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
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;