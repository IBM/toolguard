from graphviz import Digraph
from PIL import Image

def visualize_langgraph():
    # Create a directed graph
    dot = Digraph(comment="LangGraph Structure", format="png")

    # Define the nodes
    nodes = [
        "START",
        "planner",
        "execute_step",
        "draft_FC",
        #"FC_Reflector",
        "ToolGuard",
        "Execute_Tool",
        "review",
        "replan",
        "parse_response",
        "END"
    ]

    # Add nodes to the graph
    for node in nodes:
        dot.node(node)

    # Add edges based on your LangGraph logic
    edges = [
        ("START", "planner"),
        ("planner", "execute_step"),
        ("execute_step", "draft_FC"),
        #("draft_FC", "FC_Reflector"),
        #("FC_Reflector", "ToolGuard"),
        #("FC_Reflector", "execute_step"),
        ("draft_FC", "ToolGuard"),
        ("ToolGuard", "execute_step"),
        ("ToolGuard", "Execute_Tool"),
        ("Execute_Tool", "review"),
        ("review", "replan"),
       
        ("replan", "execute_step"),
        ("replan", "parse_response"),
        ("parse_response", "END"),
        # The following nodes are in the graph but not connected in your method.
        # You can connect them here if needed.
        # ("agent", "review_reflection"),
        # ("review_reflection", "guardrails"),
        # ("guardrails", "answer")
    ]

    for src, dst in edges:
        dot.edge(src, dst)

    # Render to a PNG image
    output_path = "langgraph_visual"
    dot.render(output_path, cleanup=True)

    # Display image using PIL
    img = Image.open(output_path + ".png")
    img.show()

# Call the function to generate and show the graph
visualize_langgraph()
