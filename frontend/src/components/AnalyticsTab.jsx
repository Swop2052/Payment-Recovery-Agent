import { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingDown, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f59e0b', '#10b981', '#3b82f6'];

export default function AnalyticsTab() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://localhost:8000/analytics')
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="spinner" style={{textAlign: 'center', padding: '2rem'}}>Loading analytics...</div>;
  if (!data) return <div>Error loading data. Is the backend running?</div>;

  return (
    <div>
      <h2 style={{marginBottom: '1.5rem'}}>Analytics Dashboard</h2>
      
      <div className="metrics-grid">
        <div className="glass-panel metric-card">
          <span className="label"><AlertCircle size={14} style={{display:'inline', marginBottom:'-2px'}}/> Total Failed Txns</span>
          <span className="value">{data.total_failed_transactions.toLocaleString()}</span>
        </div>
        <div className="glass-panel metric-card">
          <span className="label"><CheckCircle size={14} style={{display:'inline', marginBottom:'-2px'}}/> Revenue Recovered</span>
          <span className="value text-success">₹ {data.revenue_recovered.toLocaleString(undefined, {maximumFractionDigits: 0})}</span>
        </div>
        <div className="glass-panel metric-card">
          <span className="label"><TrendingDown size={14} style={{display:'inline', marginBottom:'-2px'}}/> Revenue Lost</span>
          <span className="value text-danger">₹ {data.revenue_lost.toLocaleString(undefined, {maximumFractionDigits: 0})}</span>
        </div>
      </div>

      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem'}}>
        <div className="glass-panel">
          <h3 style={{marginBottom: '1rem'}}>Failures by Reason</h3>
          <div style={{height: 300}}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.by_failure_reason} layout="vertical" margin={{ left: 50 }}>
                <XAxis type="number" hide />
                <YAxis dataKey="failure_reason" type="category" width={100} tick={{fill: '#94a3b8', fontSize: 12}} />
                <Tooltip cursor={{fill: 'rgba(255,255,255,0.05)'}} contentStyle={{background: '#1e293b', border: 'none', borderRadius: '8px'}}/>
                <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div className="glass-panel">
          <h3 style={{marginBottom: '1rem'}}>Failures by Payment Method</h3>
          <div style={{height: 300}}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.by_payment_method}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="count"
                  nameKey="payment_method"
                >
                  {data.by_payment_method.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{background: '#1e293b', border: 'none', borderRadius: '8px'}}/>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
