import { useState } from 'react';
import { Activity, BarChart2, Zap, DollarSign, Bot } from 'lucide-react';
import AnalyticsTab from './components/AnalyticsTab';
import LiveDemoTab from './components/LiveDemoTab';
import PriorityQueueTab from './components/PriorityQueueTab';
import ROISimulatorTab from './components/ROISimulatorTab';
import Chatbot from './components/Chatbot';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('analytics');

  return (
    <div className="app-container">
      <header className="header">
        <h1>
          <span className="gradient-text">Smart Payment Recovery</span> Agent
        </h1>
      </header>

      <div className="tabs-container">
        <button 
          className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          <BarChart2 size={18} /> Analytics
        </button>
        <button 
          className={`tab-btn ${activeTab === 'demo' ? 'active' : ''}`}
          onClick={() => setActiveTab('demo')}
        >
          <Activity size={18} /> Live Agent Demo
        </button>
        <button 
          className={`tab-btn ${activeTab === 'queue' ? 'active' : ''}`}
          onClick={() => setActiveTab('queue')}
        >
          <Zap size={18} /> Priority Queue
        </button>
        <button 
          className={`tab-btn ${activeTab === 'roi' ? 'active' : ''}`}
          onClick={() => setActiveTab('roi')}
        >
          <DollarSign size={18} /> ROI Simulator
        </button>
        <button 
          className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          <Bot size={18} /> AI Assistant
        </button>
      </div>

      <main className="tab-content glass-panel">
        {activeTab === 'analytics' && <AnalyticsTab />}
        {activeTab === 'demo' && <LiveDemoTab />}
        {activeTab === 'queue' && <PriorityQueueTab />}
        {activeTab === 'roi' && <ROISimulatorTab />}
        {activeTab === 'chat' && <Chatbot />}
      </main>
    </div>
  );
}

export default App;
