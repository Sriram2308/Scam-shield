# ScamShield Bharat

A multilingual scam-message checker for first-time digital users. Paste a suspicious SMS or WhatsApp message and get a verdict, a plain-language reason in **English, Tamil or Hindi**, and the next steps to take (call 1930, report at cybercrime.gov.in).

Built for the *Hack for Social Cause* challenge, theme: **Digital Safety & Cyber Fraud Awareness**.

## The problem
Fake KYC, bank-block, lottery, job-fee, parcel and UPI-refund messages target people who have just started using UPI and WhatsApp. Most checkers are English-only and say "scam" with no reason, so users don't learn to spot the next one.

## What the prototype does
1. **Classifies** a message with a TF-IDF (character n-gram) + logistic regression model, blended with transparent rule signals (urgency, OTP/PIN request, fee demand, threat, suspicious link). Character n-grams let it handle Tamil, Hindi and transliterated text.
2. **Names the scam type** (KYC/bank, lottery, job offer, UPI refund, parcel, loan app).
3. **Explains** in the user's language from a vetted advisory knowledge base and lists clear next steps with official reporting links.

> The baseline is trained on a small hand-made sample set (`data/sample_messages.csv`, 34 messages). It demonstrates the pipeline; it is not a production-grade detector. See *Roadmap* for the BERT and RAG upgrade.

## Quick start
```bash
git clone <your-repo-url> && cd scamshield
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # no secrets needed
uvicorn app.main:app --reload --port 8000
```
Open http://localhost:8000.

API example:
```bash
curl -X POST localhost:8000/api/check -H "Content-Type: application/json" \
  -d '{"message":"Your account will be blocked. Update KYC at http://sbi-kyc.xyz and share OTP","lang":"ta"}'
```

## Environment variables
See `.env.example`. The baseline needs none.

## Tests
```bash
pytest -q
```
Covers scam and safe messages in English and Tamil, scam-type detection, API responses in all three languages, and input validation.

## Project layout
```
app/classifier.py    model + rule signals
app/advisor.py       language-specific explanations and steps
app/main.py          FastAPI app (/api/check, /health)
app/static/          web UI
data/                sample messages, advisory knowledge base
docs/ARCHITECTURE.md design document with diagrams
tests/               pytest suite
```

## Roadmap
- Fine-tune a multilingual transformer (e.g. `bert-base-multilingual-cased`) on public SMS-spam data plus collected scam samples, and compare against this baseline.
- Replace the advisory lookup with LangChain + ChromaDB retrieval over RBI, NPCI and I4C advisories.
- WhatsApp/Telegram bot, screenshot OCR, anonymized trending-scams dashboard.
- Pilot with real users and report precision/recall and before-vs-after scam-spotting.

## License
MIT. See `LICENSE`.
