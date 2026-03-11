import { useState } from 'react';
import Layout from './components/layout/Layout';

// Import Dashboard Components
import EventOverview from './components/dashboard/EventOverview';
import QuickInsights from './components/dashboard/QuickInsights';
import ActivityFeed from './components/dashboard/ActivityFeed';
import PendingApprovals from './components/dashboard/PendingApprovals';

const Dashboard = () => (
  <div className="space-y-6 h-full pb-8">
    <div className="flex justify-between items-end">
      <h2 className="text-3xl font-bold tracking-tight text-white drop-shadow-sm">Dashboard Overview</h2>
      <div className="text-sm text-text-secondary bg-card px-3 py-1.5 rounded-md border border-gray-800 flex items-center gap-2 shadow-inner shadow-black/20">
        <span className="w-2 h-2 rounded-full bg-success animate-pulse"></span>
        <span>Live Mode: <span className="text-success font-medium">Connected</span></span>
      </div>
    </div>
    
    <EventOverview />
    
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
         <ActivityFeed />
      </div>
      <div className="space-y-6">
         <PendingApprovals />
         <QuickInsights />
      </div>
    </div>
  </div>
);

import Schedule from './components/schedule/ScheduleView';
import MailCenter from './components/mail/MailCenter';
import ContentStudio from './components/content/ContentStudio';
import Activity from './components/activity/AgentActivity';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderPage = () => {
    switch(activeTab) {
      case 'dashboard': return <Dashboard />;
      case 'schedule': return <Schedule />;
      case 'mail': return <MailCenter />;
      case 'content': return <ContentStudio />;
      case 'activity': return <Activity />;
      default: return <Dashboard />;
    }
  };

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      {renderPage()}
    </Layout>
  );
}

export default App;
