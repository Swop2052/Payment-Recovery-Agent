import { useState } from 'react';
import axios from 'axios';
import { Play } from 'lucide-react';

export default function PriorityQueueTab() {
  const [limit, setLimit] = useState(10);
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchQueue = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`http://localhost:8000/priority-queue?limit=${limit}`);
      setQueue(res.data.priority_queue);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const totalValue = queue.reduce((sum, item) => sum + item.expected_recovery_value, 0);

  return (
    <div>
      <h2 style={{marginBottom: '0.5rem'}}>Recovery Priority Queue</h2>
      <p style={{color: 'var(--text-muted)', marginBottom: '2rem'}}>
        Ranks pending failed transactions by expected recovery value = predicted success probability × amount
      </p>

      <div style={{display: 'flex', gap: '1rem', alignItems: 'flex-end', marginBottom: '2rem'}}>
        <div className="input-group" style={{width: '300px'}}>
          <label>Number of transactions to rank: {limit}</label>
          <input type="range" min="5" max="30" value={limit} onChange={e => setLimit(e.target.value)} />
        </div>
        <button className="btn-primary" onClick={fetchQueue} disabled={loading} style={{padding: '0.75rem 1.5rem'}}>
          <Play size={18} /> {loading ? 'Generating...' : 'Generate Priority Queue'}
        </button>
      </div>

      {queue.length > 0 && (
        <>
          <div className="glass-panel metric-card" style={{marginBottom: '2rem', display: 'inline-block', padding: '1rem 2rem'}}>
            <span className="label">Total Expected Recovery Value (Top {queue.length})</span>
            <span className="value text-success">₹ {totalValue.toLocaleString()}</span>
          </div>

          <div className="glass-panel" style={{overflowX: 'auto', padding: 0}}>
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Transaction ID</th>
                  <th>Reason</th>
                  <th>Amount</th>
                  <th>Success Prob</th>
                  <th>Expected Value</th>
                </tr>
              </thead>
              <tbody>
                {queue.map((item, idx) => (
                  <tr key={item.transaction_id}>
                    <td>#{idx + 1}</td>
                    <td style={{fontFamily: 'monospace'}}>{item.transaction_id}</td>
                    <td><span style={{background:'rgba(255,255,255,0.1)', padding:'4px 8px', borderRadius:'4px', fontSize:'0.85rem'}}>{item.failure_reason}</span></td>
                    <td>₹ {item.amount.toLocaleString()}</td>
                    <td>
                      <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                        {(item.predicted_success_prob * 100).toFixed(1)}%
                        <div style={{height:'6px', width:'50px', background:'rgba(255,255,255,0.1)', borderRadius:'3px', overflow:'hidden'}}>
                          <div style={{height:'100%', background:'var(--accent-primary)', width:`${item.predicted_success_prob * 100}%`}}></div>
                        </div>
                      </div>
                    </td>
                    <td className="text-success" style={{fontWeight: 'bold'}}>₹ {item.expected_recovery_value.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
