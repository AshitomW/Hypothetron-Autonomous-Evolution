
# Selection oeprators for the evolutionary algorithm.



from __future__ import annotations
import random 


from config.settings import EvolutionConfiguration
from core.hypothesis import Hypothesis, HypothesisStatus
from core.population import Population




class SelectionOperator:
  # Implement selectoin strategies for the evolutionary loop.
  # Supports elitism, tournament selection and fitness proportionate selection.

  def __init__(self, config: EvolutionConfiguration, rng: random.Random) -> None:
    self._config = config 
    self._rng = rng 

  
  def select_survivors(self, population: Population) -> list[Hypothesis]:
    # Select hypothesis that survive to the next generation
    # uses elitism + tournament selection


    active = population.active_members
    if not active:
      return []
    target_size = self._config.population_size
    elite_count = max(1, int(target_size * self._config.elite_fraction))

    # Elites survive unconditionally
    ranked = population.ranked()
    elites =  ranked[:elite_count]



    # Fill remaining slots via tournament selection
    remaining = target_size - elite_count
    selected: list[Hypothesis] = list(elites)


    for _ in range(remaining):
      winner = population.tournament_select(self._config.tournament_size,self._rng)
      selected.append(winner)
    
    return selected
  

  def select_parents_for_mutations(
      self,
      population: Population,
      count: int,
  ) -> list[Hypothesis]:
    # Select parents that will produce mutated offsprings.
    parents: list[Hypothesis] = []
    for _ in range(count):
      parent = population.tournament_select(self._config.tournament_size, self._rng)
      parents.append(parent)

    return parents 
  


  def select_parents_for_crossover(
      self,
      population: Population,
      count: int 
  ) -> list[tuple[Hypothesis,Hypothesis]]:
    # Select pairs of parents for crossover.
    pairs: list[tuple[Hypothesis, Hypothesis]] = []
    for _ in range(count):
      parent_a = population.tournament_select(self._config.tournament_size, self._rng)
      parent_b = population.tournament_select(self._config.tournament_size,self._rng)

      attempts = 0
      max_attempts = 10

      while parent_b.id == parent_a.id and attempts < max_attempts:
        parent_b = population.tournament_select(self._config.tournament_size,self._rng)
        attempts += 1
    return pairs 
  

  def apply_fitness_threshold(self,population: Population) -> int:
    # Discard hypothesis below the minimum threshold 
    return population.discard_below_threshold(self._config.min_fitness_threshold)
    

  