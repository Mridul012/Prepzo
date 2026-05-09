import { useMemo } from 'react';

/**
 * Builds a clean, summarised context object from the generated study plan.
 *
 * Designed for the chatbot: keeps the payload lightweight by trimming large
 * arrays (schedule → first 5 days, patterns → top 5, questions → key fields
 * only) while preserving all the information the AI needs to answer
 * contextual questions like "What should I revise first?" or "Which topics
 * repeat the most in past papers?".
 *
 * @param {Object|null} plan        - The generated study plan from the backend.
 * @param {string}      subject     - The exam subject.
 * @param {string}      examDate    - ISO date string for the exam.
 * @param {Object|null} patternAnalysis - Pattern analysis from PDF upload (optional).
 * @returns {Object} A memoised context object ready to pass to chatWithBot().
 */
export function useStudyPlanContext(plan, subject, examDate, patternAnalysis = null) {
  return useMemo(() => {
    if (!plan) return null;

    // ── Questions: keep only the fields the AI needs for coaching ──
    const questionsContext = plan.questions?.map((q) => ({
      question: q.question,
      type: q.type,
      difficulty: q.difficulty,
      probability: q.probability,
      priority: q.priority,
      topic: q.topic,
      // Omit solution — the AI can regenerate explanations and it saves tokens
    })) ?? [];

    // ── Study schedule: first 5 days only to avoid token bloat ──
    const studySchedule = plan.studySchedule?.slice(0, 5) ?? null;

    // ── Topic insights: pass as-is (already compact per topic) ──
    const topicInsights = plan.topicInsights ?? null;

    // ── Pattern analysis: trim to top 5 patterns by probability ──
    let trimmedPatternAnalysis = null;
    if (patternAnalysis && patternAnalysis.totalQuestionsAnalyzed > 0) {
      const topPatterns = (patternAnalysis.patterns || [])
        .slice()
        .sort((a, b) => (b.probability || 0) - (a.probability || 0))
        .slice(0, 5)
        .map((p) => ({
          pattern: p.pattern,
          category: p.category,
          frequency: p.frequency,
          probability: p.probability,
        }));

      trimmedPatternAnalysis = {
        totalQuestionsAnalyzed: patternAnalysis.totalQuestionsAnalyzed,
        patterns: topPatterns,
        categoryBreakdown: patternAnalysis.categoryBreakdown ?? {},
        topicCorrelation: patternAnalysis.topicCorrelation ?? {},
      };
    }

    // ── Identify weak topics (lowest probability questions = weakest areas) ──
    const topicProbMap = {};
    for (const q of questionsContext) {
      if (!topicProbMap[q.topic]) topicProbMap[q.topic] = [];
      topicProbMap[q.topic].push(q.probability || 0);
    }
    const weakTopics = Object.entries(topicProbMap)
      .map(([topic, probs]) => ({
        topic,
        avgProbability: probs.reduce((a, b) => a + b, 0) / probs.length,
      }))
      .sort((a, b) => a.avgProbability - b.avgProbability)
      .slice(0, 3)
      .map((t) => t.topic);

    return {
      subject,
      examDate,
      mode: plan.mode,
      focusTopics: plan.focusTopics ?? [],
      questionsContext,
      studySchedule,
      topicInsights,
      patternAnalysis: trimmedPatternAnalysis,
      weakTopics,
    };
  }, [plan, subject, examDate, patternAnalysis]);
}
