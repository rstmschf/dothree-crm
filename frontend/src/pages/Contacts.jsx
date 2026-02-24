// src/pages/Contacts.jsx
import { useState, useEffect } from 'react';
import api from '../api';

function Contacts() {
  const [contacts, setContacts] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [copiedPhoneId, setCopiedPhoneId] = useState(null); // Tracks which phone was clicked

  const [modalMode, setModalMode] = useState('add');
  const [currentId, setCurrentId] = useState(null);
  const [formData, setFormData] = useState({
    first_name: '', last_name: '', email: '', company: '', phone: '', owner_name: ''
  });

  useEffect(() => {
    const token = localStorage.getItem('access');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (payload.role === 'admin' || payload.role === 'manager') setIsAdmin(true);
      } catch (e) { console.error("Could not parse JWT token."); }
    }
    fetchContacts();
    fetchCompanies();
  }, []);

  const fetchContacts = async () => {
    try {
      const response = await api.get('clients/contacts/');
      setContacts(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load contacts.');
      setLoading(false);
    }
  };

  const fetchCompanies = async () => {
    try {
      const response = await api.get('clients/companies/');
      setCompanies(response.data);
    } catch (err) { console.error("Error fetching companies:", err); }
  };

  // Auto-Copy Phone Function
  const handleCopyPhone = (id, phone) => {
    if (!phone) return;
    navigator.clipboard.writeText(phone);
    setCopiedPhoneId(id);
    // Reset the "Copied!" message after 2 seconds
    setTimeout(() => setCopiedPhoneId(null), 2000);
  };

  const openAddModal = () => {
    setModalMode('add');
    setFormData({ first_name: '', last_name: '', email: '', company: '', phone: '', owner_name: 'Auto-assigned on save' });
    document.getElementById('contact_modal').showModal();
  };

  const openEditModal = (contact) => {
    setModalMode('edit');
    setCurrentId(contact.id);
    setFormData({
      first_name: contact.first_name || '', last_name: contact.last_name || '',
      email: contact.email || '', company: contact.company || '',
      phone: contact.phone || '', owner_name: contact.owner_name || 'N/A'
    });
    document.getElementById('contact_modal').showModal();
  };

  const handleFormChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const { owner_name, ...dataToSend } = formData;
      if (modalMode === 'add') {
        const response = await api.post('clients/contacts/', dataToSend);
        setContacts([...contacts, response.data]);
      } else {
        const response = await api.put(`clients/contacts/${currentId}/`, dataToSend);
        setContacts(contacts.map(c => c.id === currentId ? response.data : c));
      }
      document.getElementById('contact_modal').close();
    } catch (err) { alert("Failed to save contact."); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this contact?")) return;
    try {
      await api.delete(`clients/contacts/${id}/`);
      setContacts(contacts.filter(c => c.id !== id));
    } catch (err) { alert("Failed to delete contact."); }
  };

  return (
    <>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Contacts</h1>
        <button onClick={openAddModal} className="btn btn-primary">+ New Contact</button>
      </div>

      <div className="bg-base-100 rounded-box shadow p-6">
        {loading && <div className="flex justify-center p-4"><span className="loading loading-spinner loading-lg text-primary"></span></div>}
        {error && <div className="alert alert-error">{error}</div>}

        {!loading && !error && (
          <div className="overflow-x-auto">
            <table className="table table-zebra w-full">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Company</th>
                  <th>Phone</th>
                  <th>Manager</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {contacts.length === 0 ? (
                  <tr><td colSpan="6" className="text-center">No contacts found.</td></tr>
                ) : (
                  contacts.map((contact) => (
                    <tr key={contact.id}>
                      <td className="font-medium">{contact.first_name} {contact.last_name}</td>
                      <td>{contact.email}</td>
                      <td>{contact.company_name || 'N/A'}</td>
                      <td>
                        <div
                          onClick={() => handleCopyPhone(contact.id, contact.phone)}
                          className="badge badge-primary badge-outline w-36 justify-center cursor-pointer hover:bg-primary hover:text-white transition-colors"
                          title="Click to copy"
                        >
                          {copiedPhoneId === contact.id ? "Copied!" : (contact.phone || 'N/A')}
                        </div>
                      </td>
                      <td>{contact.owner_name || 'N/A'}</td>
                      <td className="text-right space-x-2">
                        <button onClick={() => openEditModal(contact)} className="btn btn-xs btn-outline">Edit</button>
                        {isAdmin && <button onClick={() => handleDelete(contact.id)} className="btn btn-xs btn-outline btn-error">Delete</button>}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Contact Modal */}
      <dialog id="contact_modal" className="modal">
        <div className="modal-box w-11/12 max-w-2xl">
          <h3 className="font-bold text-lg mb-4">{modalMode === 'add' ? 'Add New Contact' : 'Edit Contact'}</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex space-x-4">
              <div className="form-control w-1/2">
                <label className="label"><span className="label-text">First Name</span></label>
                <input type="text" name="first_name" value={formData.first_name} onChange={handleFormChange} className="input input-bordered w-full" required />
              </div>
              <div className="form-control w-1/2">
                <label className="label"><span className="label-text">Last Name</span></label>
                <input type="text" name="last_name" value={formData.last_name} onChange={handleFormChange} className="input input-bordered w-full" required />
              </div>
            </div>
            <div className="flex space-x-4">
              <div className="form-control w-1/2">
                <label className="label"><span className="label-text">Email</span></label>
                <input type="email" name="email" value={formData.email} onChange={handleFormChange} className="input input-bordered w-full" required />
              </div>
              <div className="form-control w-1/2">
                <label className="label"><span className="label-text">Phone</span></label>
                <input type="text" name="phone" value={formData.phone} onChange={handleFormChange} className="input input-bordered w-full" />
              </div>
            </div>
            <div className="flex space-x-4">
              <div className="form-control w-1/2">
                <label className="label"><span className="label-text">Company</span></label>
                <select name="company" value={formData.company} onChange={handleFormChange} className="select select-bordered w-full" required>
                  <option value="" disabled>Select a Company</option>
                  {companies.map((comp) => <option key={comp.id} value={comp.id}>{comp.name}</option>)}
                </select>
              </div>
              <div className="form-control w-1/2">
                <label className="label"><span className="label-text">Manager (Owner)</span></label>
                <input type="text" name="owner_name" value={formData.owner_name} className="input input-bordered w-full bg-base-200 text-base-content/60 cursor-not-allowed" readOnly disabled />
              </div>
            </div>
            <div className="modal-action">
              <button type="button" className="btn" onClick={() => document.getElementById('contact_modal').close()}>Cancel</button>
              <button type="submit" className="btn btn-primary">Save</button>
            </div>
          </form>
        </div>
        <form method="dialog" className="modal-backdrop"><button>close</button></form>
      </dialog>
    </>
  );
}

export default Contacts;