# SafeGuard AI - AI-Powered Scam Identification Platform

## 🆕 AI Analysis Mode

This version uses **Large Language Models (LLM)** to intelligently analyze user responses, replacing simple keyword matching with sophisticated AI understanding.

## ✨ New Features

### 1. AI-Powered Analysis
- Uses Gemini or Zhipu AI to understand user responses
- Intelligent scoring based on comprehension, not just keywords
- Detailed personalized feedback

### 2. Multi-Level Scoring System
| Score | Level | Criteria |
|-------|-------|----------|
| 100 | Excellent | All warning signs identified with correct reasoning |
| 80 | Good | Most signs identified (≥70%) with good reasoning |
| 60 | Moderate | Half signs identified (≥50%) with some reasoning |
| 40 | Fair | Few signs identified (≥30%) with minimal reasoning |
| 20 | Poor | Failed to identify signs (<30%) |

### 3. Smart Fallback
- If AI API is unavailable, automatically falls back to keyword matching
- Ensures the system always works

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install flask requests python-dotenv
```

### 2. Configure API Keys

#### Option A: Use Google Gemini (Recommended - Free Tier Available)
1. Get API key: https://makersuite.google.com/app/apikey
2. Create `.env` file:
```env
ACTIVE_MODEL=openai
OPENAI_API_KEY=your_gemini_api_key_here
MOCK_MODE=False
```

#### Option B: Use Zhipu AI (智谱AI)
1. Get API key: https://open.bigmodel.cn/
2. Create `.env` file:
```env
ACTIVE_MODEL=zhipu
ZHI_KEY=your_zhipu_api_key_here
MOCK_MODE=False
```

### 3. Run Application
```bash
python app.py
```

### 4. Access Web Interface
Open browser: http://localhost:5000

## 🧪 Testing AI Analyzer

Run the test script to verify AI analysis works:

```bash
python test_ai_analyzer.py
```

This will test 3 sample responses with different quality levels.

## 📊 API Endpoints

### New Endpoint: `/api/analyze-response`
Analyzes user response using AI

**Request:**
```json
POST /api/analyze-response
{
  "scenario": {
    "title": "Fake Driving School",
    "content": "Scam message...",
    "sender": "Coach Li",
    "red_flags": [...]
  },
  "user_response": "User's analysis..."
}
```

**Response:**
```json
{
  "success": true,
  "score": 80,
  "percentage": 75,
  "level": "good",
  "response_type": "reject",
  "identified_risks": [...],
  "missed_risks": [...],
  "feedback": "AI-generated personalized feedback...",
  "reasoning": "Explanation of the score"
}
```

## 🎯 How AI Analysis Works

### 1. Prompt Engineering
The system builds a detailed prompt that includes:
- Scenario content
- Expected warning signs
- User's response
- Scoring criteria

### 2. AI Evaluation
The AI model:
- Understands natural language nuances
- Identifies implied risks (not just exact keywords)
- Evaluates reasoning quality
- Provides personalized feedback

### 3. Structured Output
AI returns JSON with:
- Score (20-100)
- Identified risks
- Missed risks
- Personalized feedback
- Reasoning explanation

## ⚙️ Configuration Options

### In `config.py`:
```python
# Choose AI model
ACTIVE_MODEL = "openai"  # or "zhipu"

# API settings
API_TIMEOUT = 60
API_MAX_RETRIES = 3

# Temperature for AI responses
JUDGE_TEMPERATURE = 0.3  # Lower = more consistent
```

## 🔧 Troubleshooting

### Issue: "API call failed"
**Solution:** Check your API key in `.env` file

### Issue: "AI analysis unavailable"
**Solution:** System will fallback to keyword matching automatically

### Issue: Slow responses
**Solution:** AI analysis takes 2-5 seconds. This is normal.

## 📈 Advantages Over Keyword Matching

| Feature | Keyword Matching | AI Analysis |
|---------|-----------------|-------------|
| Understands synonyms | ❌ | ✅ |
| Detects implied meaning | ❌ | ✅ |
| Provides personalized feedback | ❌ | ✅ |
| Evaluates reasoning quality | ❌ | ✅ |
| Works offline | ✅ | ❌ |
| Speed | Fast | Slower (2-5s) |

## 🎓 Example Usage

**Scenario:** Fake Driving School scam

**User Response:**
"This is suspicious. They promise to bypass the exam, which is illegal. They want upfront payment to a personal account, not an official school account."

**AI Analysis:**
- Score: 100
- Level: Excellent
- Feedback: "Outstanding analysis! You correctly identified all three warning signs: the illegal promise of bypassing the exam, the request for upfront payment, and the use of a personal account. Your reasoning demonstrates excellent scam awareness."

## 🔐 Security Notes

- API keys are stored in `.env` file (not committed to git)
- User data is processed securely
- No personal information is sent to AI APIs

## 📝 License

This project is for educational purposes only.

---

**Need help?** Check the logs in console or contact support.
