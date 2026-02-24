import { useState, useEffect } from 'react';
import api from '../api';

function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get('sales/analytics/')
      .then(res => {
        setMetrics(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching analytics:", err);
        setError("Failed to load analytics dashboard.");
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="flex justify-center mt-20"><span className="loading loading-spinner loading-lg text-primary"></span></div>;
  if (error) return <div className="alert alert-error mt-10">{error}</div>;

  const maxStageValue = Math.max(...metrics.stages.map(s => s.total_value || 0));

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Sales Overview</h1>

      <div className="stats shadow w-full bg-base-100">
        <div className="stat">
          <div className="stat-figure text-primary">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="inline-block w-8 h-8 stroke-current"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path></svg>
          </div>
          <div className="stat-title">Open Pipeline</div>
          <div className="stat-value text-primary">${metrics.pipeline_value.toLocaleString()}</div>
          <div className="stat-desc">Total value of active deals</div>
        </div>
        
        <div className="stat">
          <div className="stat-figure text-secondary">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="inline-block w-8 h-8 stroke-current"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
          </div>
          <div className="stat-title">Expected This Month</div>
          <div className="stat-value text-secondary">${metrics.expected_revenue.toLocaleString()}</div>
          <div className="stat-desc">Closing within current month</div>
        </div>
        
        <div className="stat">
          <div className="stat-figure text-accent">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="inline-block w-8 h-8 stroke-current"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          </div>
          <div className="stat-title">Win Rate</div>
          <div className="stat-value text-accent">{metrics.win_rate}%</div>
          <div className="stat-desc">{metrics.won_deals} deals won historically</div>
        </div>
      </div>

      <div className="bg-base-100 rounded-box shadow p-6">
        <h2 className="text-xl font-semibold mb-6">Pipeline Funnel by Stage</h2>
        
        <div className="space-y-4">
          {metrics.stages.map((stage, index) => {
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
      
    </div>
  );
}

export default Dashboard;