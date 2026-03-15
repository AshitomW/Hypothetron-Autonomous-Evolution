# Lineage Tracking, a tree structure recording how hypothesis evolve

from __future__ import annotations
from collections import defaultdict
from typing import Optional


from core.hypothesis import Hypothesis


class LineageTree:
  # Track parent child relationship across hypothesis
  # For Analyzing idea evolution
  def __init__(self) -> None:
    self._nodes: dict[str, Hypothesis] = {}
    self._children: dict[str, list[str]] = defaultdict(list)
  def add(self, hypothesis: Hypothesis) -> None:
    self._nodes[hypothesis.id] = hypothesis
    if hypothesis.parent_id is not None:
      self._children[hypothesis.parent_id].append(hypothesis.id)
  def get(self, hypothesis_id: str) -> Optional[Hypothesis]:
    return self._nodes.get(hypothesis_id)
  def children_of(self,hypothesis_id: str) -> list[Hypothesis]:
    child_ids = self._children.get(hypothesis_id,[])
    return [self._nodes[cid] for cid in child_ids if cid in self._nodes]
  def ancestor_of(self,hypothesis_id: str) -> list[Hypothesis]:
    ancestors: list[Hypothesis] = []
    current_id: Optional[str] = hypothesis_id
    while current_id is not None:
      node = self._nodes.get(current_id)
      if node is None:
        break
      ancestors.append(node)
      current_id = node.parent_id
    return list(reversed(ancestors))
  

  def decendants_of(self,hypothesis_id: str) -> list[Hypothesis]:
    result: list[Hypothesis] = []
    stack = list(self._children.get(hypothesis_id,[]))
    while stack:
      child_id = stack.pop()
      if child_id in self._nodes:
        result.append(self._nodes[child_id])
        stack.extend(self._children.get(child_id,[]))
    return result 
  

  def roots(self) -> list[Hypothesis]:
    return [h for h in self._nodes.values() if h.parent_id is None]
  
  def depth_of(self,hypothesis_id: str) -> int:
    return len(self.ancestor_of(hypothesis_id)) - 1 # Basically: how many generations back does this hypothesis trace?
  
  @property
  def size(self) -> int:
    return len(self._nodes) # Number of hypothesis ever tracked
  
  def all_hypothesis(self) -> list[Hypothesis]:
    return list(self._nodes.values())
  
