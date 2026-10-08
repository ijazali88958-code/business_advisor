# Business Launch Advisor

A Streamlit + CrewAI + Groq multi-agent business planning application.

## What it does

The user enters country, city/region, business idea, size, budget and environment.

The application:
1. Searches for evidence from an approved list of official/public domains.
2. Passes only the retrieved evidence to the consulting agents.
3. Uses CrewAI to define a sequential multi-agent workflow.
4. Uses Groq for language reasoning.
5. Audits the final answer so unsupported facts are marked as "Not verified".

## Important limitation

No AI system can honestly promise zero hallucinations. This app reduces hallucination risk by:
- restricting factual evidence to approved domains;
- separating verified facts from recommendations;
- refusing to invent missing requirements;
- displaying the source URLs used;
- auditing the final answer.

Always confirm legal/tax/licensing requirements with the responsible authority.

## Streamlit Cloud

Put `app.py` and `requirements.txt` in the repository root.

In Streamlit Cloud, select Python 3.12 and add this secret:

```toml
GROQ_API_KEY = "your-key-here"
```

Optional:

```toml
GROQ_MODEL = "openai/gpt-oss-120b"
```
