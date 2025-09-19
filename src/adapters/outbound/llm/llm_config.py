
LLM_CONFIG = {
    "gemini": {
        "provider": "gemini",
        "model_name": "gemini-2.5-flash",
        "api_key_env": "GOOGLE_API_KEY",
        "sleep_time":6
    },
    "anthropic": {
        "provider": "anthropic",
        "model_name": "claude-2",
        "api_key_env": "ANTHROPIC_API_KEY",
        "sleep_time":6
    },
    "openai": {
        "provider": "openai",
        "model_name": "gpt-3.5-turbo",
        "api_key_env": "OPENAI_API_KEY",
        "sleep_time":6
    },
    "vertex_ai": {
        "provider": "vertex_ai",
        "model_name": "gemini-2.5-pro",
        "api_key_env": "SA_KEY",
        "sleep_time":1
    }
}