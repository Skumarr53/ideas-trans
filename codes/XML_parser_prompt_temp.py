**Prompt Template:**

Task: XML Metadata Path Extraction for Bulk Processing

Objective:
Analyze the provided XML content to identify all element tags and attribute paths that contain metadata relevant to the user's query. Generate a dictionary where each key is a metadata field name and each value is its full hierarchical path in XPath-like format (without positional indices). These paths will be reused programmatically for extracting information from bulk XML files.

Inputs:
1. User Query: "We will need to parse RIXML file to convert the labels into structured tables. Example columns include publication date, broker name, analyst names, tickers, asset class (equities, fixed income or macro), price target, report type, event type, rating


Processing Instructions:
1. Understand the metadata requirements from the user query
2. Analyze the XML structure thoroughly, including nested elements
3. Identify all possible paths that could contain relevant metadata
4. For attributes, use the format `parent_tag/@attribute_name`
5. Exclude any positional indices (e.g., use `/root/item` instead of `/root/item[1]`)
6. Include only paths that directly contain metadata values (not structural elements)
7. For repeated elements with the same metadata role, use the generic path without indices
8. Group related metadata fields when appropriate

Output Requirements:
- Return ONLY a Python dictionary in this exact format:
{
    "metadata_field1": "full/path/to/element_or_attribute",
    "metadata_field2": "another/path/@attribute",
    ...
}
- Dictionary keys should be descriptive field names derived from either:
  a) The user query's terminology, OR
  b) The XML element/attribute names if clearer
- Ensure all paths are valid and complete from the root
- Include all relevant metadata fields, not just the most obvious ones

Example Output:
{
    "document_title": "book/metadata/title",
    "publication_date": "book/metadata/pubdate",
    "author_name": "book/metadata/creator/@fullname",
    "isbn": "book/metadata/identifier[@type='isbn']"
}

Now process the provided inputs and return ONLY the dictiona