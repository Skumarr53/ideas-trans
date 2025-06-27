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


-------------------

import xml.etree.ElementTree as ET
def extract_xml_data(xml_content, paths):
    """
    Extracts data from XML content based on the provided paths.
    Args:
        xml_content (str): The XML content as a string.
        paths (dict): A dictionary mapping metadata fields to their XML paths.
    Returns:
        dict: A dictionary containing the extracted data.
    """
    # Parse the XML content
    root = ET.fromstring(xml_content)
    # Dictionary to store the extracted data
    extracted_data = {}
    # Iterate through the paths and extract the data
    for field, path in paths.items():
        try:
            # Handle attributes separately
            if "@" in path:
                # Split the path into the element path and the attribute name
                element_path, attribute = path.split("@")
                element = root.find(element_path)
                if element is not None:
                    extracted_data[field] = element.get(attribute)
            else:
                # Extract the text value of the element
                element = root.find(path)
                if element is not None:
                    extracted_data[field] = element.text
        except Exception as e:
            print(f"Error extracting {field}: {e}")
            extracted_data[field] = None
    return extracted_data
# Example XML content
xml_content = """
<Research researchID="12345" language="en" createDateTime="2023-10-01T12:00:00Z">
    <Product productID="P001" eventIndicator="true">
        <StatusInfo statusType="Published" statusDateTime="2023-10-01T12:30:00Z">
            <Version>1.0</Version>
        </StatusInfo>
        <Source>
            <Organization>
                <OrganizationID idType="LEI">987654321</OrganizationID>
                <OrganizationName>Research Org</OrganizationName>
                <PersonGroup>
                    <PersonGroupMember>
                        <Person>
                            <DisplayName>John Doe</DisplayName>
                            <ContactInfo>
                                <Email>john.doe@example.com</Email>
                            </ContactInfo>
                        </Person>
                    </PersonGroupMember>
                </PersonGroup>
            </Organization>
        </Source>
        <Content>
            <Title>Sample Research Report</Title>
            <Abstract>This is a sample abstract.</Abstract>
            <Synopsis>This is a sample synopsis.</Synopsis>
            <Resource sizeInBytes="1024" language="en">
                <Name>report.pdf</Name>
                <MIMEType>application/pdf</MIMEType>
                <Length>10</Length>
            </Resource>
        </Content>
    </Product>
    <Context>
        <IssuerDetails>
            <Issuer primaryIndicator="true" issuerType="Corporate" domicileCountryCode="US">
                <IssuerName>
                    <NameValue>Sample Issuer</NameValue>
                </IssuerName>
                <SecurityDetails>
                    <Security>
                        <SecurityID idType="ISIN" idValue="US1234567890">
                            <TradingExchange>NYSE</TradingExchange>
                        </SecurityID>
                        <SecurityFinancials securityFinancialsType="TargetPrice">
                            <FinancialValue>100.00</FinancialValue>
                            <Currency>USD</Currency>
                        </SecurityFinancials>
                        <Rating rating="Buy">
                            <PublisherDefinedValue>5</PublisherDefinedValue>
                        </Rating>
                        <AssetClass assetClass="Equity" />
                        <AssetType assetType="Common Stock" />
                        <SecurityType securityType="Stock" />
                    </Security>
                </SecurityDetails>
            </Issuer>
        </IssuerDetails>
        <ProductDetails publicationDateTime="2023-10-01T12:35:00Z">
            <ProductCategory productCategory="Research" />
            <ProductFocus focus="Equity" />
        </ProductDetails>
    </Context>
</Research>
"""
# Paths dictionary
paths = {
    "research_id": "Research/@researchID",
    "research_language": "Research/@language",
    "research_create_datetime": "Research/@createDateTime",
    "product_id": "Research/Product/@productID",
    "event_indicator": "Research/Product/@eventIndicator",
    "status_type": "Research/Product/StatusInfo/@statusType",
    "status_datetime": "Research/Product/StatusInfo/@statusDateTime",
    "version": "Research/Product/StatusInfo/Version",
    "organization_id_type": "Research/Product/Source/Organization/OrganizationID/@idType",
    "organization_id": "Research/Product/Source/Organization/OrganizationID",
    "organization_name": "Research/Product/Source/Organization/OrganizationName",
    "analyst_display_name": "Research/Product/Source/Organization/PersonGroup/PersonGroupMember/Person/DisplayName",
    "analyst_email": "Research/Product/Source/Organization/PersonGroup/PersonGroupMember/Person/ContactInfo/Email",
    "report_title": "Research/Product/Content/Title",
    "report_abstract": "Research/Product/Content/Abstract",
    "report_synopsis": "Research/Product/Content/Synopsis",
    "resource_name": "Research/Product/Content/Resource/Name",
    "resource_size_bytes": "Research/Product/Content/Resource/@sizeInBytes",
    "resource_mime_type": "Research/Product/Content/Resource/MIMEType",
    "resource_language": "Research/Product/Content/Resource/@language",
    "document_length_pages": "Research/Product/Content/Resource/Length",
    "issuer_primary_indicator": "Research/Context/IssuerDetails/Issuer/@primaryIndicator",
    "issuer_type": "Research/Context/IssuerDetails/Issuer/@issuerType",
    "issuer_domicile_country": "Research/Context/IssuerDetails/Issuer/@domicileCountryCode",
    "issuer_name": "Research/Context/IssuerDetails/Issuer/IssuerName/NameValue",
    "security_id_type": "Research/Context/IssuerDetails/Issuer/SecurityDetails/Security/SecurityID/@idType",
    "security_id_value": "Research/Context/IssuerDetails/Issuer/SecurityDetails/Security/SecurityID/@idValue",
    "trading_exchange": "Research/Context/IssuerDetails/Issuer/SecurityDetails/Security/SecurityID/TradingExchange",
    "target_price_value": "Research/Context/IssuerDetails/Issuer/SecurityDetails/Security/SecurityFinancials[@securityFinancialsType='TargetPrice']/FinancialValue",
    "target_price_currency": "Research/Context/IssuerDetails/Issuer/SecurityDetails/Security/SecurityFinancials[@securityFinancialsType='TargetPrice']/Currency",
    "rating": "Research/Context/IssuerDetails/Issuer/SecurityDetails/Security/Rating/@rating",
    "rating_value": "Research/Context/IssuerDetails/Issuer/SecurityDetails/Security/Rating/PublisherDefinedValue",
    "asset_class": "Research/Context/IssuerDetails/Issuer/SecurityDetails/Security/AssetClass/@assetClass",
    "asset_type": "Research/Context/IssuerDetails/Issuer/SecurityDetails/Security/AssetType/@assetType",
    "security_type": "Research/Context/IssuerDetails/Issuer/SecurityDetails/Security/SecurityType/@securityType",
    "product_publication_datetime": "Research/Context/ProductDetails/@publicationDateTime",
    "product_category": "Research/Context/ProductDetails/ProductCategory/@productCategory",
    "product_focus": "Research/Context/ProductDetails/ProductFocus/@focus"
}
# Extract data from the XML content
extracted_data = extract_xml_data(xml_content, paths)
# Print the extracted data
for field, value in extracted_data.items():
    print(f"{field}: {value}")