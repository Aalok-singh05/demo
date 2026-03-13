import { useState, useRef } from 'react';
import { Search, Bell, Send, Loader2, Cpu } from 'lucide-react';
import { invokeAgent } from '../../services/api';
import { useNavigate } from 'react-router-dom';

const CommandBar = () => {
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState(null);
    const [showPanel, setShowPanel] = useState(false);
    const inputRef = useRef(null);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e?.preventDefault();
        if (!input.trim() || loading) return;
        setLoading(true);
        setShowPanel(true);
        try {
            // Using the single centralized LangGraph orchestrator endpoint!
            const result = await invokeAgent(input);
            setResponse(result);
            setInput('');
        } catch (err) {
            setResponse({ error: 'Failed to reach Nexus Core orchestrator. Please try again.' });
        }
        setLoading(false);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
        if (e.key === 'Escape') {
            setShowPanel(false);
            setResponse(null);
        }
    };

    return (
        <>
            <header className="h-16 border-b border-white/10 glass-card !rounded-none !shadow-none !border-x-0 !border-t-0 flex items-center justify-between px-6 sticky top-0 z-10 w-full">
                <form onSubmit={handleSubmit} className="flex-1 max-w-2xl relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        {loading ? <Loader2 size={18} className="text-primary animate-spin" /> : <Search size={18} className="text-gray-500" />}
                    </div>
                    <input
                        ref={inputRef}
                        type="text"
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Command the Swarm (e.g. 'Draft a tweet about the new schedule' or 'Find sponsors')"
                        className="w-full bg-black/40 border border-white/10 rounded-lg pl-10 pr-20 py-2 text-sm text-text-primary focus:outline-none focus:border-white/30 focus:ring-1 focus:ring-white/30 transition-all placeholder-gray-500"
                    />
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center gap-2">
                        {input.trim() && (
                            <button type="submit" className="text-primary hover:text-white transition-colors">
                                <Send size={14} />
                            </button>
                        )}
                        <span className="text-xs text-gray-500 font-mono bg-gray-800 px-1.5 py-0.5 rounded border border-gray-700">⌘K</span>
                    </div>
                </form>

                <div className="flex items-center space-x-4 ml-6">
                    <button 
                        onClick={() => navigate('/dashboard/approvals')}
                        className="relative p-2 text-text-secondary hover:text-white transition-colors"
                        title="Pending Approvals"
                    >
                        <Bell size={20} />
                        {/* We will later hook this glow up to the websocket context! */}
                        <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-error rounded-full animate-pulse"></span>
                    </button>
                    <div className="flex items-center space-x-3 pl-4 border-l border-white/10">
                        <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold border border-primary/30">
                            YO
                        </div>
                        <div className="hidden md:block">
                            <div className="text-sm font-medium">Event Organizer</div>
                            <div className="text-xs text-text-secondary">Admin</div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Nexus Core Response Panel */}
            {showPanel && response && (
                <div className="border-b border-primary/30 bg-primary/5 px-6 py-4 backdrop-blur-sm relative z-10 w-full transition-all">
                    <div className="max-w-4xl mx-auto">
                        <div className="flex items-start gap-3">
                            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0 mt-0.5">
                                <Cpu size={16} className="text-white" />
                            </div>
                            <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                    <span className="text-primary font-semibold text-sm">Nexus Orchestrator Response</span>
                                </div>
                                
                                {response.error ? (
                                     <p className="text-sm text-error mb-3">{response.error}</p>
                                ) : (
                                    <>
                                        <p className="text-sm text-gray-300 mb-3">Command received and delegated to the Swarm.</p>
                                        <div className="bg-background/50 border border-gray-800 rounded-lg p-3 overflow-x-auto">
                                            <div className="text-[10px] text-gray-500 uppercase font-semibold mb-2">Internal State Update</div>
                                            <pre className="text-xs text-info font-mono">
                                                {JSON.stringify(response, null, 2)}
                                            </pre>
                                        </div>
                                    </>
                                )}
                            </div>
                            <button onClick={() => { setShowPanel(false); setResponse(null); }} className="text-gray-500 hover:text-white text-xs">✕</button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default CommandBar;
