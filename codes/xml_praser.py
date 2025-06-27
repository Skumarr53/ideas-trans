import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET
from collections import defaultdict

def get_namespace(root):
    # Extract XML namespace, e.g., '{http://www.rixml.org/2013/2/RIXML}'
    if root.tag[0] == '{':
        return root.tag[1:].split('}')[0]
    return ''

def find_first(elem, path, ns):
    # Like elem.find(), but returns '' if not found
    try:
        if ns:
            res = elem.find(path, namespaces={'ns': ns})
        else:
            res = elem.find(path)
        return res if res is not None else None
    except Exception:
        return None

def findall(elem, path, ns):
    try:
        if ns:
            return elem.findall(path, namespaces={'ns': ns})
        else:
            return elem.findall(path)
    except Exception:
        return []

def extract_analysts(source_elem, ns):
    analysts = []
    for person_group in findall(source_elem, ".//ns:PersonGroup", ns):
        for member in findall(person_group, ".//ns:PersonGroupMember", ns):
            person = find_first(member, ".//ns:Person", ns)
            if person is not None:
                analyst = {
                    "analyst_display_name": (find_first(person, "ns:DisplayName", ns) or find_first(person, "DisplayName", ns) or '').text if find_first(person, "ns:DisplayName", ns) is not None or find_first(person, "DisplayName", ns) is not None else '',
                    "analyst_email": '',
                }
                email_node = find_first(person, ".//ns:ContactInfo/ns:Email", ns) or find_first(person, ".//ContactInfo/Email", ns)
                analyst["analyst_email"] = email_node.text if email_node is not None else ''
                analysts.append(analyst)
    return analysts

def extract_issuer_info(issuer_elem, ns):
    # Handles one Issuer node (can be called multiple times per file)
    issuer = {
        "issuer_name": '',
        "ticker": '',
        "asset_class": '',
        "price_target": '',
        "currency": '',
        "rating": '',
        "rating_action": '',
        "coverage_action": '',
        "target_price_action": '',
        "isin": '',
        "cusip": '',
        "bloomberg": '',
    }
    # Name
    name_node = find_first(issuer_elem, ".//ns:IssuerName/ns:NameValue", ns) or find_first(issuer_elem, ".//IssuerName/NameValue", ns)
    if name_node is not None:
        issuer["issuer_name"] = name_node.text
    # Security Details
    for security in findall(issuer_elem, ".//ns:SecurityDetails/ns:Security", ns):
        # Ticker: Try to get any recognized id
        for secid in findall(security, "ns:SecurityID", ns):
            idtype = secid.attrib.get('idType', '').upper()
            val = secid.attrib.get('idValue', '')
            if not issuer["ticker"] and idtype in ("BLOOMBERG", "RIC", "PUBLISHERDEFINED"):
                issuer["ticker"] = val
            if idtype == "ISIN":
                issuer["isin"] = val
            if idtype == "CUSIP":
                issuer["cusip"] = val
            if idtype == "BLOOMBERG":
                issuer["bloomberg"] = val
        # Asset class
        ac_node = find_first(security, "ns:AssetClass", ns) or find_first(security, "AssetClass", ns)
        if ac_node is not None and 'assetClass' in ac_node.attrib:
            issuer["asset_class"] = ac_node.attrib['assetClass']
        # Price target
        for sf in findall(security, "ns:SecurityFinancials", ns) + findall(security, "SecurityFinancials", ns):
            if sf.attrib.get('securityFinancialsType', '').lower() == "targetprice":
                pt_val = find_first(sf, "ns:FinancialValue", ns) or find_first(sf, "FinancialValue", ns)
                if pt_val is not None:
                    issuer["price_target"] = pt_val.text
                cur = find_first(sf, "ns:Currency", ns) or find_first(sf, "Currency", ns)
                if cur is not None:
                    issuer["currency"] = cur.text
        # Rating (publisher defined)
        for rating in findall(security, "ns:Rating", ns) + findall(security, "Rating", ns):
            pdv = find_first(rating, "ns:PublisherDefinedValue", ns) or find_first(rating, "PublisherDefinedValue", ns)
            if pdv is not None and pdv.text:
                issuer["rating"] = pdv.text
                issuer["rating_action"] = rating.attrib.get('ratingAction', '')
            elif 'rating' in rating.attrib:
                issuer["rating"] = rating.attrib['rating']
                issuer["rating_action"] = rating.attrib.get('ratingAction', '')
        # Coverage/target price actions
        if 'coverageAction' in security.attrib:
            issuer["coverage_action"] = security.attrib['coverageAction']
        if 'targetPriceAction' in security.attrib:
            issuer["target_price_action"] = security.attrib['targetPriceAction']
    return issuer

def extract_report_metadata(root, ns):
    # General report-level info (same for all issuers in this file)
    meta = defaultdict(str)
    # Publication date
    pub_date = ''
    pd_node = find_first(root, ".//ns:ProductDetails", ns)
    if pd_node is not None:
        pub_date = pd_node.attrib.get('publicationDateTime', '')
    else:
        # Fallback for older schema
        pd_node = find_first(root, ".//ProductDetails", ns)
        if pd_node is not None:
            pub_date = pd_node.attrib.get('publicationDateTime', '')
    meta['publication_date'] = pub_date
    # Broker info
    source_node = find_first(root, ".//ns:Source", ns) or find_first(root, ".//Source", ns)
    if source_node is not None:
        org_node = find_first(source_node, ".//ns:Organization", ns) or find_first(source_node, ".//Organization", ns)
        if org_node is not None:
            broker = find_first(org_node, "ns:OrganizationName", ns) or find_first(org_node, "OrganizationName", ns)
            if broker is not None:
                meta['broker_name'] = broker.text
    # Report title/type
    content_node = find_first(root, ".//ns:Content", ns) or find_first(root, ".//Content", ns)
    if content_node is not None:
        title = find_first(content_node, "ns:Title", ns) or find_first(content_node, "Title", ns)
        if title is not None:
            meta['report_title'] = title.text
    # Report type/classification
    context_node = find_first(root, ".//ns:Context", ns) or find_first(root, ".//Context", ns)
    if context_node is not None:
        # Report type (e.g., Company Note, Update)
        prod_node = find_first(context_node, ".//ns:ProductDetails", ns) or find_first(context_node, ".//ProductDetails", ns)
        if prod_node is not None:
            meta['report_type'] = prod_node.findtext("ns:ProductName", namespaces={'ns': ns}) or prod_node.findtext("ProductName")
        # Event type
        classif_node = find_first(context_node, ".//ns:ProductClassifications", ns) or find_first(context_node, ".//ProductClassifications", ns)
        if classif_node is not None:
            for subj in findall(classif_node, "ns:Subject", ns) + findall(classif_node, "Subject", ns):
                if 'publisherDefinedValue' in subj.attrib:
                    meta['event_type'] = subj.attrib['publisherDefinedValue']
    return dict(meta)

def extract_all_from_file(xml_path):
    # Main extraction for one XML file
    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = get_namespace(root)
    ns = ns if ns else None

    report_meta = extract_report_metadata(root, ns)
    source_node = find_first(root, ".//ns:Source", ns) or find_first(root, ".//Source", ns)
    analysts = extract_analysts(source_node, ns) if source_node is not None else []
    # Multiple issuers per file
    context_node = find_first(root, ".//ns:Context", ns) or find_first(root, ".//Context", ns)
    issuer_details_node = find_first(context_node, ".//ns:IssuerDetails", ns) or find_first(context_node, ".//IssuerDetails", ns)
    if issuer_details_node is None:
        issuer_details_node = find_first(root, ".//ns:IssuerDetails", ns) or find_first(root, ".//IssuerDetails", ns)
    all_issuer_rows = []
    for issuer in findall(issuer_details_node, ".//ns:Issuer", ns) + findall(issuer_details_node, ".//Issuer", ns):
        issuer_info = extract_issuer_info(issuer, ns)
        row = {}
        row.update(report_meta)
        row['filename'] = os.path.basename(xml_path)
        # Analyst info: collapse to ; separated (could extend to column per analyst)
        row['analysts'] = "; ".join(
            ["{} <{}>".format(a['analyst_display_name'], a['analyst_email']) for a in analysts if a['analyst_display_name']]
        )
        row.update(issuer_info)
        all_issuer_rows.append(row)
    return all_issuer_rows

def process_folder(xml_folder):
    all_rows = []
    for xml_file in glob.glob(os.path.join(xml_folder, "*.xml")):
        try:
            all_rows.extend(extract_all_from_file(xml_file))
        except Exception as e:
            print(f"Failed to process {xml_file}: {e}")
    return pd.DataFrame(all_rows)

# Usage
# df = process_folder("/mnt/data/")
# display(df.head())

