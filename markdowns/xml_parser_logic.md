import xml.etree.ElementTree as ET
from typing import List, Dict, Any

def get_all_tags(xml_content: str) -> List[str]:
    """Extracts all unique tag names from the given XML content."""
    root = ET.fromstring(xml_content)
    tags = set()
    for elem in root.iter():
        tags.add(elem.tag)
    return list(tags)

def fetch_tag_values(xml_content: str, tag_names: List[str]) -> Dict[str, List[Any]]:
    """Fetches all values (text) for the selected tags from the XML content."""
    root = ET.fromstring(xml_content)
    result = {tag: [] for tag in tag_names}
    for elem in root.iter():
        if elem.tag in tag_names:
            result[elem.tag].append(elem.text)
    return result

# Sample XML for testing
sample_xml = '''
<library>
    <book id="1">
        <title>Python 101</title>
        <author>John Doe</author>
        <year>2021</year>
    </book>
    <book id="2">
        <title>Data Science Handbook</title>
        <author>Jane Smith</author>
        <year>2020</year>
    </book>
    <magazine id="5">
        <title>AI Monthly</title>
        <month>June</month>
        <year>2024</year>
    </magazine>
</library>
'''

# Test logic
if __name__ == "__main__":
    tags = get_all_tags(sample_xml)
    print("All tags:", tags)
    # Fetch values for selected tags
    selected_tags = ['title', 'author', 'year']
    values = fetch_tag_values(sample_xml, selected_tags)
    print("\nValues for selected tags:")
    for tag, vals in values.items():
        print(f"{tag}: {vals}")
