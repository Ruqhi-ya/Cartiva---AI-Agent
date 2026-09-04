"""LLM provider abstraction for Cartiva AI.

Cartiva uses Hugging Face Inference Providers to access
the Qwen3-4B-Instruct-2507 model.

The rest of the application talks to the LLM through
the LLMProvider interface, so the agent code does not
need to know how the model is hosted.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from huggingface_hub import InferenceClient


@dataclass
class ToolSpec:
    """Describes a callable tool exposed to the LLM."""

    name: str
    description: str
    parameters: dict


@dataclass
class LLMMessage:
    """A message in the conversation."""

    role: str
    content: str


@dataclass
class LLMResponse:
    """Response returned by the LLM."""

    content: str = ""
    tool_name: Optional[str] = None
    tool_arguments: dict = field(default_factory=dict)


class LLMProvider(ABC):
    """Interface every LLM backend must implement."""

    @abstractmethod
    def complete(
        self,
        messages: list[LLMMessage],
        tools: Optional[list[ToolSpec]] = None,
    ) -> LLMResponse:
        raise NotImplementedError


class HuggingFaceProvider(LLMProvider):
    """Hugging Face provider using InferenceClient."""

    def __init__(self, api_key: str, model: str):
        self.model = model or "Qwen/Qwen3-4B-Instruct-2507"

        self.client = InferenceClient(
            model=self.model,
            token=api_key,
            provider="auto",
        )

    def complete(
        self,
        messages: list[LLMMessage],
        tools: Optional[list[ToolSpec]] = None,
    ) -> LLMResponse:

        hf_messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]

        response = self.client.chat_completion(
            messages=hf_messages,
            max_tokens=120,
            temperature=0.1,
        )

        content = response.choices[0].message.content or ""

        return LLMResponse(content=content)


class MockLLMProvider(LLMProvider):
    """Development fallback provider."""

    def complete(
        self,
        messages: list[LLMMessage],
        tools: Optional[list[ToolSpec]] = None,
    ) -> LLMResponse:

        user_text = next(
            (
                message.content
                for message in reversed(messages)
                if message.role == "user"
            ),
            "",
        )

        return LLMResponse(content=user_text)


def get_provider(
    name: str,
    api_key: str = "",
    model: str = "",
) -> LLMProvider:

    if name.lower() in {"huggingface", "hf"}:
        return HuggingFaceProvider(
            api_key=api_key,
            model=model,
        )

    return MockLLMProvider()