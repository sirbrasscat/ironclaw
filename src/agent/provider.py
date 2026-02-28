"""
Provider configuration module for IronClaw.

Centralises all provider env-var reading, health checking, and model resolution.
Single contract that both core.py and sandbox.py depend on.
"""

import os
from dataclasses import dataclass
from typing import Optional

import httpx

VALID_PROVIDERS = {"ollama", "gemini", "anthropic", "openai"}

_DEFAULT_OLLAMA_MODEL = "llama3.2"
_DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"


@dataclass
class ProviderConfig:
    provider: str                  # "ollama" | "gemini" | "anthropic" | "openai"
    # Ollama specifics (meaningful only when provider == "ollama")
    ollama_base_url: str           # default: "http://localhost:11434"
    ollama_agent_model: str        # resolved: OLLAMA_AGENT_MODEL or OLLAMA_MODEL
    ollama_codegen_model: str      # resolved: OLLAMA_CODEGEN_MODEL or OLLAMA_MODEL
    # Cloud specifics (None when provider == "ollama")
    gemini_api_key: Optional[str]
    anthropic_api_key: Optional[str]
    openai_api_key: Optional[str]


def get_provider_config() -> ProviderConfig:
    """Read env vars and resolve provider config.

    Provider selection logic:
    - If PROVIDER env var is set (case-insensitive): use it, raise ValueError for unknown values.
    - If PROVIDER not set: auto-detect via key chain:
        GEMINI_API_KEY -> "gemini"
        ANTHROPIC_API_KEY -> "anthropic"
        OPENAI_API_KEY -> "openai"
        (none found) -> "gemini" (default)

    Raises:
        ValueError: if PROVIDER is set to an unknown/unsupported value.
    """
    raw_provider = os.environ.get("PROVIDER", "").strip().lower()

    if raw_provider:
        if raw_provider not in VALID_PROVIDERS:
            raise ValueError(
                f"Unknown PROVIDER={raw_provider!r}. "
                f"Valid values are: {', '.join(sorted(VALID_PROVIDERS))}"
            )
        provider = raw_provider
    else:
        # Auto-detect from available API keys
        if os.environ.get("GEMINI_API_KEY"):
            provider = "gemini"
        elif os.environ.get("ANTHROPIC_API_KEY"):
            provider = "anthropic"
        elif os.environ.get("OPENAI_API_KEY"):
            provider = "openai"
        else:
            provider = "gemini"

    # Resolve Ollama settings (populated regardless of provider; ignored when not ollama)
    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", _DEFAULT_OLLAMA_BASE_URL).rstrip("/")
    ollama_model_fallback = os.environ.get("OLLAMA_MODEL", _DEFAULT_OLLAMA_MODEL)
    ollama_agent_model = os.environ.get("OLLAMA_AGENT_MODEL", ollama_model_fallback)
    ollama_codegen_model = os.environ.get("OLLAMA_CODEGEN_MODEL", ollama_model_fallback)

    return ProviderConfig(
        provider=provider,
        ollama_base_url=ollama_base_url,
        ollama_agent_model=ollama_agent_model,
        ollama_codegen_model=ollama_codegen_model,
        gemini_api_key=os.environ.get("GEMINI_API_KEY"),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
        openai_api_key=os.environ.get("OPENAI_API_KEY"),
    )


class OllamaUnavailableError(Exception):
    """Raised when Ollama health check fails or a required model is not pulled."""
    pass


async def check_ollama_health(config: ProviderConfig) -> tuple[bool, list[str]]:
    """Ping Ollama /api/tags endpoint to verify reachability and list pulled models.

    Args:
        config: Resolved ProviderConfig (ollama_base_url used for the endpoint).

    Returns:
        (reachable, pulled_models) where:
        - reachable: True if HTTP 200 was received.
        - pulled_models: list of model name strings from /api/tags response,
          empty list if unreachable.

    Does NOT raise — callers decide what to do with the result.
    """
    url = f"{config.ollama_base_url}/api/tags"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]
                return True, models
            return False, []
    except (httpx.ConnectError, httpx.TimeoutException, httpx.RequestError):
        return False, []


def get_missing_models(config: ProviderConfig, pulled_models: list[str]) -> list[str]:
    """Return list of required model names not present in pulled_models.

    Checks both ollama_agent_model and ollama_codegen_model (deduplicated).
    Matching: exact string equality first; if a required name has no tag (no
    colon), also matches pulled models whose base name (before ':') equals it.
    This handles Ollama's convention of storing "llama3.2" as "llama3.2:latest".

    Args:
        config: Resolved ProviderConfig.
        pulled_models: List of model name strings from check_ollama_health().

    Returns:
        Sorted list of model names that are required but not pulled.
    """
    required = {config.ollama_agent_model, config.ollama_codegen_model}
    # Build a set of base names from pulled models (e.g. "llama3.2:latest" → "llama3.2")
    pulled_bases = {m.split(":")[0] for m in pulled_models}
    pulled_full = set(pulled_models)

    missing = []
    for model in required:
        base = model.split(":")[0]
        tag = model[len(base):]  # "" if no tag, else e.g. ":7b"
        if model in pulled_full:
            continue  # exact match
        if not tag and base in pulled_bases:
            continue  # "llama3.2" matches "llama3.2:latest"
        missing.append(model)
    return sorted(missing)


def provider_banner(config: ProviderConfig) -> str:
    """Return a human-readable startup line describing the active provider.

    Args:
        config: Resolved ProviderConfig.

    Returns:
        A single-line string for display at startup.
    """
    if config.provider == "ollama":
        return (
            f"[*] Provider: Ollama — agent: {config.ollama_agent_model}, "
            f"codegen: {config.ollama_codegen_model} ({config.ollama_base_url})"
        )
    elif config.provider == "gemini":
        return "[*] Provider: Gemini (cloud)"
    elif config.provider == "anthropic":
        return "[*] Provider: Anthropic (cloud)"
    elif config.provider == "openai":
        return "[*] Provider: OpenAI (cloud)"
    else:
        return f"[*] Provider: {config.provider}"
