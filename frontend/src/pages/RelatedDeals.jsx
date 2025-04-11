import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../api';

function RelatedDeals() {
  const { id } = useParams(); // ID компании
  const navigate = useNavigate();
  
  const [deals, setDeals] = useState([]);
  const [company, setCompany] = useState(null);
  const [stages, setStages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    try {
      // Запрашиваем компанию, её сделки и список стадий (чтобы красиво показать статус)
      const [companyRes, dealsRes, stagesRes] = await Promise.all([
        api.get(`clients/companies/${id}/`),
        api.get(`sales/deals/?company=${id}`),
        api.get('sales/stages/')
      ]);
      
      setCompany(companyRes.data);
      setDeals(dealsRes.data);
      setStages(stagesRes.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching company deals:", err);
      setLoading(false);
    }
  };

  // Вспомогательная функция для получения имени стадии по её ID
  const getStageName = (stageId) => {
    const stage = stages.find(s => s.id === stageId);
    return stage ? stage.name : 'Unknown';
  };

  if (loading) return <div className="flex justify-center mt-20"><span className="loading loading-spinner loading-lg text-primary"></span></div>;
  if (!company) return <div className="text-center mt-10">Company not found.</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4 mb-6">
        <button onClick={() => navigate(-1)} className="btn btn-sm btn-ghost">← Back</button>
        <h1 className="text-3xl font-bold">Deals for {company.name}</h1>
      </div>

      <div className="bg-base-100 rounded-box shadow p-6">
        {deals.length === 0 ? (
          <div className="text-center py-10 text-base-content/60">
            No deals found for this company.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="table table-zebra w-full table-hover">
              <thead>
                <tr>
                  <th>Deal Title</th>
                  <th>Value</th>
                  <th>Stage</th>
                  <th>Expected Close</th>
                  <th>Manager</th>
                </tr>
              </thead>
              <tbody>
                {deals.map(deal => (
                  <tr 
                    key={deal.id} 
                    onClick={() => navigate(`/deals/${deal.id}`)}
                    className="cursor-pointer hover:bg-base-200 transition-colors"
                  >
                    <td className="font-bold text-primary">{deal.title}</td>
                    <td>${deal.value} {deal.currency}</td>
                    <td>
                      <span className="badge badge-neutral badge-sm">
                        {getStageName(deal.stage)}
                      </span>
                    </td>
                    <td>{deal.close_date ? deal.close_date.split('T')[0] : 'N/A'}</td>
                    <td>{deal.owner_name || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default RelatedDeals;