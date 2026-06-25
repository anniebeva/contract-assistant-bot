# Contract Assistant Bot

Telegram bot for contract risk assessment. Analyzes text or files (PDF/DOCX), detects policy violations, and provides recommendations.

## Features

- Accepts contract text as a message or as a PDF/DOCX file
- Detects common violations: penalty >10%, unilateral changes, missing force majeure, payment term <5 days, unauthorized debiting
- Guardrails against prompt injection (role switching, ignoring instructions)
- Rejects off‑topic questions (cooking, taxes, etc.)
- Escalates to a human when user asks for a live lawyer
- Explains legal terms (penalty, offer, force majeure) when asked
- Conversation history (last 10 messages)
- Commands: `/start`, `/reset`

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```
3. Install dependencies
```
bash
pip install -r requirements.txt
```

4. Copy .env.example to .env and fill in your tokens:
```env
TELEGRAM_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
```

5. Run the bot:
```
bash
python main.
```

## Usage

- Start the bot with /start
- Send a contract as a text message or as a PDF/DOCX file
- Use /reset to clear the conversation history

## Example
User:
"Check this contract: penalty 20% of the amount, payment within 2 days, no force majeure, supplier may unilaterally change the price."

Bot:

```
text
Violations:
1. Penalty 20% > 10% – exceeds policy limit. Recommendation: max 10%.
2. Payment term 2 days < 5 days – too short. Recommendation: at least 5 working days.
3. No force majeure clause – add according to Civil Code.
4. Unilateral price change – prohibited. Recommendation: price changes by mutual agreement.

This is a preliminary analysis, not a legal opinion.
```

User (knowledge base question):
"What is a penalty?"

Bot:

```
text
A penalty (forfeit, fine) is a monetary amount that the debtor must pay to the creditor in case of non‑performance or improper performance of obligations. It is regulated by Article 330 of the Civil Code of the Russian Federation.

If you want to check a specific contract for risks, please send its text.
```

## Knowledge Base
The bot searches for answers in mock_knowledge_base/.
You can add, remove, or edit .md files in that folder. The bot will automatically use them.

- Current files: company policies, FAQ, force majeure policy, penalty calculation, contract termination rules.
- Retrieval method: keyword matching (simple, no embeddings).
- Limitation: The bot finds paragraphs that contain the same words as the user's question. For semantic search, consider replacing with embeddings + vector DB

## Security Measures
- Only PDF and DOCX files are accepted.
- Maximum file size: 10 MB.
- Files are processed in memory; never saved to disk.
- Antivirus scanning is not implemented in this demo, but the code includes a placeholder (# TODO) for integration with VirusTotal or ClamAV in production.
- System prompt includes guardrails to prevent prompt injection and off‑topic responses.

## Tech Stack
- Python 3.11+
- python-telegram-bot
- Groq API (Llama 3.1‑8b‑instant)
- PyPDF, python-docx
- python-dotenv
- Keyword-based retrieval from local Markdown files
- Flask (for webhook deployment on PythonAnywhere / Render)

## Deployment
The bot can be deployed on PythonAnywhere or Render.com as a Web Service with webhooks.

1. Push the code to GitHub.
2. On the platform, create a Web Service and connect your repo.
3. Set:
- Build Command: pip install -r requirements.txt
- Start Command: gunicorn app:app
4. Add all environment variables (from .env) in the dashboard.
5. Deploy. The bot will be available at https://your-service.onrender.com (or your-username.pythonanywhere.com).

Note: The bot uses app.py with Flask and webhooks for production. main.py is kept for local testing only.