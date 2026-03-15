from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field





class MechanismType(str, Enum):
  """ Types of biological mechanism a hypothesis can propose."""
  INHIBITION = 'inhibition'
  ACTIVATION = 'activation'
  MODULATION = 'modulation'
  STABILIZATION = 'stabilization'
  DEGRADATION = 'degradation'
  BINDING = 'binding'
  COMBINATION = 'combination'



class HypothesisStatus(str, Enum):
  """Lifecycle of a hypothesis"""
  CANDIDATE = 'candidate'
  TESTING = 'testing'
  EVALUATED = 'evaluated'
  SELECTED = 'selected'
  DISCARDED = 'discarded'
  ARCHIVED = 'archived'



class MutationType(str, Enum):
  '''How a hypothesis was derived from its parent'''
  ORIGINAL = "original"
  CHEMICAL_MODIFICATION = "chemical_modification"
  TARGET_CHANGE = "target_change"
  MECHANISM_SWITCH = "mechanism_switch"
  PATHWAY_REDIRECT = "pathway_redirect"
  COMBINATION = "combination"
  CROSSOVER = "crossover"
  RL_GUIDED = "rl_guided"




class EvidenceItem(BaseModel):
  """ A single piece of evidence supporting or contradicting a hypothesis"""
  source: str 
  source_id: Optional[str] = None 
  summary: str 
  confidence: float = Field(ge=0.0, le=1.0)
  supports: bool = True 
  retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))



class SimulationResult(BaseModel):
  """ Results from copmutational simulation of the hypothesis"""
  binding_affinity_kcal_mol: Optional[float] = None 
  stability_score: Optional[float] = Field(default=None, ge=0.0,le=1.0)
  toxicity_prediction: Optional[float] = Field(default=None, ge=0.0,le=1.0)
  pathway_impact_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
  raw_data: dict = Field(default_factory=dict)
  simulator_name: str = ""
  completed_at: Optional[datetime] = None 




class FitnessScores(BaseModel):
  """Composite fitness breakdown for a hypothesis"""
  simulation_fitness: float = Field(default=0.0,ge=0.0,le=1.0)
  literature_fitness: float = Field(default=0.0,ge=0.0,le=1.0)
  novelty_score: float = Field(default=0.0, ge=0.0, le=1.0)
  plausibility_score: float = Field(default=0.0,ge=0.0, le=1.0)
  diversity_contribution: float = Field(default=0.0, ge=0.0, le=1.0)
  composite_fitness: float = Field(default=0.0,ge=0.0,le=1.0)




class Hypothesis(BaseModel):
  """  
    A scientific hypothesis that evolves over generations

    This is the fundamental unit of the evolutionary system. Each hypothesis is a concrete , testable scientific prposition with full provenance tracking.
  """

  id: str = Field(default_factory=lambda: str(uuid.uuid4()))
  parent_id: Optional[str] = None 
  generation: int = Field(default=0,ge=0)

  # Scientific Content
  drug: str 
  drug_smile: Optional[str] = None
  target_protein: str 
  target_uniprot_id: Optional[str] = None 
  mechanism: MechanismType
  disease: str 
  disease_ontology_id: Optional[str] = None 
  pathway: Optional[str] = None 
  Hypothesis_statement: str 

  # Evolution Metadata
  mutation_type: MutationType = MutationType.ORIGINAL
  mutation_description: str = ""
  status: HypothesisStatus = HypothesisStatus.CANDIDATE

  # Evaluation
  simulation_results: list[SimulationResult] = Field(default_factory=list)
  evidence: list[EvidenceItem] = Field(default_factory=list)
  fitness: FitnessScores = Field(default_factory=FitnessScores)

  created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
  evaluated_at: Optional[datetime] = None 


  def add_evidence(self, item: EvidenceItem) -> None:
    self.evidence.append(item)

  def add_simulation_result(self, result: SimulationResult) -> None:
    self.simulation_results.append(result)
  
  def marked_evaluated(self) -> None:
    self.status = HypothesisStatus.EVALUATED
    self.evaluated_at = datetime.now(timezone.utc)
  
  def is_alive(self) -> bool:
    return self.status not in (HypothesisStatus.DISCARDED, HypothesisStatus.ARCHIVED)
  

  @property
  def evidence_support_ratio(self) -> float:
    """ Fraction of evidence items that support the hypothesis."""
    if not self.evidence:
      return 0.5 # Neutral prior when no evidence
    supporting = sum (1 for e in self.evidence if e.supports)
    return supporting/len(self.evidence)
  






