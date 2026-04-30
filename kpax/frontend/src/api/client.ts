const API_BASE = "";

export interface ContextField {
  field_id: string;
  label: string;
  description: string;
  input_type: "select" | "multi_select" | "slider" | "tags" | "text";
  options?: { value: string; label: string }[];
  slider_config?: { min: number; max: number; step: number; unit: string };
  required: boolean;
}

export interface StartResponse {
  session_id: string;
  question_type: string;
  question_summary: string;
  context_fields: ContextField[];
}

export interface Expert {
  name: string;
  role: string;
  perspective: string;
  stance_hint: string;
}

export interface ContextResponse {
  session_id: string;
  experts: Expert[];
  analysis_angles: string[];
  core_tension: string;
}

export interface ReportData {
  executive_summary: string;
  question_reframe: string;
  pro_arguments: { point: string; evidence: string; expert: string }[];
  con_arguments: { point: string; evidence: string; expert: string }[];
  key_disagreements: { topic: string; positions: string[] | Record<string, string> }[];
  blind_spots: string[];
  action_items: { action: string; rationale: string; urgency: string }[];
  follow_up_questions: string[];
}

export interface StreamEvent {
  type: "round_start" | "message" | "generating_summary" | "generating_report" | "done" | "error";
  round?: number;
  total_rounds?: number;
  id?: number;
  agent_id?: number;
  agent_name?: string;
  role?: string;
  content?: string;
  round_number?: number;
  index?: number;
  total?: number;
  debate_id?: number;
  report?: ReportData;
  error?: string;
}

const api = {
  startAnalysis: async (question: string): Promise<StartResponse> => {
    const res = await fetch(`${API_BASE}/api/analyze/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  submitContext: async (session_id: string, answers: Record<string, unknown>): Promise<ContextResponse> => {
    const res = await fetch(`${API_BASE}/api/analyze/context`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id, answers }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  supplement: async (session_id: string, text: string) => {
    const res = await fetch(`${API_BASE}/api/analyze/supplement`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id, text }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  runAnalysis: (session_id: string) => {
    return fetch(`${API_BASE}/api/analyze/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id }),
    });
  },

  getReport: async (session_id: string) => {
    const res = await fetch(`${API_BASE}/api/report/${session_id}`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  followUp: async (session_id: string, question: string) => {
    const res = await fetch(`${API_BASE}/api/report/${session_id}/followup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
};

export default api;
