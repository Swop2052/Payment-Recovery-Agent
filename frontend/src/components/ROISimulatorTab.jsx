import { useState } from 'react';

export default function ROISimulatorTab() {
  const [txns, setTxns] = useState(10000);
  const [avgVal, setAvgVal] = useState(1500);
  const [baseRate, setBaseRate] = useState(20);
  const [aiRate, setAiRate] = useState(45);

  const baselineRecovered = txns * avgVal * (baseRate / 100);
  const aiRecovered = txns * avgVal * (aiRate / 100);
  const extraRevenue = aiRecovered - baselineRecovered;

  return (
    <div>
      <h2 style={{marginBottom: '0.5rem'}}>Revenue Impact Simulator</h2>
      <p style={{color: 'var(--text-muted)', marginBottom: '2rem'}}>Estimate monthly revenue impact of deploying this agent at scale</p>
      
      <div className="form-grid" style={{marginBottom: '2rem'}}>
        <div className="input-group">
          <label>Monthly failed transactions</label>
          <input type="number" value={txns} onChange={(e) => setTxns(Number(e.target.value))} />
        </div>
        <div className="input-group">
          <label>Average transaction value (INR)</label>
          <input type="number" value={avgVal} onChange={(e) => setAvgVal(Number(e.target.value))} />
        </div>
        <div className="input-group">
          <label>Current (baseline) recovery rate: {baseRate}%</label>
          <input type="range" min="0" max="100" value={baseRate} onChange={(e) => setBaseRate(Number(e.target.value))} />
        </div>
        <div className="input-group">
          <label>Expected AI recovery rate: {aiRate}%</label>
          <input type="range" min="0" max="100" value={aiRate} onChange={(e) => setAiRate(Number(e.target.value))} />
        </div>
      </div>

      <div className="metrics-grid">
        <div className="glass-panel metric-card">
          <span className="label">Baseline Monthly Recovery</span>
          <span className="value">₹ {baselineRecovered.toLocaleString()}</span>
        </div>
        <div className="glass-panel metric-card">
          <span className="label">AI Agent Monthly Recovery</span>
          <span className="value">₹ {aiRecovered.toLocaleString()}</span>
        </div>
        <div className="glass-panel metric-card" style={{border: '1px solid var(--accent-primary)'}}>
          <span className="label">Extra Revenue Recovered</span>
          <span className="value gradient-text">₹ {extraRevenue.toLocaleString()}</span>
        </div>
      </div>

      <div className="glass-panel" style={{marginTop: '2rem', textAlign: 'center', background: 'var(--accent-gradient)'}}>
        <h2 style={{color: 'white', margin: 0}}>
          🎉 Annualized extra revenue: ₹ {(extraRevenue * 12).toLocaleString()}
        </h2>
      </div>
    </div>
  );
}
