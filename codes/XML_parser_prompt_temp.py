### Prompt Template for XML Metadata Tag and Attribute Extraction

**Purpose:** Extract precise XML tags and attribute paths corresponding to user-requested metadata details from given XML content. These extracted paths should be reusable for similar XML structures.

**Prompt Template:**

---

You are provided with XML content and a user's query specifying certain metadata they wish to extract. Your task is:

1. **Carefully read and analyze the provided XML content.**
2. **Identify and clearly list the exact XML tags and attributes, including their full hierarchical paths,** that correspond directly to the requested metadata details.
3. **Present the extracted information in a structured and reusable format**, clearly distinguishing tags from attributes.

**User Query Example:**

```
"Identify tags and attributes paths for extracting: publication date, analyst name, ticker symbol, asset class, and price target."
```

**XML Content Example:**

```xml
<ResearchReport>
    <Header>
        <PublicationDate>2024-06-27</PublicationDate>
        <Broker name="Goldman Sachs" />
    </Header>
    <Body>
        <Analyst name="John Doe" />
        <Issuer>
            <Ticker>APPL</Ticker>
            <AssetClass>Equities</AssetClass>
            <PriceTarget currency="USD">180</PriceTarget>
        </Issuer>
    </Body>
</ResearchReport>
```

**Desired Response Format:**

```markdown
### Tags:
- Publication Date: `/ResearchReport/Header/PublicationDate`
- Ticker Symbol: `/ResearchReport/Body/Issuer/Ticker`
- Asset Class: `/ResearchReport/Body/Issuer/AssetClass`

### Attributes:
- Broker Name: `/ResearchReport/Header/Broker[@name]`
- Analyst Name: `/ResearchReport/Body/Analyst[@name]`
- Price Target (Currency): `/ResearchReport/Body/Issuer/PriceTarget[@currency]`
```

Ensure your response clearly separates tags and attributes and uses XPath-style notation for accuracy and ease of reuse.



----------------

import xml.etree.ElementTree as ET
from typing import Dict

def extract_metadata(xml_content: str) -> Dict[str, str]:
    tree = ET.ElementTree(ET.fromstring(xml_content))
    root = tree.getroot()

    def get_text(path: str) -> str:
        elem = root.find(path)
        return elem.text.strip() if elem is not None and elem.text else None

    def get_attribute(path: str, attr_name: str) -> str:
        elem = root.find(path)
        return elem.attrib.get(attr_name) if elem is not None else None

    return {
        # Tags
        "Publication Date": get_text("Header/PublicationDate"),
        "Ticker Symbol": get_text("Body/Issuer/Ticker"),
        "Asset Class": get_text("Body/Issuer/AssetClass"),

        # Attributes
        "Broker Name": get_attribute("Header/Broker", "name"),
        "Analyst Name": get_attribute("Body/Analyst", "name"),
        "Price Target (Currency)": get_attribute("Body/Issuer/PriceTarget", "currency"),
    }

# Example usage:
if __name__ == "__main__":
    sample_xml = """
    <ResearchReport>
        <Header>
            <PublicationDate>2024-06-27</PublicationDate>
            <Broker name="Goldman Sachs" />
        </Header>
        <Body>
            <Analyst name="John Doe" />
            <Issuer>
                <Ticker>APPL</Ticker>
                <AssetClass>Equities</AssetClass>
                <PriceTarget currency="USD">180</PriceTarget>
            </Issuer>
        </Body>
    </ResearchReport>
    """
    result = extract_metadata(sample_xml)
    for key, value in result.items():
        print(f"{key}: {value}")
