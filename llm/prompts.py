"""
Prompt Templates for hypothesis generation, mutation and evaluation
All prompts are parameterized no hardcoded scientific content.
"""



from __future__ import annotations
from core.hypothesis import Hypothesis, MechanismType


SYSTEM_PROMPT = """ You are an AI research scientist specializing in drug discovery and molecular biology. You generate, evaluate, and refine scientific hypotheses. Your response must be precise, scientifically grounded, and structured as JSON when requested."""

def hypothesis_generation_prompt(
    disease: str, 
    known_targets: list[str],
    known_drugs: list[str],
    num_hypotheses: int,
    existing_hypotheses: list[str] | None = None,
) -> str:
  """
  Prompt the llm to generate novel hypotheses for a given disease context.
  """

  existing_section = ""
  if existing_hypotheses:
    existing_text = "\n".join(f"  - {h}" for h in existing_hypotheses[:10])
    existing_section = f"""
The following hypotheses already exist. Generate NOVEL ones that differ:
{existing_text}
"""
    mechanisms = ", ".join(m.value for m in MechanismType)
    return f"""Generate {num_hypotheses} novel drug-target hypotheses for: {disease}

Known relevant targets: {", ".join(known_targets[:15])}
Known relevant drugs/compounds: {", ".join(known_drugs[:15])}
Possible mechanism types: {mechanisms}
{existing_section}
For each hypothesis, provide a JSON array where each element has:
{{
  "drug": "compound name",
  "drug_smiles": "SMILES string if known, else null",
  "target_protein": "protein name",
  "target_uniprot_id": "UniProt ID if known, else null",
  "mechanism": "one of [{mechanisms}]",
  "pathway": "relevant biological pathway",
  "hypothesis_statement": "A clear scientific statement of the hypothesis",
  "rationale": "Why this hypothesis is worth investigating"
}}

Prioritize:
1. Scientific plausibility
2. Novelty (not trivially known)
3. Testability
4. Diversity of approaches"""
  



def mutation_prompt(
    parent: Hypothesis,
    mutation_type: str,
    population_context: str, 
) -> str:
  """
  Prompt the LLM to mutate an existing hypothesis.
  """
  mechanisms = ", ".join(m.value for m in MechanismType)

  return f"""Mutate the following scientific hypothesis using a {mutation_type} strategy.

Parent hypothesis:
  Drug: {parent.drug}
  Target: {parent.target_protein}
  Mechanism: {parent.mechanism.value}
  Disease: {parent.disease}
  Pathway: {parent.pathway or "unknown"}
  Statement: {parent.hypothesis_statement}
  Current fitness: {parent.fitness.composite_fitness:.3f}

Mutation type: {mutation_type}
Available mechanisms: {mechanisms}

Population context (avoid duplicating these):
{population_context}

Generate a SINGLE mutated hypothesis as JSON:
{{
  "drug": "modified or new compound",
  "drug_smiles": "SMILES if known, else null",
  "target_protein": "protein name",
  "target_uniprot_id": "UniProt ID if known, else null", 
  "mechanism": "mechanism type",
  "pathway": "pathway",
  "hypothesis_statement": "clear scientific statement",
  "mutation_description": "what was changed and why"
}}

The mutation should:
1. Be scientifically motivated
2. Preserve what works in the parent (high fitness aspects)
3. Explore a meaningful variation
4. Be specific and testable"""

def literature_critique_prompt(hypothesis: Hypothesis) -> str:
  """
  Promptt the LLM to evaluate a hypothesis against known literature
  """
  return f"""Evaluate this scientific hypothesis against known biomedical knowledge:

Hypothesis: {hypothesis.hypothesis_statement}
Drug: {hypothesis.drug}
Target: {hypothesis.target_protein}
Mechanism: {hypothesis.mechanism.value}
Disease: {hypothesis.disease}
Pathway: {hypothesis.pathway or "unspecified"}

Provide your evaluation as JSON:
{{
  "supporting_evidence": [
    {{"fact": "...", "confidence": 0.0-1.0, "source_hint": "..."}}
  ],
  "contradicting_evidence": [
    {{"fact": "...", "confidence": 0.0-1.0, "source_hint": "..."}}
  ],
  "mechanistic_plausibility": 0.0-1.0,
  "novelty_assessment": "known/partially_known/novel",
  "key_risks": ["risk1", "risk2"],
  "overall_assessment": "brief summary"
}}

Be critical and scientifically rigorous. Flag any speculative claims."""

  
def crossover_prompt(parent_a: Hypothesis, parent_b: Hypothesis) -> str:
  """
  Prompt the LLM to combine two hypothesis into a novel offspring.
  """
  mechanisms = ", ".join(m.value for m in MechanismType)

  return f"""Combine elements from two parent hypotheses into a novel offspring.

Parent A:
  Drug: {parent_a.drug}
  Target: {parent_a.target_protein}
  Mechanism: {parent_a.mechanism.value}
  Disease: {parent_a.disease}
  Fitness: {parent_a.fitness.composite_fitness:.3f}

Parent B:
  Drug: {parent_b.drug}
  Target: {parent_b.target_protein}
  Mechanism: {parent_b.mechanism.value}
  Disease: {parent_b.disease}
  Fitness: {parent_b.fitness.composite_fitness:.3f}

Available mechanisms: {mechanisms}

Create a SINGLE offspring hypothesis as JSON:
{{
  "drug": "compound (may combine aspects of both parents)",
  "drug_smiles": "SMILES if known, else null",
  "target_protein": "protein name",
  "target_uniprot_id": "UniProt ID if known, else null",
  "mechanism": "mechanism type",
  "pathway": "pathway",
  "hypothesis_statement": "clear scientific statement",
  "mutation_description": "how elements from both parents were combined"
}}

The offspring should inherit strengths from both parents while proposing 
something neither parent alone considered."""
