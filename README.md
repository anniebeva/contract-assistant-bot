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
3. Install dependencies

bash
pip install -r requirements.txt

4. Copy .env.example to .env and fill in your tokens:
env
TELEGRAM_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key

5. Run the bot:

bash
python main.py

## Usage

- Start the bot with /start
- Send a contract as a text message or as a PDF/DOCX file
- Use /reset to clear the conversation history

## Example
User:
"Check this contract: penalty 20% of the amount, payment within 2 days, no force majeure, supplier may unilaterally change the price."

Bot:
text
Violations:
1. Penalty 20% > 10% – exceeds policy limit. Recommendation: max 10%.
2. Payment term 2 days < 5 days – too short. Recommendation: at least 5 working days.
3. No force majeure clause – add according to Civil Code.
4. Unilateral price change – prohibited. Recommendation: price changes by mutual agreement.

This is a preliminary analysis, not a legal opinion.

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