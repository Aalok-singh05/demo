import { useState, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Calendar, LayoutDashboard, Mail, MessageSquare, Settings, Activity, ChevronLeft, Menu, LogOut } from 'lucide-react';
import { getAgentStatus } from '../../services/api';

const Sidebar = ({ isOpen, toggleSidebar }) => {
    const navigate = useNavigate();

    const navItems = [
        { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
        { path: '/dashboard/schedule', icon: Calendar, label: 'Schedule' },
        { path: '/dashboard/mail', icon: Mail, label: 'Mail Center' },
        { path: '/dashboard/content', icon: MessageSquare, label: 'Content Studio' },
        { path: '/dashboard/activity', icon: Activity, label: 'Agent Activity' },
    ];

    const handleLogout = () => {
        localStorage.removeItem('isLoggedIn');
        navigate('/');
    };

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
        <aside className={`border-r border-white/10 glass-card !rounded-none !shadow-none !border-y-0 !border-l-0 h-full flex flex-col transition-all duration-300 ease-in-out ${isOpen ? 'w-64' : 'w-[60px]'}`}>
            <div className={`p-6 flex items-center ${isOpen ? 'justify-between' : 'justify-center'} h-20`}>
                <div className={`overflow-hidden transition-opacity duration-300 ${isOpen ? 'opacity-100 flex-1' : 'opacity-0 w-0 flex-none'}`}>
                    <h1 className="text-2xl font-bold text-primary tracking-wider whitespace-nowrap">NEXUS</h1>
                    <p className="text-[10px] text-text-secondary mt-1 tracking-widest uppercase whitespace-nowrap">Command</p>
                </div>
                <button 
                    onClick={toggleSidebar} 
                    className={`text-text-secondary hover:text-white p-1 rounded-md hover:bg-gray-800 transition-colors flex-shrink-0`}
                    title={isOpen ? "Collapse Sidebar" : "Expand Sidebar"}
                >
                    {isOpen ? <ChevronLeft size={20} /> : <Menu size={20} />}
                </button>
            </div>

            <nav className="flex-1 px-3 space-y-2 mt-2 overflow-y-auto overflow-x-hidden">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    return (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            title={!isOpen ? item.label : undefined}
                            className={({ isActive }) => `flex items-center space-x-3 py-3 rounded-lg transition-colors ${isActive
                                    ? 'bg-primary/10 text-primary'
                                    : 'text-text-secondary hover:bg-gray-800/50 hover:text-white'
                                } ${isOpen ? 'px-4 w-full' : 'px-0 justify-center w-full'}`}
                        >
                            <Icon size={20} className="flex-shrink-0" />
                            <span className={`font-medium whitespace-nowrap overflow-hidden transition-all duration-300 ${isOpen ? 'opacity-100 w-auto' : 'opacity-0 w-0 hidden'}`}>
                                {item.label}
                            </span>
                        </NavLink>
                    );
                })}
            </nav>

            {/* Agent Status Sidebar Section */}
            <div className={`p-4 border-t border-white/10 transition-all duration-300 ${!isOpen ? 'px-2' : ''}`}>
                <h3 className={`text-xs font-semibold text-text-secondary uppercase tracking-wider mb-4 transition-all duration-300 ${isOpen ? 'px-2' : 'hidden'}`}>
                    Swarm Status
                </h3>
                <div className="space-y-3 px-1">
                    {agentStatus.map(agent => (
                        <div key={agent.name} className={`flex items-center ${isOpen ? 'justify-between' : 'justify-center'}`} title={!isOpen ? `${agent.name}: ${agent.status}` : undefined}>
                            <div className="flex items-center space-x-3">
                                <div className={`w-2 h-2 rounded-full ${agent.indicator} flex-shrink-0`} />
                                <div className={`overflow-hidden transition-all duration-300 ${isOpen ? 'opacity-100 w-auto' : 'opacity-0 w-0 hidden'}`}>
                                    <div className={`text-sm font-medium ${agent.color} whitespace-nowrap`}>{agent.name}</div>
                                    <div className="text-xs text-gray-500 whitespace-nowrap">{agent.status}</div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className={`p-4 transition-all duration-300 space-y-2 ${!isOpen ? 'px-2' : ''}`}>
                <button 
                    className={`flex items-center space-x-3 py-3 text-text-secondary hover:text-white hover:bg-gray-800/50 rounded-lg transition-colors w-full ${isOpen ? 'px-4' : 'px-0 justify-center'}`}
                    title={!isOpen ? "Settings" : undefined}
                >
                    <Settings size={20} className="flex-shrink-0" />
                    <span className={`font-medium whitespace-nowrap overflow-hidden transition-all duration-300 ${isOpen ? 'opacity-100 w-auto' : 'opacity-0 w-0 hidden'}`}>
                        Settings
                    </span>
                </button>
                <button 
                    onClick={handleLogout}
                    className={`flex items-center space-x-3 py-3 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors w-full ${isOpen ? 'px-4' : 'px-0 justify-center'}`}
                    title={!isOpen ? "System Logout" : undefined}
                >
                    <LogOut size={20} className="flex-shrink-0" />
                    <span className={`font-medium whitespace-nowrap overflow-hidden transition-all duration-300 ${isOpen ? 'opacity-100 w-auto' : 'opacity-0 w-0 hidden'}`}>
                        System Logout
                    </span>
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
