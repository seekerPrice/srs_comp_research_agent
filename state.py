import operator
from typing import Annotated, List, TypedDict

class AgentState(TypedDict):
    topic: str
    plan: List[str]
    findings: List[str]  # Changed: No operator.add, so it replaces by default (reset per turn)
    messages: Annotated[List[str], operator.add]
    current_step: int
