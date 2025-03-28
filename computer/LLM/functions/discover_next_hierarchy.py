"""
Hierarchy Sequence Finder
Discovers the next available hierarchy file number in a sequence.
Features:
- Scans existing hierarchy files
- Identifies the next available sequential number
- Supports configurable path settings
- Simple output reporting
- Sequential file naming convention support
"""

import os

# Sample result
# The next hierarchy file to create is: 2.json

# Configuration
HIERARCHIES_BASE_PATH = "../Transformer.codes/hierarchies/"

def discover_next_hierarchy():
    """
    Discover the next non-existing hierarchy file number in sequence.
    
    Iterates through numbered files until finding the first gap in the sequence.
    
    Returns:
        int: The next available hierarchy number
    """
    i = 1
    while True:
        hierarchy_file_name = f"{i}.json"
        hierarchy_path = os.path.join(HIERARCHIES_BASE_PATH, hierarchy_file_name)

        # Break the loop when we find a non-existent file
        if not os.path.exists(hierarchy_path):
            break

        i += 1
    
    print(f"The next hierarchy file to create is: {hierarchy_file_name}")

if __name__ == "__main__":
    discover_next_hierarchy()
