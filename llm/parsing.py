'''
Parse LLM outputs into structured hypothesis objects.
Handles malformed responses gracefully.
'''


from __future__ import annotations
import json
import logging 
from typing import Any 
from core.hypothesis import Hypothesis, MechanismType, MutationType


logger =logging.getLogger(__name__)

def parse_generated_hypothesis(
   raw_json: dict[str,Any] | list[dict[str,Any]],
   disease: str,
   generation: int,  
) -> list[Hypothesis]:
  # Parse the llm output into hypothesis objects

  if isinstance(raw_json, dict):
    items = [raw_json]
  elif isinstance(raw_json,list):
    items = raw_json
  else:
    logger.warning("Unexpected LLM output type: %s", type(raw_json))
    return []


  hypotheses: list[Hypothesis] = []
  for item in items:
    try:
      hypothesis = _parse_single_hypothesis(item,disease,generation)
      hypotheses.append(hypothesis)
    except (KeyError,ValueError) as exc:
      logger.warning("Failed to parse hypothesis: %s. Data: %s", exc, item)
      continue 


def parse_mutated_hypothesis(
    raw_json: dict[str, Any],
    parent: Hypothesis,
    mutation_type: MutationType
) -> Hypothesis:
  # Parse a mutated hypothesis from LLM output
  mechanism = _safe_parse_mechanism(raw_json.get("mechanism", parent.mechanism.value))

  return Hypothesis(
        parent_id=parent.id,
        generation=parent.generation + 1,
        drug=raw_json.get("drug", parent.drug),
        drug_smiles=raw_json.get("drug_smiles"),
        target_protein=raw_json.get("target_protein", parent.target_protein),
        target_uniprot_id=raw_json.get("target_uniprot_id"),
        mechanism=mechanism,
        disease=parent.disease,
        disease_ontology_id=parent.disease_ontology_id,
        pathway=raw_json.get("pathway", parent.pathway),
        hypothesis_statement=raw_json.get("hypothesis_statement", ""),
        mutation_type=mutation_type,
        mutation_description=raw_json.get("mutation_description", ""),
    )




def parse_literature_critique(raw_json: dict[str, Any]) -> dict[str, Any]:
   
    #Parse the literature critique response into structured data.
   
    return {
        "supporting": raw_json.get("supporting_evidence", []),
        "contradicting": raw_json.get("contradicting_evidence", []),
        "plausibility": float(raw_json.get("mechanistic_plausibility", 0.5)),
        "novelty": raw_json.get("novelty_assessment", "unknown"),
        "risks": raw_json.get("key_risks", []),
        "assessment": raw_json.get("overall_assessment", ""),
    }

def _parse_single_hypothesis(
    data: dict[str, Any],
    disease: str,
    generation: int,
) -> Hypothesis:
    #Parse a single hypothesis dict."""
    mechanism = _safe_parse_mechanism(data.get("mechanism", "inhibition"))

    return Hypothesis(
        generation=generation,
        drug=data["drug"],
        drug_smiles=data.get("drug_smiles"),
        target_protein=data["target_protein"],
        target_uniprot_id=data.get("target_uniprot_id"),
        mechanism=mechanism,
        disease=disease,
        pathway=data.get("pathway"),
        hypothesis_statement=data.get("hypothesis_statement", ""),
        mutation_type=MutationType.ORIGINAL,
    )


def _safe_parse_mechanism(value: str) -> MechanismType:
    #Parse mechanism type with fallback."""
    try:
        return MechanismType(value.lower().strip())
    except ValueError:
        logger.warning("Unknown mechanism type '%s', defaulting to MODULATION", value)
        return MechanismType.MODULATION