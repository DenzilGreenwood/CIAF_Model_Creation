"""LLM Provider abstraction for multiple LLM backends."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum


class LLMProviderType(str, Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"
    MOCK = "mock"


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs: Any
    ) -> str:
        """Generate text using the LLM.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Temperature for generation
            max_tokens: Maximum tokens
            **kwargs: Additional provider-specific arguments

        Returns:
            Generated text
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
            model: Model to use (default: gpt-4)
        """
        import os
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.available = self.api_key is not None

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs: Any
    ) -> str:
        """Generate using OpenAI API."""
        if not self.available:
            raise RuntimeError("OpenAI API key not configured")

        try:
            import openai
            openai.api_key = self.api_key

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}")

    def is_available(self) -> bool:
        """Check if OpenAI provider is available."""
        return self.available


class OllamaProvider(LLMProvider):
    """Local Ollama provider."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        """Initialize Ollama provider.

        Args:
            base_url: Ollama server URL
            model: Model to use (default: mistral)
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if Ollama server is running."""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs: Any
    ) -> str:
        """Generate using Ollama API."""
        if not self.available:
            raise RuntimeError("Ollama server not available at " + self.base_url)

        try:
            import requests

            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "stream": False,
                    **kwargs
                },
                timeout=120
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {e}")

    def is_available(self) -> bool:
        """Check if Ollama provider is available."""
        return self.available


class MockProvider(LLMProvider):
    """Mock LLM provider for testing."""

    def __init__(self):
        """Initialize mock provider."""
        self.available = True

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs: Any
    ) -> str:
        """Generate mock response."""
        # Return deterministic mock responses based on keywords
        if "banking" in prompt.lower() or "loan" in prompt.lower():
            if "recommend" in prompt.lower():
                return "Based on the customer's creditworthiness and financial history, I recommend approving a credit line extension of $50,000 with a 6.5% annual interest rate."
            elif "risk" in prompt.lower():
                return "Risk Assessment: Medium. Customer has stable income but recent payment delays noted."
        elif "healthcare" in prompt.lower() or "diagnosis" in prompt.lower():
            if "recommend" in prompt.lower():
                return "Patient presents with symptoms consistent with Type 2 Diabetes. Recommend HbA1c testing and lifestyle modification program."
            elif "risk" in prompt.lower():
                return "Patient Risk Level: Medium-High. Multiple comorbidities detected."
        else:
            return "This is a mock AI-generated response for testing purposes. In production, this would be replaced with real LLM output."

    def is_available(self) -> bool:
        """Check if mock provider is available."""
        return True


class LLMProviderFactory:
    """Factory for creating LLM providers."""

    _providers: Dict[str, type] = {
        LLMProviderType.OPENAI: OpenAIProvider,
        LLMProviderType.OLLAMA: OllamaProvider,
        LLMProviderType.MOCK: MockProvider,
    }

    @classmethod
    def create(
        cls,
        provider_type: LLMProviderType = LLMProviderType.MOCK,
        **kwargs: Any
    ) -> LLMProvider:
        """Create an LLM provider.

        Args:
            provider_type: Type of provider to create
            **kwargs: Provider-specific arguments

        Returns:
            LLMProvider instance
        """
        provider_class = cls._providers.get(provider_type)
        if not provider_class:
            raise ValueError(f"Unknown provider type: {provider_type}")

        instance = provider_class(**kwargs)

        # Fallback to mock if primary provider unavailable
        if not instance.is_available() and provider_type != LLMProviderType.MOCK:
            print(f"⚠️  {provider_type} not available, falling back to Mock provider")
            return MockProvider()

        return instance

    @classmethod
    def create_auto(cls) -> LLMProvider:
        """Automatically create the best available provider.

        Priority: OpenAI > Ollama > Mock
        """
        # Try OpenAI first
        openai_provider = OpenAIProvider()
        if openai_provider.is_available():
            return openai_provider

        # Try Ollama next
        ollama_provider = OllamaProvider()
        if ollama_provider.is_available():
            return ollama_provider

        # Fall back to Mock
        return MockProvider()
