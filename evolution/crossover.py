# evolution/crossover.py

# Crossover operator: combines two parent hypotheses into a  offspring.


from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from core.hypothesis import Hypothesis, MutationType
from llm.parsing import parse_mutated_hypothesis
from llm.prompts import crossover_prompt
from llm.provider import BaseLLMProvider, LLMMessage

logger = logging.getLogger(__name__)


class CrossoverOperator:
    #Combines two high-fitness hypotheses into a  offspring.

    def __init__(self, llm: BaseLLMProvider) -> None:
        self._llm = llm

    async def crossover(
        self,
        parent_a: Hypothesis,
        parent_b: Hypothesis,
    ) -> Hypothesis:
    
       # Generate an offspring combining elements of both parents.
    
        prompt = crossover_prompt(parent_a, parent_b)
        messages = [
            LLMMessage(role="system", content="You are a drug discovery AI scientist."),
            LLMMessage(role="user", content=prompt),
        ]

        try:
            response = await self._llm.complete_json(messages, temperature=0.9)
            offspring = parse_mutated_hypothesis(response, parent_a, MutationType.CROSSOVER)
            # Record both parents in the description
            offspring.mutation_description = (
                f"Crossover of H[{parent_a.id[:8]}] x H[{parent_b.id[:8]}]: "
                + offspring.mutation_description
            )
            logger.info(
                "Crossover H[%s] x H[%s] -> H[%s]",
                parent_a.id[:8],
                parent_b.id[:8],
                offspring.id[:8],
            )
            return offspring
        except Exception as exc:
            logger.warning("Crossover LLM call failed: %s", exc)
            # Fallback: take drug from A, target from B
            return Hypothesis(
                parent_id=parent_a.id,
                generation=max(parent_a.generation, parent_b.generation) + 1,
                drug=parent_a.drug,
                target_protein=parent_b.target_protein,
                mechanism=parent_a.mechanism,
                disease=parent_a.disease,
                pathway=parent_b.pathway or parent_a.pathway,
                hypothesis_statement=(
                    f"{parent_a.drug} targets {parent_b.target_protein} "
                    f"via {parent_a.mechanism.value} (crossover fallback)"
                ),
                mutation_type=MutationType.CROSSOVER,
                mutation_description="Fallback crossover: drug from A, target from B",
            )