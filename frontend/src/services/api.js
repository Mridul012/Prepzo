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

// AI chatbot — context-aware conversation with full plan context.
// Accepts a structured context object (from useStudyPlanContext hook) so
// all plan data flows to the backend in a single, well-typed payload.
export const chatWithBot = (messages, context = {}) =>
  api.post('/chat', {
    messages,
    subject: context.subject ?? null,
    examDate: context.examDate ?? null,
    mode: context.mode ?? null,
    topics: context.focusTopics ?? null,
    questionsContext: context.questionsContext ?? null,
    // Enhanced context: schedule, ML predictions, pattern analysis, weak topics
    studySchedule: context.studySchedule ?? null,
    topicInsights: context.topicInsights ?? null,
    patternAnalysis: context.patternAnalysis ?? null,
    weakTopics: context.weakTopics ?? null,
  });

// Analytics — get platform stats
export const getAnalytics = () => api.get('/analytics');

// Analytics — track an event
export const trackEvent = (eventType) =>
  api.post(`/analytics/track?event_type=${encodeURIComponent(eventType)}`);

export default api;
