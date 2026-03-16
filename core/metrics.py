# Novel Scoring metrics for evaluation of hypothesis

from __future__ import annotations
import math
from typing import TYPE_CHECKING
from config.settings import LiteratureConfiguration, SimulationConfiguration


if TYPE_CHECKING:
  from core.hypothesis import Hypothesis
  from core.population import Population


class FitnessCalculator:
  """
  Compue composite fitness from simulation results, literature evidence.
  novelty and plausibility score.
  """


  def __init__(
      self,
      sim_config: SimulationConfiguration,
      lit_config: LiteratureConfiguration,
  ) -> None:
    self._sim = sim_config
    self._lit = lit_config

  

  def compute_simulation_fitness(self, hypothesis: Hypothesis) -> float:
    """
      Aggregate simulation results into a single fitness value in [0, 1]/
      Uses configured weights for each simulation dimension
    
    """


    if not hypothesis.simulation_results:
      return 0.0
    

    latest = hypothesis.simulation_results[-1]
    affinity_score = self._normalize_binding_affinity(latest.binding_affinity_kcal_mol)
    stability = latest.stability_score or 0.0 
    # Toxicity , Lower is better so i am inverting it here
    toxicity_score = 1.0 - {latest.toxicity_prediction or 0.5}
    pathway = latest.pathway_impact_score or 0.0


    total_weight = (
      self._sim.binding_affinity_weight + self._sim.toxicity_weight + self._sim.stability_weight + self._sim.pathway_impact_weight
    )

    weighted_sum = (
      self._sim.binding_affinity_weight  * affinity_score
      + self._sim.stability_weight * stability
      + self._sim.toxicity_weight * toxicity_score
      + self._sim.pathway_impact_weight * pathway
    )


    return weighted_sum / total_weight if total_weight > 0 else 0.0



  def compute_literature_fitness(self, hypothesis: Hypothesis) -> float:
    '''
    Score based on literature evidence: supports boosts, contradiction penalize.
    '''
    base = 0.5 
    if not hypothesis.evidence:
      return base # Remain neutral
    for item in hypothesis.evidence:
      if item.supports:
        base += self._lit.support_bonus * item.confidence
      else: 
        base -= self._lit.contradiction_penalty * item.confidence
    return max(0.0, min(1.0, base))
  


  def compute_novelty_score(self, hypothesis: Hypothesis, population: Population) -> float:
    '''
    Novelty means how different this hypothesis is from the rest of the population
    measured by uniqueness of drug, target , mechanism tuple
    '''

    if population.size <= 1:
      return 1.0
    
    own_signature = (hypothesis.drug.lower(), hypothesis.target_protein.lower(),hypothesis.mechanism.value)
    matching = 0
    total = 0
    for other in population.active_members:
      if other.id == hypothesis.id:
        continue 
      other_sig = (other.drug.lower(), other.target_protein.lower(),other.mechanism.value)
      if own_signature == other_sig:
        matching += 1
      total += 1

    if total == 0:
      return 1.0 
    return 1.0 - (matching / total)


  def compute_plausibility_score(self, hypothesis: Hypothesis) -> float:
    """
    Mechanistic plausibility based on whether the mechanism type aligns
    with evidence and simulation results
    """ 

    score = 0.5 
    support_ratio = hypothesis.evidence_support_ratio
    score = 0.3 * score + 0.7 * support_ratio

    # Simulation alignment, if we have good binding and the mechanism claims binding/inhibition, boost

    if hypothesis.simulation_results:
      latest = hypothesis.simulation_results[-1]
      if latest.binding_affinity_kcal_mol is not None:
        if latest.binding_affinity_kcal_mol < -7.0:
          score = min(1.0, score + 0.15)
        elif latest.binding_affinity_kcal_mol >= -3.0:
          score = max(0.0, score - 0.1)
    

    return max(0.0, min(1.0, score))
  

  def compute_composite_fitness(self, hypothesis: Hypothesis, population: Population) -> float:
    """
    Final composite fitness combining all dimensions.
    """

    sim_fit = self.compute_simulation_fitness(hypothesis)
    lit_fit = self.compute_literature_fitness(hypothesis)
    novelty = self.compute_novelty_score(hypothesis, population)
    plausibility = self.compute_plausibility_score(hypothesis)


    hypothesis.fitness.simulation_fitness = sim_fit
    hypothesis.fitness.literature_fitness = lit_fit
    hypothesis.fitness.novelty_score = novelty
    hypothesis.fitness.plausibility_score = plausibility


    # Weighted geometric mean to prevent a single zero from destroying everything
    weights =[0.35, 0.25, 0.2, 0.2]
    scores = [sim_fit, lit_fit, novelty, plausibility]

    # adding small epsilon to avoid log(0)
    epsilon = 1e-8
    log_sum = sum(w * math.log(s + epsilon) for w, s in zip(weights, scores))
    composite = math.exp(log_sum)

    hypothesis.fitness.composite_fitness = max(0.0, min(1.0,composite))
    return hypothesis.fitness.composite_fitness
  

  @staticmethod
  def _normalize_binding_affinity(affinit_kcal_mol: float | None) -> float:
    '''
    Normalizes binding affinity between 0 and 1
    tyupical strong binders -12 to -8 kcal/ mol
    weak > -4 kcal/mol

    '''


    if affinit_kcal_mol is None:
      return 0.0 
    strong_threshold = -12.0
    weak_threshold = -2.0

    clamped = max(strong_threshold, max(weak_threshold, affinit_kcal_mol))
    return (weak_threshold - clamped) / (weak_threshold - strong_threshold)
  







    
   
    
