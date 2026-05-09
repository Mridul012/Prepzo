import { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Navbar from '../components/Navbar';
import ChatBubble from '../components/ChatBubble';
import { chatWithBot } from '../services/api';
import { track } from '../utils/analytics';
import { useViewport } from '../hooks/useViewport';
import { useStudyPlanContext } from '../hooks/useStudyPlanContext';

const pageVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
};

function ArrowRightIcon({ size = 16, color = '#FFFFFF' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3.33 8H12.67M12.67 8L8.67 4M12.67 8L8.67 12" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function ChatPage() {
  const location = useLocation();
  const { isMobile } = useViewport();
  const navigate = useNavigate();

  const getStoredData = () => {
    try {
      return JSON.parse(localStorage.getItem('prepzo_last_result') || '{}');
    } catch {
      return {};
    }
  };

  const rawState = location.state;
  const stored = getStoredData();

  const plan = rawState?.plan || stored?.plan || null;
  const subject = rawState?.subject || stored?.subject || '';
  const examDate = rawState?.examDate || stored?.examDate || '';

  // Pattern analysis is stored separately (comes from PDF upload, not plan generation)
  const patternAnalysis = stored?.patternAnalysis || null;

  // Build the structured context object for the chatbot (memoised)
  const chatContext = useStudyPlanContext(plan, subject, examDate, patternAnalysis);

  useEffect(() => {
    if (!plan) navigate('/input', { replace: true });
  }, []); // only on mount — don't re-run on every render

  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: plan
        ? `Hey! I'm Prepzo, your AI study assistant. I have your ${plan.mode} plan loaded. Ask me anything about your topics, questions, or study strategy!`
        : `Hey! I'm Prepzo. Loading your plan...`,
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const handleSend = async (textOverride) => {
    const textToSend = textOverride || input;
    if (!textToSend.trim() || loading) return;

    const newMessages = [...messages, { role: 'user', content: textToSend }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    track.chatbotMessageSent(textToSend.length);

    try {
      const response = await chatWithBot(newMessages, chatContext);
      setMessages([...newMessages, { role: 'assistant', content: response.data.reply, isNew: true }]);
    } catch {
      setMessages([
        ...newMessages,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' },
      ]);
      track.errorOccurred('chat', 'Chat API request failed');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSend();
  };

  const modeColor = plan?.mode === 'survival' ? '#E8341C' : plan?.mode === 'balanced' ? '#D4910A' : '#0D9E6E';

  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={{ duration: 0.4 }}
      style={{
        background: '#F5F5F5',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Navbar />

      <div
        style={{
          background: '#FFFFFF',
          borderBottom: '1px solid #E0E0E8',
          padding: '16px 24px',
          marginTop: 56, // below navbar
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
          <button
            onClick={() => navigate('/result', { state: { plan, subject, examDate } })}
            style={{
              background: 'none',
              border: 'none',
              fontFamily: "'DM Mono', monospace",
              fontSize: 12,
              color: '#6B6B80',
              cursor: 'pointer',
              padding: 0,
            }}
            onMouseEnter={(e) => (e.target.style.color = '#6C63FF')}
            onMouseLeave={(e) => (e.target.style.color = '#6B6B80')}
          >
            ← Back to Plan
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span
              style={{
                fontFamily: "'Sora', sans-serif",
                fontWeight: 600,
                fontSize: 18,
                color: '#0A0A0F',
                letterSpacing: '-0.02em',
              }}
            >
              Prepzo Chat
            </span>
            <span
              style={{
                display: 'inline-block',
                border: `1px solid ${modeColor}`,
                color: modeColor,
                borderRadius: 999,
                padding: '2px 8px',
                fontFamily: "'DM Mono', monospace",
                fontSize: 10,
                textTransform: 'uppercase',
                letterSpacing: '0.04em',
              }}
            >
              {plan?.mode}
            </span>
          </div>
        </div>
      </div>

      <div
        ref={scrollRef}
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '24px 24px',
          display: 'flex',
          flexDirection: 'column',
          maxWidth: 800,
          margin: '0 auto',
          width: '100%',
        }}
      >
        {messages.map((msg, i) => (
          <ChatBubble key={i} message={msg} />
        ))}
        {loading && <ChatBubble message={{ role: 'assistant', content: '', isTyping: true }} />}
      </div>

      <div
        style={{
          background: '#FFFFFF',
          borderTop: '1px solid #E0E0E8',
          padding: isMobile ? '12px 16px' : '16px 24px',
        }}
      >
        <div style={{ maxWidth: 800, margin: '0 auto' }}>
          {/* chat-actions class lets CSS media query wrap buttons on small screens */}
          <div className="chat-actions" style={{ display: 'flex', gap: 8, marginBottom: 12, overflowX: 'auto', paddingBottom: 4 }}>
            {['💡 Explain Q#1', '📚 More on this topic', '🔄 Simplify'].map((action) => (
              <button
                key={action}
                onClick={() => handleSend(action)}
                style={{
                  background: '#FFFFFF',
                  border: '1px solid #E0E0E8',
                  borderRadius: 999,
                  padding: '7px 16px',
                  fontFamily: "'Sora', sans-serif",
                  fontSize: 13,
                  color: '#6B6B80',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  transition: 'all 0.2s ease',
                }}
                onMouseEnter={(e) => {
                  e.target.style.borderColor = '#6C63FF';
                  e.target.style.color = '#6C63FF';
                }}
                onMouseLeave={(e) => {
                  e.target.style.borderColor = '#E0E0E8';
                  e.target.style.color = '#6B6B80';
                }}
              >
                {action}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', gap: 12 }}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about your plan..."
              style={{
                flex: 1,
                background: '#FFFFFF',
                border: '1.5px solid #E0E0E8',
                borderRadius: 12,
                padding: '14px 16px',
                fontFamily: "'Sora', sans-serif",
                fontSize: 15,
                color: '#0A0A0F',
                outline: 'none',
                transition: 'all 0.2s ease',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#6C63FF';
                e.target.style.boxShadow = '0 0 0 3px rgba(108,99,255,0.12)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#E0E0E8';
                e.target.style.boxShadow = 'none';
              }}
            />
            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || loading}
              style={{
                background: '#0A0A0F',
                color: '#FFFFFF',
                fontFamily: "'Sora', sans-serif",
                fontWeight: 500,
                fontSize: 15,
                border: 'none',
                borderRadius: 999,
                padding: '0 8px 0 20px',
                cursor: !input.trim() || loading ? 'not-allowed' : 'pointer',
                opacity: !input.trim() || loading ? 0.7 : 1,
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              Send
              <span
                style={{
                  background: '#FFFFFF',
                  borderRadius: '50%',
                  padding: 6,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <ArrowRightIcon size={14} color="#0A0A0F" />
              </span>
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
