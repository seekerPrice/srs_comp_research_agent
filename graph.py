from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from state import AgentState
from nodes import planner_node, researcher_node, responder_node

def create_graph():
    """Constructs and compiles the LangGraph agent."""
    
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("responder", responder_node)
    
    # Define Edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "researcher")
    
    # Conditional Edge Logic
    def should_continue(state: AgentState):
        current_step = state.get('current_step', 0)
        plan = state.get('plan', [])
        
        if current_step < len(plan):
            return "continue"
        else:
            return "end"
            
    workflow.add_conditional_edges(
        "researcher",
        should_continue,
        {
            "continue": "researcher",
            "end": "responder"
        }
    )
    
    workflow.add_edge("responder", END)
    
    # Checkpointer for Persistence
    conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
    memory = SqliteSaver(conn)
    
    # Compile
    app = workflow.compile(checkpointer=memory)
    # print(app.get_graph().draw_mermaid())  <-- Commented out or removed

    return app
