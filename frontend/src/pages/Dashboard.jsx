import { useState, useEffect } from 'react';
import api from '../api';

const getLocalISOTime = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  const tzOffset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - tzOffset).toISOString().slice(0, 16);
};

function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [reminders, setReminders] = useState([]);
  const [deals, setDeals] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({ text: '', date: '', deal: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const fetchDeals = async () => {
      try {
        const res = await api.get('sales/deals/');
        setDeals(res.data);
      } catch (err) {
        console.error("Failed to load deals", err);
      }
    };

    const fetchAnalytics = async () => {
      try {
        const res = await api.get('sales/analytics/');
        setMetrics(res.data);
      } catch (err) {
        console.error("Error fetching analytics:", err);
        setError("Failed to load analytics.");
      }
    };

    const fetchReminders = async () => {
      try {
        const res = await api.get('sales/reminders/');
        setReminders(res.data);
      } catch (err) {
        console.error("Failed to load reminders", err);
      }
    };

    const fetchAllData = async () => {
      setLoading(true);
      await Promise.allSettled([fetchAnalytics(), fetchReminders(), fetchDeals()]);
      setLoading(false);
    };

    fetchAllData();
  }, []);

  const handleToggleDone = async (reminder) => {
    setReminders(prev => prev.map(r =>
      r.id === reminder.id ? { ...r, is_done: !reminder.is_done } : r
    ));

    try {
      await api.patch(`sales/reminders/${reminder.id}/`, { is_done: !reminder.is_done });
    } catch (err) {
      console.error("Error updating status", err);
      setReminders(prev => prev.map(r =>
        r.id === reminder.id ? { ...r, is_done: reminder.is_done } : r
      ));
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this reminder?")) return;
    try {
      await api.delete(`sales/reminders/${id}/`);
      setReminders(prev => prev.filter(r => r.id !== id));
    } catch (err) {
      console.error("Error deleting reminder", err);
    }
  };

  const openEditModal = (reminder) => {
    setFormData({
      text: reminder.text || '',
      date: getLocalISOTime(reminder.date),
      deal: reminder.deal
    });
    setEditingId(reminder.id);
    setIsModalOpen(true);
  };

  const openCreateModal = () => {
    const defaultDate = new Date();
    defaultDate.setHours(defaultDate.getHours() + 1);

    setFormData({ text: '', date: getLocalISOTime(defaultDate), deal: '' });
    setEditingId(null);
    setIsModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    const payload = {
      ...formData,
      deal: parseInt(formData.deal, 10),
      date: new Date(formData.date).toISOString()
    };

    try {
      if (editingId) {
        const res = await api.put(`sales/reminders/${editingId}/`, payload);
        setReminders(prev => prev.map(r => r.id === editingId ? res.data : r));
      } else {
        const res = await api.post('sales/reminders/', payload);
        setReminders([res.data, ...reminders]);
      }
      setIsModalOpen(false);
    } catch (err) {
      console.error("Error saving reminder", err);
      alert("Failed to save reminder. Please check the data.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) return <div className="flex justify-center mt-20"><span className="loading loading-spinner loading-lg text-primary"></span></div>;

  const maxStageValue = metrics?.stages?.length ? Math.max(...metrics.stages.map(s => s.total_value || 0)) : 0;

  return (
    <div className="space-y-8 relative pb-10">
      <h1 className="text-3xl font-bold">Sales Overview</h1>

      {/* --- БЛОК АНАЛИТИКИ --- */}
      {error ? (
        <div className="alert alert-error shadow-sm">{error}</div>
      ) : metrics ? (
        <>
          <div className="stats shadow w-full bg-base-100">
            <div className="stat">
              <div className="stat-figure text-primary">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="inline-block w-8 h-8 stroke-current"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path></svg>
              </div>
              <div className="stat-title">Current deals</div>
              <div className="stat-value text-primary">${metrics.pipeline_value?.toLocaleString() || 0}</div>
              <div className="stat-desc">Total value of active deals</div>
            </div>

            <div className="stat">
              <div className="stat-figure text-secondary">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="inline-block w-8 h-8 stroke-current"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
              </div>
              <div className="stat-title">Expected This Month</div>
              <div className="stat-value text-secondary">${metrics.expected_revenue?.toLocaleString() || 0}</div>
              <div className="stat-desc">Closing within current month</div>
            </div>

            <div className="stat">
              <div className="stat-figure text-accent">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="inline-block w-8 h-8 stroke-current"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              </div>
              <div className="stat-title">Win Rate</div>
              <div className="stat-value text-accent">{metrics.win_rate || 0}%</div>
              <div className="stat-desc">{metrics.won_deals || 0} deals won historically</div>
            </div>
          </div>

          <div className="bg-base-100 rounded-box shadow p-6">
            <h2 className="text-xl font-semibold mb-6">Distribution by Stage</h2>

            <div className="space-y-4">
              {metrics.stages?.map((stage, index) => {
                const progressValue = maxStageValue > 0 ? ((stage.total_value || 0) / maxStageValue) * 100 : 0;

                return (
                  <div key={index} className="flex items-center">
                    <div className="w-1/4 pr-4 text-right font-medium">
                      {stage.name} <span className="text-xs text-base-content/50">({stage.deal_count})</span>
                    </div>

                    <div className="w-1/2 px-2">
                      <progress
                        className={`progress w-full h-4 ${stage.is_won ? 'progress-success' : stage.is_lost ? 'progress-error' : 'progress-primary'}`}
                        value={progressValue}
                        max="100"
                      ></progress>
                    </div>

                    <div className="w-1/4 pl-4 font-bold">
                      ${(stage.total_value || 0).toLocaleString()}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </>
      ) : (
        <div className="alert alert-warning shadow-sm">No analytics data available.</div>
      )}

      {/* --- ТАБЛИЦА НАПОМИНАНИЙ --- */}
      <div className="card bg-base-100 shadow-xl mt-8">
        <div className="card-body p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="card-title text-xl">Upcoming Reminders</h2>
            <button className="btn btn-primary btn-sm" onClick={openCreateModal}>
              + Add Reminder
            </button>
          </div>

          {/* Контейнер с overflow-y-auto для скролла внутри таблицы */}
          <div className="overflow-x-auto overflow-y-auto max-h-[400px] border border-base-200 rounded-lg pr-2 custom-scrollbar">
            <table className="table table-pin-rows table-zebra w-full">
              <thead>
                <tr className="bg-base-200 text-base-content">
                  <th>Status</th>
                  <th>Date & Time</th>
                  <th>Task</th>
                  <th>Deal</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {reminders.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="text-center text-base-content/50 py-8">
                      No reminders scheduled.
                    </td>
                  </tr>
                ) : (
                  reminders.map((reminder) => (
                    <tr key={reminder.id} className="hover">
                      <td>
                        <input
                          type="checkbox"
                          className="checkbox checkbox-primary checkbox-sm"
                          checked={reminder.is_done}
                          onChange={() => handleToggleDone(reminder)}
                        />
                      </td>
                      <td className={`whitespace-nowrap font-medium ${reminder.is_done ? "opacity-50" : ""}`}>
                        {new Date(reminder.date).toLocaleString([], {
                          month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                        })}
                      </td>
                      <td className={reminder.is_done ? "line-through opacity-50" : ""}>
                        {reminder.text || <span className="text-gray-400 italic">No description</span>}
                      </td>
                      <td>
                        <a href={`/deals/${reminder.deal}`} className="link link-hover text-primary font-semibold truncate max-w-[150px] inline-block">
                          {reminder.deal_title || `Deal #${reminder.deal}`}
                        </a>
                      </td>
                      <td>
                        <div className="flex gap-2">
                          <button
                            className="btn btn-ghost btn-xs text-info"
                            onClick={() => openEditModal(reminder)}
                            disabled={reminder.is_done}
                          >
                            Edit
                          </button>
                          <button
                            className="btn btn-ghost btn-xs text-error"
                            onClick={() => handleDelete(reminder.id)}
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* --- МОДАЛЬНОЕ ОКНО --- */}
      {isModalOpen && (
        <dialog className="modal modal-open">
          <div className="modal-box">
            <h3 className="font-bold text-lg mb-4">
              {editingId ? "Edit Reminder" : "New Reminder"}
            </h3>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="form-control w-full">
                <label className="label"><span className="label-text">Task Description</span></label>
                <input
                  type="text"
                  className="input input-bordered w-full"
                  value={formData.text}
                  onChange={e => setFormData({ ...formData, text: e.target.value })}
                  placeholder="E.g. Call client for feedback"
                />
              </div>

              <div className="form-control w-full">
                <label className="label"><span className="label-text">Date & Time</span></label>
                <input
                  type="datetime-local"
                  required
                  className="input input-bordered w-full"
                  value={formData.date}
                  onChange={e => setFormData({ ...formData, date: e.target.value })}
                />
              </div>

              <div className="form-control w-full">
                <label className="label">
                  <span className="label-text">Select Deal</span>
                </label>
                <select
                  className="select select-bordered w-full"
                  value={formData.deal}
                  onChange={e => setFormData({ ...formData, deal: e.target.value })}
                  required
                >
                  <option value="" disabled>-- Choose a deal --</option>
                  {deals.map(deal => (
                    <option key={deal.id} value={deal.id}>
                      {deal.title || `Deal #${deal.id}`}
                    </option>
                  ))}
                </select>
                {deals.length === 0 && (
                  <label className="label">
                    <span className="label-text-alt text-error">No active deals found.</span>
                  </label>
                )}
              </div>

              <div className="modal-action mt-6">
                <button
                  type="button"
                  className="btn"
                  onClick={() => setIsModalOpen(false)}
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isSubmitting || deals.length === 0}
                >
                  {isSubmitting ? <span className="loading loading-spinner loading-xs"></span> : "Save"}
                </button>
              </div>
            </form>
          </div>
          <form method="dialog" className="modal-backdrop" onClick={() => !isSubmitting && setIsModalOpen(false)}>
            <button>close</button>
          </form>
        </dialog>
      )}

    </div>
  );
}

export default Dashboard;