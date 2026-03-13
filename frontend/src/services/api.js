/**
 * NEXUS API Service — Centralized client for all backend endpoints.
 * All calls include error handling and return parsed JSON.
 */

const API_BASE = '/api';

async function request(path, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error(`[API] ${options.method || 'GET'} ${path} failed:`, err);
    throw err;
  }
}

// ── Dashboard & Activity ─────────────────────────────────────
export const getDashboard = () => 
  request('/events/default_event').catch(err => {
    console.warn("Default event not found, returning mock data");
    return {
      name: "TechSummit 2026",
      status: "planning",
      finance_output: null
    };
  }); // Gets the current event state
export const getActivity = () => request('/activity');              // Gets the agent logs
export const getApprovals = () => request('/approvals');            // Will get pending approvals (needs backend route if not exist)
export const handleApproval = (id, action) =>
  request(`/approval/${id}?decision=${encodeURIComponent(action)}`, {
    method: 'POST',
  });

// ── File Uploads (Event Dispatcher Trigger) ──────────────────
export const uploadParticipants = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  // Matches our actual backend route for CSV uploads
  const res = await fetch(`${API_BASE}/upload/participants`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Upload failed');
  return res.json();
};

// ── The Centralized Agent Invoker ────────────────────────────
// Replaces ALL previous generation endpoints (optimize, generate, sendBatch, sendChat)
export const invokeAgent = (message, requestType = "general") =>
  request(`/agents/invoke?user_input=${encodeURIComponent(message)}&request_type=${encodeURIComponent(requestType)}`, {
    method: 'POST',
  });

// Helper functions that wrap the centralized invoker
export const sendChat = (message) => invokeAgent(message, "general");
export const optimizeSchedule = (prompt) => invokeAgent(prompt || "Optimize the schedule", "schedule");
export const generateContent = (prompt) => invokeAgent(prompt || "Generate content", "content");
export const personalizeEmails = (prompt) => invokeAgent(prompt || "Draft emails", "mail");
export const analyzeData = (prompt) => invokeAgent(prompt || "Analyze the data", "analytics");
export const calculateBudget = (prompt) => invokeAgent(prompt || "Calculate the budget", "finance");

// ── State Read-Only (Direct DB queries) ──────────────────────
export const getSessions = () => request('/schedule');
export const getContentQueue = () => request('/content');

// ── Missing Additional API Exports ───────────────────────────
export const getAgentStatus = () => request('/agents/status').then(res => res.agents || []);
export const getParticipants = () => request('/participants');
export const sendBatch = (prompt) => invokeAgent(prompt || "Send emails", "mail");
export const getInsights = async () => []; // Mocked as no backend route exists yet
export const approveContent = (id) => handleApproval(id, 'approve');
export const getAgentState = async () => null; // Mocked state
export const getAgentLogs = () => getActivity().then(res => res.activities || []);
