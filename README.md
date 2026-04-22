# FactVerify AI

Built for **Smart Startup Garage** — a course where we took an idea from scratch to investor pitch. Ours was an AI fact-checker that verifies claims against academic and government sources and returns cited answers.

Pitched it live, demoed the product, got **Grade 1**.

---

## What it does

You type a question or claim. It runs it through an LLM grounded on academic sources (.gov, .edu, DOI) and comes back with a verified answer and citations.

---

## Stack

- **Python + Streamlit** — app and UI
- **Groq (LLaMA 3.1 8B)** — LLM inference
- **Firebase Auth** — login and signup
- **Streamlit Secrets** — keeps credentials out of code

---

## Structure

```
factverify/
├── app.py
├── config/       # page config, CSS, secret getters
├── auth/         # Firebase handlers, session, rate limiting
├── api/          # Groq client
├── ui/           # login page, main app
└── utils/        # greeting, display name helpers
```

---

## Security

- API keys built inside functions, never module-level strings
- LLM output HTML-escaped before rendering (no XSS)
- 5 failed logins → 15 min lockout
- Firebase token auto-expires after 55 min, user gets logged out
- Auth errors are intentionally vague (no email enumeration)
- Prompts capped at 2000 characters

---

## Setup

```bash
pip install -r requirements.txt
```

Add `.streamlit/secrets.toml`:

```toml
[firebase]
api_key = "..."
auth_domain = "..."
project_id = "..."

[groq]
api_key = "..."
```

```bash
streamlit run app.py
```

---

## Context

B2C at €9.99/mo, B2B at €0.01/query. €9.1B TAM. €150K pre-seed ask. Whether any of that happens is another story — but the product works and the pitch scored top marks.
