from graphviz import Digraph
from PIL import Image

def visualize_langgraph():
    # Create a directed graph
    workflow = Digraph(comment="LangGraph Structure", format="png")
    workflow.node("policy_creator")

    workflow.node("split")
    workflow.node("merge")
    workflow.node("review_policy")
    workflow.node("add_policies")
    workflow.node("add_references")
    workflow.node("reference_correctness")
    workflow.node("example_creator")
    workflow.node("add_examples")
    workflow.node("final")

    #workflow.set_entry_point("policy_creator")

    workflow.edge("policy_creator", "add_policies")
    # workflow.add_conditional_edges("add_policies", lambda state: "merge_and_split" if state.get("stop", False) else "add_policies" )
    # workflow.add_edge("merge_and_split", "review_policy")
    workflow.edge("add_policies","split")
    workflow.edge("add_policies", "add_policies")
    
    workflow.edge("split", "merge")
    workflow.edge("merge", "review_policy")
    workflow.edge("review_policy", "add_references")
    workflow.edge("add_references", "reference_correctness")
    workflow.edge("reference_correctness", "example_creator")
    workflow.edge("example_creator", "add_examples")
    workflow.edge("add_examples","final")
    workflow.edge("add_examples","add_examples")
    
  
    # for src, dst in edges:
    #     workflow.edge(src, dst)

    # Render to a PNG image
    output_path = "step 1"
    workflow.render(output_path, cleanup=True)

    # Display image using PIL
    img = Image.open(output_path + ".png")
    img.show()

# Call the function to generate and show the graph
visualize_langgraph()
