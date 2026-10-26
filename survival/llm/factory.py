import os

from survival.llm.fallback import FallbackLLM
from survival.llm.openai_compat import OpenAICompatLLM

# name, base URL, key variable in .env, model, extra settings, token padding
# VERIFY each model name in the provider's own model list before relying on it.
PROVIDERS = [
    ("groq-gpt-oss-20b", "https://api.groq.com/openai/v1", "GROQ_API_KEY",
     "openai/gpt-oss-20b", {"reasoning_effort": "low"}, 1000),
    ("groq-gpt-oss-120b", "https://api.groq.com/openai/v1", "GROQ_API_KEY",
     "openai/gpt-oss-120b", {"reasoning_effort": "low"}, 1000),
    ("gemini", "https://generativelanguage.googleapis.com/v1beta/openai", "GEMINI_API_KEY",
     "gemini-2.5-flash", {}, 1000),
    ("openrouter", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY",
     "meta-llama/llama-3.3-70b-instruct:free", {}, 0),
]


def build_llm():
    providers = []
    for name, url, key_var, model, extra, padding in PROVIDERS:
        key = os.environ.get(key_var)
        if key:
            providers.append(OpenAICompatLLM(name, url, key, model, extra, padding))
    if not providers:
        raise ValueError("No API keys found. Set at least GROQ_API_KEY in .env")
    return FallbackLLM(providers)