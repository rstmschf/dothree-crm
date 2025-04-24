import { Outlet, useLocation, Link } from 'react-router-dom';
import { useState, useEffect } from 'react';

function Layout() {
  const location = useLocation();
  const [fullName, setFullName] = useState('');
  const [isTgLoading, setIsTgLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setFullName(payload.full_name || 'User');
      } catch (e) {
        console.error("Could not parse JWT token.");
      }
    }
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = '/login';
  };

  const handleTelegramLinkClick = async () => {
    const token = localStorage.getItem('access');
    if (!token) return;

    setIsTgLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/accounts/telegram/link/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.telegram_link) {
          window.open(data.telegram_link, '_blank');
        }
      } else {
        console.error('Telegram link connection error:', response.status);
      }
    } catch (error) {
      console.error('Network error:', error);
    } finally {
      setIsTgLoading(false);
    }
  };

  return (
    <div className="drawer lg:drawer-open">
      <input id="my-drawer-2" type="checkbox" className="drawer-toggle" />

      <div className="drawer-content flex flex-col bg-base-200 min-h-screen">
        <div className="navbar bg-base-100 border-b border-base-300 px-4">
          <div className="flex-none lg:hidden">
            <label htmlFor="my-drawer-2" className="btn btn-square btn-ghost">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="inline-block w-6 h-6 stroke-current"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
            </label>
          </div>
          <div className="flex-1">
            <span className="text-xl font-bold lg:hidden">My CRM</span>
          </div>

          <div className="flex-none flex items-center gap-2">
            <button 
              className="btn btn-sm btn-ghost normal-case text-base"
              onClick={handleTelegramLinkClick}
              disabled={isTgLoading}
            >
              {isTgLoading ? (
                <span className="loading loading-spinner loading-sm"></span>
              ) : (
                fullName
              )}
            </button>

            <button onClick={handleLogout} className="btn btn-sm btn-outline btn-error">
              Logout
            </button>
          </div>

        </div>

        <div className="p-6">
          <Outlet />
        </div>
      </div>

      <div className="drawer-side border-r border-base-300 z-50">
        <label htmlFor="my-drawer-2" aria-label="close sidebar" className="drawer-overlay"></label>
        <ul className="menu p-4 w-64 min-h-full bg-base-100 text-base-content">
          <li className="mb-6 mt-2">
            <Link to="/" className={location.pathname === '/' ? 'active' : ''}><span className="text-2xl font-bold text-primary">Dothree</span></Link>
          </li>
          <li>
            <Link to="/" className={location.pathname === '/' ? 'active' : ''}>Overview</Link>
          </li>
          <li>
            <Link to="/contacts" className={location.pathname === '/contacts' ? 'active' : ''}>Contacts</Link>
          </li>
          <li>
            <Link to="/companies" className={location.pathname === '/companies' ? 'active' : ''}>Companies</Link>
          </li>
          <li>
            <Link to="/deals" className={location.pathname === '/deals' ? 'active' : ''}>Deals</Link>
          </li>
        </ul>
      </div>
    </div>
  );
}

export default Layout;