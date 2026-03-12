import { Link, Navigate } from "react-router-dom";
import { Bot, CalendarDays, Mail, Zap, ChevronRight, ShieldCheck, Activity } from 'lucide-react';
import { WarpBackground } from '../components/layout/WarpBackground';


/* ---------------- LANDING PAGE ---------------- */

const LandingPage = () => {
  if (localStorage.getItem("isLoggedIn") === "true") {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="min-h-screen bg-black bg-light-streaks text-text-primary font-sans overflow-x-hidden selection:bg-primary/30">

      {/* Navigation */}
      <nav className="fixed w-full top-0 z-50 border-b border-white/10 glass-card !rounded-none !shadow-none !border-x-0 !border-t-0">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">

          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-primary/20 border border-primary/50 flex items-center justify-center">
              <Bot className="w-5 h-5 text-primary" />
            </div>
            <span className="text-xl font-bold tracking-wider text-white">NEXUS</span>
          </div>

          <div className="flex items-center space-x-4">
            <Link
              to="/login"
              className="text-text-secondary hover:text-white transition-colors text-sm font-medium"
            >
              Log In
            </Link>

            <Link to="/login" className="btn-primary-glass px-5 py-2.5 text-sm">
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* ---------------- HERO SECTION ---------------- */}

      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 px-6 bg-transparent overflow-hidden">

        {/* Warp Background */}
        <div className="absolute inset-0 z-0">
          <WarpBackground />
        </div>

        {/* Glow Effect */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
          <div className="absolute top-1/2 left-1/2 
          -translate-x-1/2 -translate-y-1/2 
          w-[800px] h-[800px] 
          bg-primary/20 rounded-full 
          blur-[120px] opacity-40" />
        </div>

        {/* Hero Content */}
        <div className="max-w-5xl mx-auto text-center relative z-10">



          <h1 className="text-5xl md:text-7xl font-extrabold text-white tracking-tight mb-8 leading-tight drop-shadow-lg">
            AI-Powered <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-400">
              Event Orchestration
            </span>
          </h1>

          <p className="text-lg md:text-xl text-text-secondary max-w-2xl mx-auto mb-10 leading-relaxed">
            Deploy an autonomous swarm of AI agents to manage your schedules,
            generate content, and handle communications seamlessly.
            Experience the future of event management.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/login"
              className="w-full sm:w-auto px-8 py-4 btn-primary-glass text-lg flex items-center justify-center group shadow-[0_0_30px_rgba(255,255,255,0.1)]"
            >
              Initialize Command
              <ChevronRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>

        </div>
      </section>

      {/* ---------------- STATS ---------------- */}

      <section className="border-y border-white/10 glass-card !rounded-none !shadow-none !border-x-0 relative z-10">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { label: "Active AI Agents", value: "6+" },
              { label: "Tasks Automated", value: "100%" },
              { label: "Uptime Guaranteed", value: "99.9%" },
              { label: "System Latency", value: "<1s" },
            ].map((stat, i) => (
              <div key={i} className="text-center">
                <div className="text-3xl md:text-4xl font-bold tracking-tight text-white mb-2">
                  {stat.value}
                </div>
                <div className="text-sm text-text-secondary uppercase tracking-wider">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ---------------- FEATURES ---------------- */}
{/* 
      <section className="py-24 px-6 relative z-10">
        <div className="max-w-7xl mx-auto flex flex-col items-center">

          <h2 className="text-3xl md:text-4xl font-bold text-white mb-16 text-center">
            Meet Your Autonomous Swarm
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full">
            {[
              {
                title: "Chronos",
                role: "Scheduler",
                icon: CalendarDays,
                color: "text-agents-chronos",
                bg: "bg-agents-chronos/10",
                border: "border-agents-chronos/20",
                desc: "Intelligent conflict resolution and automated itinerary generation.",
              },
              {
                title: "Hermes",
                role: "Communications",
                icon: Mail,
                color: "text-agents-hermes",
                bg: "bg-agents-hermes/10",
                border: "border-agents-hermes/20",
                desc: "Context-aware email delivery and instant stakeholder updates.",
              },
              {
                title: "Athena",
                role: "Analytics",
                icon: Activity,
                color: "text-agents-athena",
                bg: "bg-agents-athena/10",
                border: "border-agents-athena/20",
                desc: "Real-time insights and predictive attendance modeling.",
              },
            ].map((agent, i) => (
              <div
                key={i}
                className="group p-8 glass-card transition-all hover:-translate-y-1 overflow-hidden relative"
              >
                <div
                  className={`w-14 h-14 rounded-xl ${agent.bg} ${agent.border} border flex items-center justify-center mb-6`}
                >
                  <agent.icon className={`w-7 h-7 ${agent.color}`} />
                </div>

                <h3 className="text-2xl font-bold text-white mb-2">
                  {agent.title}
                </h3>

                <div className="text-xs font-semibold text-primary uppercase tracking-wider mb-4">
                  {agent.role}
                </div>

                <p className="text-text-secondary leading-relaxed">
                  {agent.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section> */}

      <section className="py-24 px-6 relative z-10 bg-[#020202]"> 
  <div className="max-w-7xl mx-auto flex flex-col items-center">
    <h2 className="text-3xl md:text-4xl font-bold text-white mb-16 text-center tracking-tight">
      Meet Your Autonomous Swarm
    </h2>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full">
      {[
        {
          title: "Chronos",
          role: "Scheduler",
          icon: CalendarDays,
          color: "text-blue-400",
          glow: "group-hover:shadow-[0_0_40px_-10px_rgba(59,130,246,0.5)]",
          flare: "from-blue-500/20",
          desc: "Intelligent conflict resolution and automated itinerary generation.",
        },
        {
          title: "Hermes",
          role: "Communications",
          icon: Mail,
          color: "text-purple-400",
          glow: "group-hover:shadow-[0_0_40px_-10px_rgba(168,85,247,0.5)]",
          flare: "from-purple-500/20",
          desc: "Context-aware email delivery and instant stakeholder updates.",
        },
        {
          title: "Athena",
          role: "Analytics",
          icon: Activity,
          color: "text-emerald-400",
          glow: "group-hover:shadow-[0_0_40px_-10px_rgba(16,185,129,0.5)]",
          flare: "from-emerald-500/20",
          desc: "Real-time insights and predictive attendance modeling.",
        },
      ].map((agent, i) => (
        <div
          key={i}
          className={`group relative p-8 rounded-2xl transition-all duration-500 
            hover:-translate-y-3 cursor-default
            bg-gradient-to-br from-white/[0.08] to-transparent
            backdrop-blur-2xl border border-white/[0.1]
            hover:border-white/[0.2] ${agent.glow} overflow-hidden`}
        >
          {/* THE GLOW FLARE: A hidden radial gradient that activates on hover */}
          <div className={`absolute -inset-px bg-gradient-to-br ${agent.flare} to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 -z-10`} />

          {/* Icon Container with its own inner glow */}
          <div
            className={`w-14 h-14 rounded-xl flex items-center justify-center mb-6 
              bg-white/[0.05] border border-white/[0.1] 
              group-hover:scale-110 transition-transform duration-500`}
          >
            <agent.icon className={`w-7 h-7 ${agent.color} filter drop-shadow-[0_0_8px_rgba(255,255,255,0.3)]`} />
          </div>

          <h3 className="text-2xl font-bold text-white mb-2">
            {agent.title}
          </h3>

          <div className={`text-xs font-black ${agent.color} uppercase tracking-[0.2em] mb-4`}>
            {agent.role}
          </div>

          <p className="text-slate-300/80 leading-relaxed font-light text-[15px]">
            {agent.desc}
          </p>

          {/* Decorative Corner Light */}
          <div className="absolute top-0 right-0 w-24 h-24 bg-white/[0.02] blur-2xl pointer-events-none" />
        </div>
      ))}
    </div>
  </div>
</section>

      {/* ---------------- FOOTER ---------------- */}

      <footer className="border-t border-white/10 py-12 px-6 relative z-10 bg-black/50">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">

          <div className="flex items-center space-x-2 text-text-secondary">
            <ShieldCheck className="w-5 h-5 text-success" />
            <span className="text-sm">Secured by Nexus Core</span>
          </div>

          <p className="text-sm text-gray-600">
            © {new Date().getFullYear()} AI-Powered Event Orchestration. All systems operational.
          </p>

        </div>
      </footer>

    </div>
  );
};

export default LandingPage;