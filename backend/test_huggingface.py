from app.config import settings
from app.agent.llm_provider import get_provider, LLMMessage

print("Provider:", settings.LLM_PROVIDER)
print("Model:", settings.LLM_MODEL)

provider = get_provider(
    settings.LLM_PROVIDER,
    settings.LLM_API_KEY,
    settings.LLM_MODEL
)

response = provider.complete(
    [
        LLMMessage(
            role="user",
            content="Say hello in one short sentence."
        )
    ]
)

print("Qwen response:")
print(response.content)