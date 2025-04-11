import { Outlet, useLocation, Link } from 'react-router-dom';

function Layout() {
  const location = useLocation();

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = '/login';
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
            <span className="text-xl font-bold lg:hidden">Dothree CRM</span>
          </div>
          <div className="flex-none">
            <button onClick={handleLogout} className="btn btn-sm btn-outline btn-error">Logout</button>
          </div>
        </div>

        <div className="p-8">
            <Outlet /> 
        </div>
      </div>

      <div className="drawer-side border-r border-base-300 z-50">
        <label htmlFor="my-drawer-2" aria-label="close sidebar" className="drawer-overlay"></label>
        <ul className="menu p-4 w-64 min-h-full bg-base-100 text-base-content">
          <li className="mb-6 mt-2">
            <span className="text-2xl font-bold text-primary">Dothree CRM</span>
          </li>
          <li>
            <Link to="/contacts" className={location.pathname === '/contacts' ? 'active' : ''}>Contacts</Link>
          </li>
          <li>
            <Link to="/companies" className={location.pathname === '/companies' ? 'active' : ''}>Companies</Link>
          </li>
        </ul>
      </div>
    </div>
  );
}

export default Layout;