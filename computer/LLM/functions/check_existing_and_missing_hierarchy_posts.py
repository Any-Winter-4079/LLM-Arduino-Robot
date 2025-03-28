"""
Hierarchy Post Checker
Checks for the existence of posts corresponding to the leaf nodes in a hierarchy.
Features:
- Recursively traverses JSON hierarchies
- Identifies missing and existing posts
- Handles directory-based post verification
- Supports configurable paths
- Simple reporting of results
"""

import os
import json

# Sample result
# For 1.json:

# Existing posts:
# - Earth
# - The Nebular Hypothesis

# Missing posts:
# - Structure of the Sun
# - Solar Activity
# ...

# Configuration
HIERARCHIES_BASE_PATH = "../Transformer.codes/hierarchies/"
POSTS_DIR = "../Transformer.codes/posts/"

def get_leaf_nodes(node):
    """
    Recursively extract leaf nodes from a hierarchy tree structure.
    
    Args:
        node: A dictionary representing a node in the hierarchy
        
    Returns:
        List of leaf nodes (nodes without children)
    """
    leaf_nodes = []
    if "subItems" in node:
        for sub_node in node["subItems"]:
            leaf_nodes.extend(get_leaf_nodes(sub_node))
    else:
        leaf_nodes.append(node)
    return leaf_nodes

def check_existing_and_missing_hierarchy_posts(hierarchy_file_name):
    """
    Check which posts exist and which are missing based on a hierarchy file.
    
    Args:
        hierarchy_file_name: Path to the hierarchy JSON file
        
    Returns:
        None - results are printed to console
    """
    # Load hierarchy definition from JSON file
    with open(hierarchy_file_name, "r") as f:
        hierarchy = json.load(f)

    # Extract all leaf nodes from the hierarchy
    leaf_nodes = get_leaf_nodes(hierarchy)

    # Check existence of each post
    existing_posts = []
    missing_posts = []
    for node in leaf_nodes:
        post_name = node["href"].split("/")[-1]
        post_path = os.path.join(POSTS_DIR, post_name + ".js")
        if os.path.exists(post_path):
            existing_posts.append(node)
        else:
            missing_posts.append(node)

    # Report results
    print("Existing posts:")
    for post in existing_posts:
        print(f"- {post['name']}")

    print("\nMissing posts:")
    for post in missing_posts:
        print(f"- {post['name']}")

if __name__ == "__main__":
    hierarchy_path = f"{HIERARCHIES_BASE_PATH}/1.json"
    check_existing_and_missing_hierarchy_posts(hierarchy_path)
