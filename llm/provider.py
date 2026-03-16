'''
LLM interface supporting most of backend: OpenAI, Anthropic, Ollama, vLLM, huggingFace, or any OPENAI compatible API.


LiteLLM is used as universal router, with fallback to direct HTTP for custom endpoints
'''



from __future__ import annotations
import logging

from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel

from config.settings import LLMBackend, LLMConfiguration

logger = logging.getLogger(__name__)



class LLMMessage(BaseModel):
  '''A single message in a converstation'''
  role: str # systtem, user , assistant....
  content: str 


class LLMResponse(BaseModel):
  ''' Response from LLM'''
  content: str 
  model: str 
  usage: dict[str, int] = {}
  raw: dict[str, Any] = {}




class BaseLLMProvider(ABC):
  ''' Abstract interface for LLM providers.'''
  @abstractmethod
  async def complete(
    self,
    messages: list[LLMMessage],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None, 
  ) -> LLMResponse:
    '''
    Send messgaes and get a completion
    '''

  @abstractmethod
  async def complete_json(
    self,
    messages: list[LLMMessage],
    temperatue: Optional[float] = None,
    max_tokens: Optional[int] = None,
  ) -> dict[str, Any]:
    '''Send messages and get a completion'''
  




class LiteLLMProvider(BaseLLMProvider):
  ''''
    Provider using litellm , which supports must of the llm backends.
  '''


  def __init__(self, config: LLMConfiguration) -> None:
    self._config = config 
    self._model = self._resolve_model_string()

  def _resolve_model_string(self) -> str:
    """
    Litellm uses prefixed model strings: <provider>/<model_name>
    """
    prefix_map = {
      LLMBackend.OPENAI: "openai",
      LLMBackend.ANTHROPIC: "anthropic",
      LLMBackend.OLLAMA: "ollama",
      LLMBackend.HUGGINGFACE: "huggingface",
      LLMBackend.VLLM:"openai", # vLLM exposes openai compatible APi
      LLMBackend.CUSTOM_OPENAI_COMPATIBLE: "openai",
      LLMBackend.LITELLM :"", # litellm auto detection
    }

    prefix = prefix_map.get(self._config.backend,"")
    if prefix and not self._config.model_name.startswith(prefix):
      return f"{prefix}/{self._config.model_name}"
    return self._config.model_name 
  
  async def complete(self, messages: list[LLMMessage], temperature: Optional[float]=None, max_tokens: Optional[int] = None) -> LLMResponse:
    import litellm

    message_dicts = [{"role":m.role,"content":m.content} for m in messages]
    kwargs: dict[str, Any] = {
      "model": self._model,
      "messages": message_dicts,
      "temperature": temperature or self._config.temperature,
      "max_tokens": max_tokens or self._config.max_tokens,
      "num_retries": self._config.max_retries,
      "timeout": self._config.timeout_seconds
    }


    if self._config.api_key:
      kwargs["api_key"] = self._config.api_key
    if self._config.base_url:
      kwargs["api_base"] = self._config.base_url

    response = await litellm.acompletion(**kwargs)
    

    return LLMResponse(
      content=response.choices[0].message.content or "",
      model = response.model or self._model,
      usage={
        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
        "completion_tokens": response.usage.completion_tokens if response.usage else 0
      }, 
      raw=response.model_dump() if hasattr(response,"model_dump") else {}
    )
  
  async def complete_json(
      self,
      messages: list[LLMMessage],
      temperature: Optional[float] = None, 
      max_tokens: Optional[int] = None,
  ) -> dict[str, Any]:
    import json

    json_messages = list(messages)
    if json_messages and json_messages[-1].role == "user":
      json_messages[-1] = LLMMessage(
        role="user",
        content=json_messages[-1].content + "\n\nRespond with valid JSON only.",  
      )

    response = await self.complete(json_messages, temperature,max_tokens)

    content = response.content.strip()
    if content.startswith("```json"):
      content = content[7:]
    if content.startswith("```"):
      content = content[3:]
    if content.endswith("```"):
      content = content[:-3]
    return json.loads(content.strip())
  

def create_llm_provider(config: LLMConfiguration) -> BaseLLMProvider:
  """Factory foor creating llm provider"""
  logger.info(
    "Creating LLM provider: backend=%s, model=%s",
    config.backend.value,
    config.model_name, 
  )
  return LiteLLMProvider(config)

