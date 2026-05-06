# Prepzo.ai

> "We are not another AI study tool — we are a decision engine that tells students exactly what to study when time is limited."

Prepzo is a Deadline-Aware Exam Preparation Engine. It figures out how much time a student has, prioritizes what matters most (Pareto principle), and generates a personalized preparation plan with high-probability questions.

## Features & USP
1. **Deadline Mode:**
   - **≤ 3 days** → Survival Mode
   - **4–7 days** → Balanced Mode
   - **> 7 days** → Full Mode
2. **Priority System:**
   - 🔴 Must Do
   - 🟡 Should Do
   - ⚪ Optional
3. **Outcome Driven Strategy:** "Solve these X questions to maximize chances of passing."
4. **Pareto Engine:** Focuses on the top 30% topics that carry 70% of the marks.

---

## Team Execution Plan & Roles

### 1. Yash: Backend Lead + Deadline Engine + AI Integration
- **Independent Task:** Set up FastAPI project, OTP auth, deadline logic stub, output schema
- **Core APIs:** `/send-otp`, `/verify-otp`, `/analyze-input`, `/generate-plan`, `/chat`
- **Logic:** Deadline Mode, LLM call with retry + schema normalization, In-memory storage

### 2. Rudransh: Frontend — React UI
- **Independent Task:** Create React project, all page routes, static UI components, dark theme
- **UI Elements:** Auth page, Input page (chips, PDF upload), Result page (Mode banner, Pareto plan card), Filters, Chatbot UI

### 3. Mridul: AI & Prompt Engineering
- **Independent Task:** Write + test master prompt in ChatGPT Playground, design fallback prompt
- **Prompt Logic:** Strict JSON schema, Mode-aware instructions, Post-processing rules (no dupes, sorted by prob)

### 4. Anuj: Data & Priority Logic
- **Independent Task:** Map all SESD topics to priority scores (Observer, Strategy, SOLID, etc.)
- **Logic:** Extract topics, High/Medium/Low priority mapping
- **Weight Formula:** `final_priority = AI_prob * topic_weight`

### 5. Karan: Chatbot + Testing + Analytics + PPT
- **Independent Task:** Build PPT skeleton, write test cases, design analytics schema
- **Flow:** Chatbot intents (Explain Q#3, Simplify), Full flow testing, Analytics tracking, Demo PPT

---

## Dependency Order
| Phase | Who | Depends On | Unlocks |
|---|---|---|---|
| 1 — Foundation | Anuj | Nobody | Topic weights → feeds Rudransh + Yash |
| 1 — Foundation | Mridul | Rudransh (topics) | Master prompt → feeds Yash |
| 2 — Core Build | Yash | Rudransh + Mridul | All APIs → unblocks Anuj + Karan |
| 3 — UI + Bot | Rudransh | Yash (APIs) | Full UI → enables Karan to test |
| 4 — Polish | Karan | Anuj + Yash | Testing, analytics, demo PPT |

---

## 3-Day Execution Timeline

| | Yash | Rudransh | Mridul | Anuj | Karan |
|---|---|---|---|---|---|
| **Day 1** | Auth APIs + deadline logic | All pages (static UI) | Prompt v1 in Playground | Topic priority map | PPT skeleton + test cases |
| **Day 2** | AI integration + `/generate-plan` | Hit APIs, result page live | Prompt finalised + fallback | Weights JSON to Yash | Chatbot flow + analytics |
| **Day 3** | Bug fixes + deploy | Polish + chatbot UI | Output QA | Pareto data ready | 25 users + full test + demo |

---

## System Flow
**Frontend (Rudransh) → Deadline Engine (Yash) → AI + Prompt (Mridul) → Priority Weights (Anuj) → Chatbot + Demo (Karan)**
