import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from state import AgentState
from tools import tools

# LLM Setup
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash", convert_system_message_to_human=True)
except ImportError:
    llm_gemini = None
    print("Warning: langchain-google-genai not installed. Fallback disabled.")

llm_primary = ChatOpenAI(model="gpt-5-nano")

def invoke_llm_with_fallback(messages, tools=None):
    """Tries llm_primary, falls back to Gemini on error."""
    try:
        if tools:
            # Note: binding tools creates a new Runnable
            runnable = llm_primary.bind_tools(tools)
            return runnable.invoke(messages)
        else:
            return llm_primary.invoke(messages)
    except Exception as e:
        print(f"Primary LLM unavailable. Using fallback model (Gemini)...")
        if llm_gemini:
            try:
                if tools:
                    runnable = llm_gemini.bind_tools(tools)
                    return runnable.invoke(messages)
                else:
                    return llm_gemini.invoke(messages)
            except Exception as e2:
                raise Exception(f"Fallback LLM also failed: {e2}") from e
        else:
             raise e

# ... Update nodes to use invoke_llm_with_fallback ...
# I will do this in chunks.


def planner_node(state: AgentState):
    """Generates a research plan based on the topic."""
    try:
        print("\n")
        print("--- PLANNER NODE ---")
        user_input = state['topic']
        messages = state.get('messages', [])
        
        # Simple history context
        history = "\n".join(messages[-5:]) if messages else "No history."

        prompt = f"""You are a research planner. Use the following conversation history for context if needed.
        
        History:
        {history}

        Current Request: '{user_input}'

        Create a research plan based on the request.

        Rules:
        1. If the request is about 'the creator' or 'who created this', return exactly ONE step: 'Who is the creator?'.
        2. For all OTHER requests, create a list of 3 specific search queries or retrieval tasks.

        Return ONLY the queries separated by newlines."""
        
        response = invoke_llm_with_fallback([HumanMessage(content=prompt)])
        plan = [line.strip() for line in response.content.split('\n') if line.strip()]
        
        print(f"Plan Generated: {plan}")

        # We return 'findings': [] to reset findings for this new turn/plan
        # We return 'current_step': 0 to reset the step counter
        return {
            "plan": plan, 
            "messages": [f"Plan created for '{user_input}' with {len(plan)} steps."],
            "findings": [],         # OVERWRITE findings for the new turn
            "current_step": 0       # OVERWRITE step counter
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "plan": [],
            "messages": [f"Error creating plan: {e}"],
            "findings": [],
            "current_step": 0
        }

from tools import tools

def researcher_node(state: AgentState):
    """Executes the current step in the plan using native tool calling."""
    try:
        print("\n")
        print("--- RESEARCHER NODE ---")
        plan = state.get('plan', [])
        current_step = state.get('current_step', 0)
        
        print(f"Debug: Step={current_step}, PlanLen={len(plan)}")

        if current_step >= len(plan):
            print("Research plan execution complete.")
            return {"current_step": current_step} 
            
        query = plan[current_step]
        print(f"Executing Step {current_step + 1}/{len(plan)}: {query}")
        
        # Filter tools: Only use RAG (retrieve_documents) for questions about the creator
        topic = state.get('topic', '').lower()
        active_tools = list(tools)
        
        if "creator" not in topic and "creator" not in query.lower():
            active_tools = [t for t in active_tools if t.__name__ != 'retrieve_documents']
        
        
        # System prompt to guide tool usage
        messages = [
            SystemMessage(content="""You are a research assistant. You have access to search tools. Use them to find information for the user's query.

RULES:
1. If the query asks about the 'creator', 'who created this', or 'author', you MUST use the 'retrieve_documents' tool. Do NOT answer from internal knowledge.
2. For all other queries, use web search or other tools, but do NOT use 'retrieve_documents'."""),
            HumanMessage(content=f"Query: {query}")
        ]
        
        response = invoke_llm_with_fallback(messages, tools=active_tools)
        
        findings = []
        messages_log = []
        
        if response.tool_calls:
            print(f"Tool(s) Selected: {[tc['name'] for tc in response.tool_calls]}")
            
            # Create a map of tool names to functions
            tool_map = {t.__name__: t for t in tools}
            
            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                
                if tool_name in tool_map:
                    try:
                        # Execute the tool
                        tool_func = tool_map[tool_name]
                        result = tool_func(**tool_args)
                        
                        finding = f"Query: {query}\nSource: {tool_name}\nResult: {result}"
                        findings.append(finding)
                        messages_log.append(f"Executed {tool_name} for: {query}")
                    except Exception as e:
                        findings.append(f"Error executing {tool_name}: {e}")
                else:
                    findings.append(f"Error: Tool {tool_name} not found.")
        else:
            # Fallback if no tool was called (LLM answered directly)
            print("No tool selected. LLM answered directly.")
            findings.append(f"Query: {query}\nSource: LLM Internal Knowledge\nResult: {response.content}")
            messages_log.append(f"LLM answered directly for: {query}")

        return {
            "findings": findings,
            "current_step": current_step + 1,
            "messages": messages_log
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_step = state.get('current_step', 0)
        return {
            "current_step": current_step + 1,
            "messages": [f"Error in researcher node: {e}"]
        }

def responder_node(state: AgentState):
    """Synthesizes the final answer."""
    print("\n")
    print("--- RESPONDER NODE ---")
    topic = state['topic']
    # ...
    topic = state['topic']
    findings = state['findings']
    
    context = "\n\n".join(findings)
    prompt = f"""You are a research assistant. Synthesize a comprehensive answer for the topic '{topic}' based on the following findings:

{context}

If the findings contain error messages (e.g., 'Error executing...'), explicitly apologize to the user and explain what went wrong, rather than trying to construct an answer from the error text.
Provide citations where possible."""
    
    response = invoke_llm_with_fallback([HumanMessage(content=prompt)])
    print("Response generated.")
    
    return {"messages": [response.content]}
