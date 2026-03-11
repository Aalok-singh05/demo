import CommandBar from './CommandBar';
import Sidebar from './Sidebar';

const Layout = ({ children, activeTab, setActiveTab }) => {
    return (
        <div className="flex h-screen bg-background text-text-primary overflow-hidden font-sans">
            {/* Fixed Sidebar */}
            <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col relative overflow-hidden">
                {/* Fixed Top Command Bar */}
                <CommandBar />

                {/* Scrollable Page Content */}
                <main className="flex-1 overflow-y-auto p-6 scroll-smooth">
                    <div className="max-w-7xl mx-auto">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
};

export default Layout;
