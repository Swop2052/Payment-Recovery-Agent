import { useState } from 'react';
import axios from 'axios';
import { Rocket, Lightbulb, MessageSquare, Clock, Smartphone } from 'lucide-react';

const FAILURE_REASONS = [
  "insufficient_balance", "bank_server_down", "wrong_otp", "network_timeout",
  "card_declined_by_bank", "daily_limit_exceeded", "expired_card"
];

export default function LiveDemoTab() {
  const [formData, setFormData] = useState({
    transaction_id: "DEMO-001",
    user_id: "U00001",
    user_name: "Krishna",
    amount: 1499.0,
    payment_method: "upi",
    failure_reason: "insufficient_balance",
    hour_of_day: 14,
    day_of_week: 2,
    device_type: "android",
    retry_count: 0,
    past_success_rate: 0.75,
    preferred_channel: "whatsapp"
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' || type === 'range' ? Number(value) : value
    }));
  };

  const runAgent = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post('http://localhost:8000/trigger-recovery-agent', formData);
      setResult(res.data);
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  return (
    <div>
      <h2 style={{marginBottom: '0.5rem'}}>🎮 Simulate a failed transaction</h2>
      <p style={{color: 'var(--text-muted)', marginBottom: '2rem'}}>Adjust the parameters below and watch the agent make autonomous decisions.</p>

      <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem'}}>
        <div className="glass-panel form-grid">
          <div className="input-group">
            <label>Amount (INR)</label>
            <input type="number" name="amount" value={formData.amount} onChange={handleChange} />
          </div>
          <div className="input-group">
            <label>Payment Method</label>
            <select name="payment_method" value={formData.payment_method} onChange={handleChange}>
              {["upi", "credit_card", "debit_card", "netbanking", "wallet"].map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
          <div className="input-group">
            <label>Failure Reason</label>
            <select name="failure_reason" value={formData.failure_reason} onChange={handleChange}>
              {FAILURE_REASONS.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
          <div className="input-group">
            <label>Device Type</label>
            <select name="device_type" value={formData.device_type} onChange={handleChange}>
              {["android", "ios", "desktop_web", "mobile_web"].map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
        </div>

        <div className="glass-panel form-grid">
          <div className="input-group">
            <label>Preferred Channel</label>
            <select name="preferred_channel" value={formData.preferred_channel} onChange={handleChange}>
              {["whatsapp", "sms", "email"].map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="input-group">
            <label>User's Past Success Rate: {formData.past_success_rate}</label>
            <input type="range" name="past_success_rate" min="0" max="1" step="0.05" value={formData.past_success_rate} onChange={handleChange} />
          </div>
          <div className="input-group">
            <label>Retry count so far: {formData.retry_count}</label>
            <input type="range" name="retry_count" min="0" max="3" step="1" value={formData.retry_count} onChange={handleChange} />
          </div>
          <div className="input-group">
            <label>Hour of failure: {formData.hour_of_day}:00</label>
            <input type="range" name="hour_of_day" min="0" max="23" step="1" value={formData.hour_of_day} onChange={handleChange} />
          </div>
        </div>
      </div>

      <div style={{textAlign: 'center', marginBottom: '2rem'}}>
        <button className="btn-primary" onClick={runAgent} disabled={loading}>
          {loading ? <span className="spinner">↻</span> : <Rocket size={20} />}
          {loading ? 'Agent Thinking...' : 'Run Recovery Agent'}
        </button>
      </div>
      
      {error && <div className="glass-panel" style={{borderColor: 'var(--danger)', color: 'var(--danger)'}}>{error}</div>}

      {result && (
        <div style={{animation: 'fadeInUp 0.5s ease-out'}}>
          <div className="glass-panel" style={{background: 'rgba(255,255,255,0.02)', borderColor: 'var(--success)'}}>
            <h3 style={{color: 'var(--success)', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
              <CheckCircle size={24}/> Agent decision complete
            </h3>
            
            <div className="metrics-grid" style={{marginBottom: '2rem'}}>
              <div className="metric-card">
                <span className="label">Predicted Success</span>
                <span className="value">{(result.predicted_success_prob * 100).toFixed(1)}%</span>
              </div>
              <div className="metric-card">
                <span className="label">Attempt Recovery?</span>
                <span className="value" style={{color: result.should_attempt_recovery ? 'var(--success)' : 'var(--danger)'}}>
                  {result.should_attempt_recovery ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="metric-card">
                <span className="label">Channel</span>
                <span className="value" style={{textTransform: 'uppercase'}}><Smartphone size={24} style={{display:'inline', marginBottom:'-4px'}}/> {result.recommended_channel}</span>
              </div>
            </div>

            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem'}}>
              <div>
                <h4 style={{marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                  <Lightbulb size={20} color="var(--warning)"/> Agent Reasoning Trace
                </h4>
                {result.reasons && result.reasons.map((r, i) => (
                  <div key={i} style={{background: 'rgba(245, 158, 11, 0.1)', borderLeft: '3px solid var(--warning)', padding: '0.75rem', marginBottom: '0.5rem', borderRadius: '4px', fontSize: '0.95rem'}}>
                    {r}
                  </div>
                ))}
              </div>

              <div>
                {result.should_attempt_recovery ? (
                  <>
                    <h4 style={{marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                      <Clock size={20} color="var(--accent-primary)"/> Recommended Retry
                    </h4>
                    <div style={{fontSize: '1.1rem', marginBottom: '1.5rem', padding: '0.5rem', background: 'rgba(255,255,255,0.05)', borderRadius: '6px'}}>
                      {new Date(result.recommended_retry_time).toLocaleString()}
                    </div>

                    <h4 style={{marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                      <MessageSquare size={20} color="var(--success)"/> Generated Message
                    </h4>
                    <div className="message-card" style={{marginTop: 0}}>
                      {result.generated_message}
                    </div>
                  </>
                ) : (
                  <div className="glass-panel" style={{borderColor: 'var(--warning)', background: 'rgba(245, 158, 11, 0.05)'}}>
                    ⏸️ Agent decided this transaction has low recovery value - skipping outreach to avoid spam.
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Just adding CheckCircle since we missed importing it in this file
import { CheckCircle } from 'lucide-react';
