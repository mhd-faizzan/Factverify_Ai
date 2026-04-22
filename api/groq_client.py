import html
from datetime import datetime
from groq import Groq
from config.settings import get_groq_api_key

MAX_PROMPT_LENGTH = 2000

_SYSTEM_PROMPT = """You are a senior academic researcher and fact-checker. Your task is to:

1. Provide accurate, well-researched information current to {date}
2. Verify claims with evidence-based reasoning
3. Cite 3-5 reliable academic sources
4. Be transparent about limitations or uncertainties

Format your response as:
- Clear, factual answer
- Evidence and reasoning
- Sources section with format: [Title](URL) - Author (Year) or DOI:...

Separate your main response from sources using ###SOURCES### as a divider."""


def sanitize(text: str) -> str:
    # escape HTML special chars so LLM output can't inject tags into the UI
    return html.escape(text)


def get_verified_response(prompt: str) -> tuple[str | None, list[str]]:
    if len(prompt) > MAX_PROMPT_LENGTH:
        return None, [f"Query too long. Please keep it under {MAX_PROMPT_LENGTH} characters."]

    try:
        client = Groq(api_key=get_groq_api_key())
        system = _SYSTEM_PROMPT.format(date=datetime.now().strftime("%B %Y"))

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000,
            top_p=0.9,
            stream=True,
        )

        full_response = "".join(
            chunk.choices[0].delta.content
            for chunk in completion
            if chunk.choices[0].delta.content
        )

        if "###SOURCES###" in full_response:
            main, raw_sources = full_response.split("###SOURCES###", 1)
            sources = [sanitize(s.strip()) for s in raw_sources.strip().splitlines() if s.strip()]
            return sanitize(main.strip()), sources

        return sanitize(full_response.strip()), []

    except Exception as e:
        return None, ["Something went wrong while fetching the response. Please try again."]
