import argparse
import uuid
from dotenv import load_dotenv
from graph import create_graph

# Load environment variables
load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="LangGraph Research Assistant")
    parser.add_argument("--topic", help="Research topic")
    parser.add_argument("--thread_id", help="Thread ID for persistence (optional)")
    args = parser.parse_args()
    
    # Determine Thread ID
    thread_id = args.thread_id or str(uuid.uuid4())
    print(f"Using Thread ID: {thread_id}")

    # Interactive Topic Input
    topic = args.topic
    if not topic:
        print("\n--- Research Assistant ---")
        topic = input("Enter research topic (or press Enter to resume existing thread): ").strip()

    # Initialize Graph
    app = create_graph()
    
    # Initial State
    initial_state = {}
    if topic:
        initial_state["topic"] = topic
        print(f"Starting research on: {topic}")
        
    config = {"configurable": {"thread_id": thread_id}}
    
    # Run the graph
    # Run the graph
    print("Agent ready. Type 'quit' to exit.")
    
    while True:
        try:
            if not topic:
                topic = input("\nUser (type 'quit' to exit): ").strip()
            
            if topic.lower() in ["quit", "exit"]:
                print("Goodbye!")
                break
                
            if not topic:
                continue

            print("Agent working...")
            
            # Run the graph for this turn
            inputs = {"topic": topic}
            
            for event in app.stream(inputs, config=config):
                for key, value in event.items():
                    if value and "messages" in value:
                        # Print the last message from the node
                        print(f"[{key.upper()}]: {value['messages'][-1]}")
            
            # Clear topic for next iteration
            topic = None

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception:
            import traceback
            traceback.print_exc()
            topic = None

if __name__ == "__main__":
    main()
