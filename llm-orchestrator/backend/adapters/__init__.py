from .base import LLMClient, LLMResponse, LLMStreamChunk
from .openrouter import OpenRouterClient
from .openai_adapter import OpenAIClient
from .gemini import GeminiClient
from .mistral import MistralClient
from .grok import GrokClient
from .groq import GroqClient
from .deepseek import DeepSeekClient
from .perplexity import PerplexityClient
from .ollama import OllamaClient

ADAPTER_MAP: dict[str, type[LLMClient]] = {
    "openrouter": OpenRouterClient,
    "openai": OpenAIClient,
    "gemini": GeminiClient,
    "mistral": MistralClient,
    "grok": GrokClient,
    "groq": GroqClient,
    "deepseek": DeepSeekClient,
    "perplexity": PerplexityClient,
    "ollama": OllamaClient,
}

__all__ = [
    "LLMClient", "LLMResponse", "LLMStreamChunk",
    "ADAPTER_MAP",
    "OpenRouterClient", "OpenAIClient", "GeminiClient",
    "MistralClient", "GrokClient", "GroqClient",
    "DeepSeekClient", "PerplexityClient",
]
