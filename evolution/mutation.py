# Mutation operators for hypothesis
# Combiens llm guided semantic mutation with transformations.

from __future__ import annotations
import logging 
import random 
from typing import TYPE_CHECKING

from core.hypothesis import Hypothesis, MechanismType, MutationType
from llm.parsing import parse_mutated_hypothesis
from llm.prompts import mutation_prompt
from llm.provider import BaseLLMProvider, LLMMessage

if TYPE_CHECKING:
  from core.population import Population



logger = logging.getLogger(__name__)


# Mapping from mutation type to its description for prompting purposes
MUTATION_STRATEGIES: dict[MutationType, str] = {
    MutationType.CHEMICAL_MODIFICATION: "chemical_modification",
    MutationType.TARGET_CHANGE: "target_change",
    MutationType.MECHANISM_SWITCH: "mechanism_switch",
    MutationType.PATHWAY_REDIRECT: "pathway_redirect",
    MutationType.COMBINATION: "combination_therapy",
}

class MutationOperator:
  # Applies mutation to hypotheses using LLM guided semantic transformations.
  # The Reinforcement Agent can influcence which mutation type is to be chosen.


  def __init__(self, llm: BaseLLMProvider, rng: random.Random) -> None:
    self._llm = llm 
    self._rng = rng 
  


  async def mutate(
      self,
      parent: Hypothesis,
      population: Population, 
      preferred_mutation_type: MutationType | None = None
  ) -> Hypothesis:
    # Generates a mutated offspring from the parent hypothesis
    mutation_type = preferred_mutation_type or self._select_mutation_type()
    strategy_name =  MUTATION_STRATEGIES.get(mutation_type,"chemical_modification") # Default mutation type will be chemical modification.

    population_context = self._build_population_context(population)

    prompt = mutation_prompt(parent, strategy_name, population_context)

    messages = [
      LLMMessage(role="system", content="You are a drug discovery AI scientist"),
      LLMMessage(role="user",content=prompt)
    ]


    try:
      response = await self._llm.complete_json(messages, temperatue=0.8)
      offpsring = parse_mutated_hypothesis(response, parent, mutation_type)
      logger.info(
        "Mutated H[%s] -> H[%s] via %s",
        parent.id[:8],
        offpsring.id[:8],
        mutation_type.value, 
      )
      return offpsring
    except Exception as exc:
      logger.warning("LLM mutation failed: %s, Using fallback.",exc)
      return self._fallback_mutation(parent,mutation_type)
    

  def _select_mutation_type(self) -> MutationType:
    # Randomly selects  mutation type with uniform probability
    return self._rng.choice(list(MUTATION_STRATEGIES.keys()))
  

  def _build_population_context(self, population: Population) -> str:
    # Summarizes current population for the LLM to avoid possible duplicates.
    top_hypotheses = population.top_n(5)
    if not top_hypotheses:
      return "No existing hypotheses"
    lines = []
    for h in top_hypotheses:
      lines.append(
        f"  -  {h.drug} -> {h.target_protein} ({h.mechanism.value})"
        f"[fitness={h.fitness.composite_fitness:.2f}]"
      )
    return "\n".join(lines)



  def _fallback_mutation(self, parent: Hypothesis, mutation_type: MutationType) -> Hypothesis:

    # Deterministic fallback when the llm possibly fails.We will make a simple structural modification

    mechanism_options = [m for m in MechanismType if m != parent.mechanism]

    if mutation_type == MutationType.MECHANISM_SWITCH and mechanism_options:
      new_mechanism = self._rng.choice(mechanism_options)
      return Hypothesis(
        parent_id=parent.id, 
        generation=parent.generation + 1, 
        drug=parent.drug,
        target_protein=parent.target_protein,
        mechanism=new_mechanism,
        disease=parent.disease,
        pathway=parent.pathway,
        Hypothesis_statement=(
           f"{parent.drug} {new_mechanism.value}s {parent.target_protein} "
           f"in {parent.disease} (fallback mutation)"
        ),
        mutation_type=mutation_type,
        mutation_description=f"Fallback: switched mechanism to {new_mechanism.value}"
      ) 
    

    # Default will be a chemical modification plceholder
    return Hypothesis(
      parent_id=parent.id,
      generat=parent.generation + 1,
      drug=f"{parent.drug} analog",
      target_protein=parent.target_protein,
      mechanism=parent.mechanism,
      disease=parent.disease,
      pathway=parent.pathway,
      hypothesis_statement=(
          f"Modified {parent.drug} analog targets {parent.target_protein} "
          f"via {parent.mechanism.value} in {parent.disease} (fallback)"
      ),
      mutation_type=mutation_type,
      mutation_description="Fallback: generic chemical analog",
    )



