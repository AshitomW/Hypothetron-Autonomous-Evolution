from __future__ import annotations
from enum import Enum 
from typing import Optional
from pydantic import BaseModel, Field 
from pydantic_settings import BaseSettings
from pathlib import Path




class LLMBackend(str, Enum):
  OPENAI = "openai"
  ANTHROPIC = "anthropic"
  OLLAMA = "ollama"
  VLLM = "vllm"
  LITELLM = "litellm"
  HUGGINGFACE = "huggingface"
  CUSTOM_OPENAI_COMPATIBLE = "custom_openai_compatible"



class LLMConfiguration(BaseModel):
  backend: LLMBackend = LLMBackend.LITELLM
  model_name: str = "gpt-4o-mini"
  base_url: Optional[str] = None 
  api_key: Optional[str] = None 
  temperature: float = Field(default=0.7, ge=0.0, le=2.0)
  max_tokens: int = Field(default=4096, ge=1)
  timeout_seconds: int = Field(default=120,ge=1)
  max_retries: int = Field(default=3, ge=0)




class EvolutionConfiguration(BaseModel):
  population_size: int = Field(default=50, ge=2, description="Number of hypothesis per generation")
  max_generations: int = Field(default=100, ge=1)
  mutation_rate: float = Field(default=0.3,ge=0.0,le=1.0)
  crossover_rate: float = Field(default=0.2, ge=0.0, le=1.0)
  elite_fraction: float = Field(default=0.1,ge=0.0, le=1.0, description="Top Fraction kept unchanged")
  tournament_size: int = Field(default=5, ge=2)
  min_fitness_threshold: float = Field(default=0.15, ge=0.0, le=1.0)
  diversity_weight: float = Field(default=0.2, ge=0.0, le=1.0)
  stagnation_limit: int = Field(default=10, ge=1, description="Generations without improvements before reset")



class SimulationConfiguration(BaseModel):
  docking_enabled: bool = True
  dynamics_enabled: bool = False
  pathway_enabled: bool = True
  docking_timeout_seconds: int = Field(default=300, ge=1)
  dynamics_steps: int = Field(default=10000, ge=100)
  binding_affinity_weight: float = Field(default=0.35, ge=0.0, le=1.0)
  stability_weight: float = Field(default=0.25, ge=0.0, le=1.0)
  toxicity_weight: float = Field(default=0.2, ge=0.0, le=1.0)
  pathway_impact_weight: float = Field(default=0.2, ge=0.0, le=1.0)


class LiteratureConfiguration(BaseModel):
  pubmed_enabled: bool = True 
  max_papers_per_query: int = Field(default=20, ge=1)
  contradiction_penalty: float = Field(default=0.3, ge=0.0, le=1.0)
  support_bonus: float = Field(default=0.2, ge=0.0, le=1.0)
  novelty_bonus: float = Field(default=0.15, ge=0.0, le=1.0)





class ReinforcementConfiguration(BaseModel):
  enabled: bool = True
  learning_rate: float = Field(default=1e-3, ge=1e-8)
  discount_factor: float = Field(default=0.99, ge=0.0, le=1.0)
  epsilon_start: float = Field(default=1.0, ge=0.0, le=1.0)
  epsilon_end: float = Field(default=0.05, ge=0.0, le=1.0)
  epsilon_decay_steps: int = Field(default=500, ge=1)
  replay_buffer_size: int = Field(default=10000, ge=100)
  batch_size: int = Field(default=64, ge=1)
  target_update_frequency: int = Field(default=10, ge=1)
  state_dimension: int = Field(default=12, ge=1)
  action_dimension: int = Field(default=6, ge=1)



class StorageConfiguration(BaseModel):
  database_path: Path = Path('data/hypotheses.db')
  lineage_export_path: Path = Path('data/lineage_export.json')
  checkpoint_dir: Path = Path("data/checkpoints")





class ApplicationSettings(BaseSettings):
  llm: LLMConfiguration = LLMConfiguration()
  evolution: EvolutionConfiguration = EvolutionConfiguration()
  simulation: SimulationConfiguration = SimulationConfiguration()
  literature: LiteratureConfiguration  = LiteratureConfiguration()
  reinforcement: ReinforcementConfiguration = ReinforcementConfiguration()
  storage: StorageConfiguration = StorageConfiguration()
  log_level: str = "INFO"
  random_seed: int = 42 


  class Configuration:
    ev_prefix = "HYPOTHETRON"
    env_nested_delimiter = "__"



def load_settings() -> ApplicationSettings:
  return ApplicationSettings()
  