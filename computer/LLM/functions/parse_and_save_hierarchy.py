"""
Hierarchy Parser
Converts indented text-based hierarchies into structured JSON format.
Features:
- Parses hierarchical numerical indexes (e.g., 1.2.3)
- Generates clean URL-friendly links automatically
- Supports nested subitem relationships
- Creates JSON with proper structure and indentation
- Handles multi-level hierarchies with unlimited depth
"""

import json

# Configuration
BASE_FILE_PATH = "../Transformer.codes/hierarchies"

def parse_and_save_hierarchy(text):
    """
    Parse a text-based hierarchy and save it as a structured JSON file.
   
    Args:
        text: String containing the hierarchical text with numerical indices
                in format like "1.2.3 Item Name"
    
    Returns:
        None - outputs JSON file to disk
    """
    # Split text into lines and parse each line into index and name
    lines = text.strip().split('\n')
    items = [line.strip().split(' ', 1) for line in lines if line.strip()]
    items = [(item[0].strip(), item[1].strip()) for item in items if len(item) == 2]

    def get_children(items, level=0):
        """
        Recursively extract hierarchical structure from the parsed items.
        
        Args:
            items: List of (index, name) tuples
            level: Current hierarchy depth level
            
        Returns:
            Tuple containing (list of nodes at this level, remaining items)
        """
        result = []
        while items:
            index, name = items[0]
            index_parts = index.split('.')
            if len(index_parts) <= level:
                break
            if len(index_parts) - 1 == level:
                items.pop(0)
                sub_items = []
                if items and len(items[0][0].split('.')) > level + 1:
                    sub_items, items = get_children(items, level + 1)
                node = {"name": name}
                if sub_items:
                    node['subItems'] = sub_items
                else:
                    # Create URL-friendly link for leaf nodes
                    href = f"/posts/{'-'.join(name.lower().split())}"
                    node.update({"id": int(''.join(index_parts)), "href": href})
                result.append(node)

        return result, items

    # Process the hierarchy starting with the root
    if items:
        root_index, root_name = items.pop(0)
        root_index_base = root_index.split('.')[0]
        children, _ = get_children(items, level=1)
        hierarchy = {
            "name": root_name,
            "subItems": children
        }
        
        # Save the resulting hierarchy to a JSON file
        file_path = f'{BASE_FILE_PATH}/{root_index_base}.json'
        with open(file_path, 'w') as json_file:
            json.dump(hierarchy, json_file, indent=4)
        
        print(f"JSON saved to {file_path}")
    else:
        print("Failed to parse the hierarchy.")

if __name__ == "__main__":
    index_text = '''
1 The Solar System
1.1 The Sun
1.1.1 Structure of the Sun
1.1.2 Solar Activity
1.1.3 Importance of the Sun
1.2 The Planets
1.2.1 The Terrestrial Planets
1.2.1.1 Mercury
1.2.1.2 Venus
1.2.1.3 Earth
1.2.1.4 Mars
1.2.2 The Jovian Planets
1.2.2.1 Jupiter
1.2.2.2 Saturn
1.2.2.3 Uranus
1.2.2.4 Neptune
1.3 Dwarf Planets
1.3.1 Pluto
1.3.2 Ceres
1.3.3 Eris
1.3.4 Makemake
1.3.5 Haumea
1.4 Asteroids
1.4.1 The Asteroid Belt
1.4.2 Composition of Asteroids
1.4.3 Notable Asteroids
1.5 Comets
1.5.1 Structure of Comets
1.5.2 Types of Comets
1.5.3 Famous Comets
1.6 Moons
1.6.1 Earth's Moon
1.6.2 The Galilean Moons
1.6.3 Other Notable Moons
1.7 Formation and Evolution of the Solar System
1.7.1 The Nebular Hypothesis
1.7.2 Early Stages of the Solar System
1.7.3 Evolution of the Planets
    '''
    parse_and_save_hierarchy(index_text)
