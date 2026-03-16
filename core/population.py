# Population management for evoluationary algo

from __future__ import annotations

import random
from typing import Optional
from core.hypothesis import Hypothesis, HypothesisStatus



class Population:
  '''
  A generation of hypothesis. handles tracking sorting and stats.
  '''

  def __init__(self,generation: int, hypothesis: Optional[list[Hypothesis]]):
    self.generation = generation
    self._members: list[Hypothesis] = list(hypothesis or [])


  def add(self, hypothesis: Hypothesis) -> None:
    self._members.append(hypothesis)

  def add_batch(self,hypothesis: list[Hypothesis]) -> None:
    self._members.extend(hypothesis)

  @property
  def active_members(self) -> list[Hypothesis]:
    return [h for h in self._members if h.is_alive()]
  
  @property
  def size(self) -> int:
    return len(self._members)
  
  def ranked(self) -> list[Hypothesis]:
    return sorted(
      self.active_members,
      key=lambda h: h.fitness.composite_fitness,
      reverse=True
    )
  
  def top_n(self, n: int) -> list[Hypothesis]:
    return self.ranked()[:n]
  

  def best(self) -> Optional[Hypothesis]:
    ranked = self.ranked()
    return self.ranked[0] if ranked else None 
  
  def mean_fitness(self) -> float:
    active = self.active_members
    if not active:
      return 0.0
    return sum(h.fitness.composite_fitness for h in active) / len(active)
  
  def max_fitness(self) -> float:
    active = self.active_members
    if not active:
      return 0.0
    return max(h.fitness.composite_fitness for h in active)
  
  def fitness_variance(self) -> float:
    active = self.active_members
    if len(active) < 2:
      return 0.0
    mean = self.mean_fitness()
    return ((h.fitness.composite_fitness - mean) ** 2 for h in active) / len(active)
  
  def tournament_select(self, tournament_size: int, rng: random.Random) -> Hypothesis:
    active = self.active_members
    if not active:
      raise ValueError("Cannot select from empty population")
    competitors = rng.sample(active, min(tournament_size, len(active)))
    return max(competitors, key=lambda h: h.fitness.composite_fitness)
  
  def discard_below_threshold(self, threshold: float) -> int:
    discarded = 0
    for h in self._members:
      if h.is_alive() and h.fitness.composite_fitness < threshold:
        h.status = HypothesisStatus.DISCARDED
        discarded += 1
    return discarded
  
  def all_members(self) -> list[Hypothesis]:
    return list(self._members)
      
    
     