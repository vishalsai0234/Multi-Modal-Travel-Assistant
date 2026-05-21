"""
generate_graph.py

Run this once to generate the graph.png required for submission.
Usage: python generate_graph.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from graph.builder import build_graph, generate_graph_image

print("Building graph...")
app = build_graph(use_memory=False)

print("Generating graph.png...")
generate_graph_image(app, "graph.png")

print("Done! graph.png saved.")
