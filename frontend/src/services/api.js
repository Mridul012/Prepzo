import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

// PDF upload — extract text + detect topics
export const uploadPdf = (file) => {
  const fd = new FormData();
  fd.append('file', file);
  return api.post('/upload-pdf', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// Generate exam preparation plan
export const generatePlan = (data) => api.post('/generate-plan', data);

// AI chatbot — context-aware conversation with full plan context
export const chatWithBot = (
  messages,
  subject,
  examDate,
  mode,
  topics,
  questionsContext,
  studySchedule,
  topicInsights,
) =>
  api.post('/chat', {
    messages,
    subject,
    examDate,
    mode,
    topics,
    questionsContext,
    // Enhanced context: study schedule (first 5 days) + ML predictions
    studySchedule: studySchedule?.slice(0, 5) ?? null,
    topicInsights: topicInsights ?? null,
  });

// Analytics — get platform stats
export const getAnalytics = () => api.get('/analytics');

// Analytics — track an event
export const trackEvent = (eventType) =>
  api.post(`/analytics/track?event_type=${encodeURIComponent(eventType)}`);

export default api;
