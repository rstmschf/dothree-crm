import { useState, useEffect } from 'react';
import api from '../api';
import { Link } from 'react-router-dom';

function Companies() {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [copiedPhoneId, setCopiedPhoneId] = useState(null);

  const [modalMode, setModalMode] = useState('add'); 
  const [currentId, setCurrentId] = useState(null);
  const [formData, setFormData] = useState({
    name: '', industry: '', phone: '', website: '', owner_name: ''
  });

  useEffect(() => {
    const token = localStorage.getItem('access');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (payload.role === 'admin' || payload.role === 'manager') setIsAdmin(true);
      } catch (e) {}
    }
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    try {
      const response = await api.get('clients/companies/');
      setCompanies(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load companies.');
      setLoading(false);
    }
  };

  const handleCopyPhone = (id, phone) => {
    if (!phone) return;
    navigator.clipboard.writeText(phone);
    setCopiedPhoneId(id);
    setTimeout(() => setCopiedPhoneId(null), 2000); 
  };

  const openAddModal = () => {
    setModalMode('add');
    setFormData({ name: '', industry: '', phone: '', website: '', owner_name: 'Auto-assigned on save' });
    document.getElementById('company_modal').showModal();
  };

  const openEditModal = (company) => {
    setModalMode('edit');
    setCurrentId(company.id);
    setFormData({
      name: company.name || '', industry: company.industry || '',
      phone: company.phone || '', website: company.website || '',
      owner_name: company.owner_name || 'N/A'
    });
    document.getElementById('company_modal').showModal();
  };

  const handleFormChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const { owner_name, ...dataToSend } = formData; 
      if (modalMode === 'add') {
        const response = await api.post('clients/companies/', dataToSend);
        setCompanies([...companies, response.data]); 
      } else {
        const response = await api.put(`clients/companies/${currentId}/`, dataToSend);
        setCompanies(companies.map(c => c.id === currentId ? response.data : c));
      }
      document.getElementById('company_modal').close();
    } catch (err) { alert("Failed to save company."); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this company?")) return;
    try {
      await api.delete(`clients/companies/${id}/`);
      setCompanies(companies.filter(c => c.id !== id)); 
    } catch (err) { alert("Failed to delete company."); }
  };

  return (
    <>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-3xl font-bold">Companies</h1>
        <button onClick={openAddModal} className="btn btn-primary">+ New Company</button>
      </div>

      <div className="bg-base-100 rounded-box shadow p-6">
        {loading && <div className="flex justify-center p-4"><span className="loading loading-spinner loading-lg text-primary"></span></div>}
        {error && <div className="alert alert-error">{error}</div>}

        {!loading && !error && (
          <div className="overflow-x-auto">
            <table className="table table-zebra w-full">
              <thead>
                <tr>
                  <th>Company Name</th>
                  <th>Industry</th>
                  <th>Website</th>
                  <th>Manager</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {companies.length === 0 ? (
                  <tr><td colSpan="6" className="text-center">No companies found.</td></tr>
                ) : (
                  companies.map((company) => (
                    <tr key={company.id}>
                      <td className="font-bold">
                        <Link to={`/companies/${company.id}/deals`} className="link link-hover link-primary">
                          {company.name}
                        </Link>
                      </td>
                      <td>{company.industry || 'N/A'}</td>
                      <td>
                        {company.website ? (
                          <a href={company.website.startsWith('http') ? company.website : `https://${company.website}`} target="_blank" rel="noreferrer" className="link link-primary">
                            {company.website}
                          </a>
                        ) : 'N/A'}
                      </td>
                      <td>{company.owner_name || 'N/A'}</td>
                      <td className="text-right space-x-2">
                        <button onClick={() => openEditModal(company)} className="btn btn-xs btn-outline">Edit</button>
                        {isAdmin && <button onClick={() => handleDelete(company.id)} className="btn btn-xs btn-outline btn-error">Delete</button>}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Company Modal */}
      <dialog id="company_modal" className="modal">
        <div className="modal-box w-11/12 max-w-2xl">
          <h3 className="font-bold text-lg mb-4">{modalMode === 'add' ? 'Add New Company' : 'Edit Company'}</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex space-x-4">
              <div className="form-control w-1/2">
                <label className="label"><span className="label-text">Company Name</span></label>
                <input type="text" name="name" value={formData.name} onChange={handleFormChange} className="input input-bordered w-full" required />
              </div>
              <div className="form-control w-1/2">
                <label className="label"><span className="label-text">Industry</span></label>
                <input type="text" name="industry" value={formData.industry} onChange={handleFormChange} className="input input-bordered w-full" />
              </div>
            </div>
            <div className="flex space-x-4">
              <div className="form-control w-1/2">
                <label className="label"><span className="label-text">Website</span></label>
                <input type="text" name="website" value={formData.website} onChange={handleFormChange} className="input input-bordered w-full" placeholder="www.example.com" />
              </div>
              <div className="form-control w-1/2">
                <label className="label"><span className="label-text">Manager (Owner)</span></label>
                <input type="text" name="owner_name" value={formData.owner_name} className="input input-bordered w-full bg-base-200 text-base-content/60 cursor-not-allowed" readOnly disabled />
              </div>
            </div>
            <div className="modal-action">
              <button type="button" className="btn" onClick={() => document.getElementById('company_modal').close()}>Cancel</button>
              <button type="submit" className="btn btn-primary">Save</button>
            </div>
          </form>
        </div>
        <form method="dialog" className="modal-backdrop"><button>close</button></form>
      </dialog>
    </>
  );
}

export default Companies;