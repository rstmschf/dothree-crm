import { useState, useEffect } from 'react';
import api from '../api';
import { Link } from 'react-router-dom';

function Deals() {
  const [deals, setDeals] = useState([]);
  const [stages, setStages] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [leads, setLeads] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);

  // Modal State
  const [modalMode, setModalMode] = useState('add');
  const [currentId, setCurrentId] = useState(null);
  const [formData, setFormData] = useState({
    title: '', value: '', currency: 'USD', stage: '', lead: '', company: '', close_date: '', owner: ''
  });

  useEffect(() => {
    // Check Admin status for delete permissions
    const token = localStorage.getItem('access');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (payload.role === 'admin' || payload.role === 'manager') setIsAdmin(true);
      } catch (e) { }
    }
    fetchAllData();
  }, []);

  // Fetch all required data in parallel for efficiency
  const fetchAllData = async () => {
    try {
      const [dealsRes, stagesRes, companiesRes, leadsRes] = await Promise.all([
        api.get('sales/deals/'),
        api.get('sales/stages/'),
        api.get('clients/companies/'),
        api.get('sales/leads/')
      ]);

      setDeals(dealsRes.data);
      // Sort stages by the 'order' field provided by serializer
      setStages(stagesRes.data.sort((a, b) => a.order - b.order));
      setCompanies(companiesRes.data);
      setLeads(leadsRes.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching deal data:", err);
      setError('Failed to load data.');
      setLoading(false);
    }
  };

  // --- HTML5 DRAG AND DROP HANDLERS ---
  const handleDragStart = (e, dealId) => {
    e.dataTransfer.setData('dealId', dealId);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = async (e, newStageId) => {
    e.preventDefault();
    const dealId = e.dataTransfer.getData('dealId');
    if (!dealId) return;

    const previousDeals = [...deals];
    setDeals(deals.map(deal =>
      deal.id.toString() === dealId ? { ...deal, stage: newStageId } : deal
    ));

    try {
      // Call DealMoveStageSerializer endpoint
      await api.post(`/sales/deals/${dealId}/move-stage/`, { stage_id: newStageId });
    } catch (err) {
      console.error("Failed to move deal:", err);
      alert("Failed to move deal. Reverting...");
      setDeals(previousDeals); // Revert on failure
    }
  };

  // --- MODAL HANDLERS ---
  const openAddModal = () => {
    setModalMode('add');
    setFormData({
      title: '', value: '', currency: 'USD',
      stage: stages.length > 0 ? stages[0].id : '', // Default to first stage
      lead: '', company: '', close_date: '', owner: 'Auto-assigned'
    });
    document.getElementById('deal_modal').showModal();
  };

  const openEditModal = (deal) => {
    setModalMode('edit');
    setCurrentId(deal.id);
    setFormData({
      title: deal.title || '',
      value: deal.value || '',
      currency: deal.currency || 'USD',
      stage: deal.stage || '',
      lead: deal.lead || '',
      company: deal.company || '',
      close_date: deal.close_date ? deal.close_date.split('T')[0] : '', // Format for date input
      owner: deal.owner || 'N/A'
    });
    document.getElementById('deal_modal').showModal();
  };

  const handleFormChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const { owner, ...dataToSend } = formData;
      // Convert empty strings to null for ForeignKeys to prevent Django validation errors
      if (!dataToSend.lead) dataToSend.lead = null;
      if (!dataToSend.company) dataToSend.company = null;

      if (modalMode === 'add') {
        const response = await api.post('sales/deals/', dataToSend);
        setDeals([...deals, response.data]);
      } else {
        const response = await api.put(`sales/deals/${currentId}/`, dataToSend);
        setDeals(deals.map(d => d.id === currentId ? response.data : d));
      }
      document.getElementById('deal_modal').close();
    } catch (err) { alert("Failed to save deal."); console.error(err); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this deal?")) return;
    try {
      await api.delete(`sales/deals/${id}/`);
      setDeals(deals.filter(d => d.id !== id));
    } catch (err) { alert("Failed to delete deal."); }
  };

  return (
    <>
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-3xl font-bold">Deals</h1>
        <button onClick={openAddModal} className="btn btn-primary">+ New Deal</button>
      </div>

      {loading && <div className="flex justify-center p-4"><span className="loading loading-spinner loading-lg text-primary"></span></div>}
      {error && <div className="alert alert-error">{error}</div>}

      {!loading && !error && (
        <div className="flex overflow-x-auto space-x-6 pb-4 min-h-[60vh]">
          {/* Map through the Stages to create Kanban Columns */}
          {stages.map(stage => (
            <div
              key={stage.id}
              className="bg-base-200 rounded-box w-80 min-w-[260px] p-4 flex flex-col shadow-inner"
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, stage.id)}
            >
              <div className="flex justify-between items-center mb-4 px-1">
                <h3 className="font-bold text-lg">{stage.name}</h3>
                <span className="badge badge-neutral">
                  {deals.filter(d => d.stage === stage.id).length}
                </span>
              </div>

              <div className="flex-1 space-y-4 overflow-y-auto">
                {/* Map through Deals belonging to this specific stage */}
                {deals.filter(deal => deal.stage === stage.id).map(deal => (
                  <div
                    key={deal.id}
                    draggable
                    onDragStart={(e) => handleDragStart(e, deal.id)}
                    className="bg-base-100 p-4 rounded-xl shadow cursor-grab active:cursor-grabbing hover:shadow-md transition-shadow border border-base-300"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-semibold">{deal.title}</h4>
                      {stage.is_won && <span className="text-success text-xl">🎉</span>}
                      {stage.is_lost && <span className="text-error text-xl">❌</span>}
                    </div>

                    <div className="text-xl font-bold text-primary mb-2">
                      {deal.value ? `${deal.value} ${deal.currency}` : 'No value'}
                    </div>

                    <div className="text-sm text-base-content/70 mb-3 space-y-1">
                      {deal.company && <div>🏢 {deal.company_name}</div>}
                      {deal.close_date && <div>📅 {deal.close_date.split('T')[0]}</div>}
                    </div>

                    <div className="flex justify-end space-x-2 mt-2 pt-2 border-t border-base-200">
                      <Link to={`/deals/${deal.id}`} className="btn btn-xs btn-primary btn-outline">Details</Link>
                      <button onClick={() => openEditModal(deal)} className="btn btn-xs btn-ghost">Edit</button>
                      {isAdmin && <button onClick={() => handleDelete(deal.id)} className="btn btn-xs btn-ghost text-error">Delete</button>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Deal Modal */}
      <dialog id="deal_modal" className="modal">
        <div className="modal-box w-11/12 max-w-3xl">
          <h3 className="font-bold text-lg mb-4">{modalMode === 'add' ? 'Add New Deal' : 'Edit Deal'}</h3>
          <form onSubmit={handleSubmit} className="space-y-4">

            {/* Row 1: Title & Value/Currency */}
            <div className="flex space-x-4">
              <div className="form-control w-1/2">
                <label className="label"><span className="label-text">Deal Title</span></label>
                <input type="text" name="title" value={formData.title} onChange={handleFormChange} className="input input-bordered w-full" required />
              </div>
              <div className="form-control w-1/4">
                <label className="label"><span className="label-text">Value</span></label>
                <input type="number" step="0.01" name="value" value={formData.value} onChange={handleFormChange} className="input input-bordered w-full" required />
              </div>
              <div className="form-control w-1/4">
                <label className="label"><span className="label-text">Currency</span></label>
                <select name="currency" value={formData.currency} onChange={handleFormChange} className="select select-bordered w-full">
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                </select>
              </div>
            </div>

            {/* Row 2: Stage & Close Date */}
            <div className="flex space-x-4">
              <div className="form-control w-1/2">
                <label className="label"><span className="label-text">Pipeline Stage</span></label>
                <select name="stage" value={formData.stage} onChange={handleFormChange} className="select select-bordered w-full" required>
                  <option value="" disabled>Select a Stage</option>
                  {stages.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                </select>
              </div>
              <div className="form-control w-1/2">
                <label className="label"><span className="label-text">Expected Close Date</span></label>
                <input type="date" name="close_date" value={formData.close_date} onChange={handleFormChange} className="input input-bordered w-full" />
              </div>
            </div>

            {/* Row 3: Company & Lead Links */}
            <div className="flex space-x-4">
              <div className="form-control w-1/2">
                <label className="label"><span className="label-text">Linked Company (Optional)</span></label>
                <select name="company" value={formData.company} onChange={handleFormChange} className="select select-bordered w-full">
                  <option value="">None</option>
                  {companies.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </div>
              <div className="form-control w-1/2">
                <label className="label"><span className="label-text">Linked Lead (Optional)</span></label>
                <select name="lead" value={formData.lead} onChange={handleFormChange} className="select select-bordered w-full">
                  <option value="">None</option>
                  {leads.map(l => <option key={l.id} value={l.id}>{l.title || `Lead #${l.id}`}</option>)}
                </select>
              </div>
            </div>

            <div className="modal-action mt-6">
              <button type="button" className="btn" onClick={() => document.getElementById('deal_modal').close()}>Cancel</button>
              <button type="submit" className="btn btn-primary">Save Deal</button>
            </div>
          </form>
        </div>
        <form method="dialog" className="modal-backdrop"><button>close</button></form>
      </dialog>
    </>
  );
}

export default Deals;