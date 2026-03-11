import { useState, useEffect } from 'react';
import { Calendar, LayoutDashboard, Mail, MessageSquare, Settings, Activity } from 'lucide-react';
import { getAgentStatus } from '../../services/api';

const Sidebar = ({ activeTab, setActiveTab }) => {
    const navItems = [
        { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
        { id: 'schedule', icon: Calendar, label: 'Schedule' },
        { id: 'mail', icon: Mail, label: 'Mail Center' },
        { id: 'content', icon: MessageSquare, label: 'Content Studio' },
        { id: 'activity', icon: Activity, label: 'Agent Activity' },
    ];

    const [agentStatus, setAgentStatus] = useState([
        { name: 'Chronos', role: 'Scheduler', status: 'Idle', color: 'text-agents-chronos', indicator: 'bg-agents-chronos opacity-50' },
        { name: 'Hermes', role: 'Mailer', status: 'Idle', color: 'text-agents-hermes', indicator: 'bg-agents-hermes opacity-50' },
        { name: 'Apollo', role: 'Content', status: 'Idle', color: 'text-agents-apollo', indicator: 'bg-agents-apollo opacity-50' },
        { name: 'Athena', role: 'Analytics', status: 'Idle', color: 'text-agents-athena', indicator: 'bg-agents-athena opacity-50' },
        { name: 'Nexus Core', role: 'Coordinator', status: 'Idle', color: 'text-primary', indicator: 'bg-primary opacity-50' },
        { name: 'Fortuna', role: 'Budget', status: 'Idle', color: 'text-warning', indicator: 'bg-warning opacity-50' },
    ]);

    useEffect(() => {
        const fetchStatus = () => {
            getAgentStatus()
                .then(data => {
                    setAgentStatus(data.map(a => {
                        const colorMap = {
                            Chronos: 'text-agents-chronos',
                            Hermes: 'text-agents-hermes',
                            Apollo: 'text-agents-apollo',
                            Athena: 'text-agents-athena',
                            'Nexus Core': 'text-primary',
                            Fortuna: 'text-warning',
                        };
                        const indicatorMap = {
                            working: `animate-pulse ${(colorMap[a.name] || 'text-gray-400').replace('text-', 'bg-')}`,
                            idle: `${(colorMap[a.name] || 'text-gray-400').replace('text-', 'bg-')} opacity-50`,
                            observing: `${(colorMap[a.name] || 'text-gray-400').replace('text-', 'bg-')} opacity-80`,
                            planning: `animate-pulse ${(colorMap[a.name] || 'text-gray-400').replace('text-', 'bg-')}`,
                        };
                        const statusLabels = {
                            working: 'Working...',
                            idle: 'Idle',
                            observing: 'Observing',
                            planning: 'Planning...',
                        };
                        return {
                            name: a.name,
                            role: a.role,
                            status: statusLabels[a.status] || a.status,
                            color: colorMap[a.name] || 'text-gray-400',
                            indicator: indicatorMap[a.status] || indicatorMap.idle,
                        };
                    }));
                })
                .catch(() => {}); // Keep fallback
        };
        fetchStatus();
        const interval = setInterval(fetchStatus, 5000); // Poll every 5s
        return () => clearInterval(interval);
    }, []);

    return (
        <aside className="w-64 border-r border-gray-800 bg-card h-full flex flex-col">
            <div className="p-6">
                <h1 className="text-2xl font-bold text-primary tracking-wider">NEXUS</h1>
                <p className="text-xs text-text-secondary mt-1 tracking-widest uppercase">Event Command</p>
            </div>

            <nav className="flex-1 px-4 space-y-2 mt-4">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = activeTab === item.id;
                    return (
                        <button
                            key={item.id}
                            onClick={() => setActiveTab(item.id)}
                            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${isActive
                                    ? 'bg-primary/10 text-primary'
                                    : 'text-text-secondary hover:bg-gray-800/50 hover:text-white'
                                }`}
                        >
                            <Icon size={20} />
                            <span className="font-medium">{item.label}</span>
                        </button>
                    );
                })}
            </nav>

            {/* Agent Status Sidebar Section */}
            <div className="p-4 border-t border-gray-800">
                <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-4 px-2">Swarm Status</h3>
                <div className="space-y-3 px-2">
                    {agentStatus.map(agent => (
                        <div key={agent.name} className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className={`w-2 h-2 rounded-full ${agent.indicator}`} />
                                <div>
                                    <div className={`text-sm font-medium ${agent.color}`}>{agent.name}</div>
                                    <div className="text-xs text-gray-500">{agent.status}</div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="p-4">
                <button className="w-full flex items-center space-x-3 px-4 py-3 text-text-secondary hover:text-white hover:bg-gray-800/50 rounded-lg transition-colors">
                    <Settings size={20} />
                    <span className="font-medium">Settings</span>
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
