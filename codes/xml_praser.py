"""
Robust XML extraction for sell-side research documents.
- Designed for clarity, maintainability, and extensibility.
- Supports RIXML-based research report samples.

Extracts: publication date, broker name, analyst names, tickers, asset class, price target, report type, event type, and rating.
"""
import os
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from glob import glob

def parse_analysts(org_elem) -> List[Dict[str, Any]]:
    analysts = []
    ns = {'rixml': 'http://www.rixml.org/2005/3/RIXML'}
    for pg in org_elem.findall('.//rixml:PersonGroupMember', ns):
        person = pg.find('rixml:Person', ns)
        if person is not None:
            analysts.append({
                'name': person.findtext('rixml:DisplayName', default='', namespaces=ns),
                'job_title': person.findtext('rixml:JobTitle', default='', namespaces=ns),
                'email': person.findtext('rixml:ContactInfo/rixml:Email', default='', namespaces=ns),
            })
    return analysts

def parse_tickers(security_elem) -> List[Dict[str, Any]]:
    tickers = []
    ns = {'rixml': 'http://www.rixml.org/2005/3/RIXML'}
    for secid in security_elem.findall('.//rixml:SecurityID', ns):
        tickers.append({
            'id_type': secid.attrib.get('idType', ''),
            'id_value': secid.attrib.get('idValue', ''),
            'exchange': secid.findtext('rixml:TradingExchange', default='', namespaces=ns)
        })
    return tickers

def parse_price_target(security_elem) -> Optional[Dict[str, Any]]:
    ns = {'rixml': 'http://www.rixml.org/2005/3/RIXML'}
    for fin in security_elem.findall('.//rixml:SecurityFinancials', ns):
        if fin.attrib.get('securityFinancialsType') == 'TargetPrice' and fin.attrib.get('priorCurrent') == 'Current':
            return {
                'currency': fin.findtext('rixml:Currency', default='', namespaces=ns),
                'value': fin.findtext('rixml:FinancialValue', default='', namespaces=ns)
            }
    return None

def parse_rating(security_elem) -> Optional[str]:
    ns = {'rixml': 'http://www.rixml.org/2005/3/RIXML'}
    for rating in security_elem.findall('.//rixml:Rating', ns):
        if rating.attrib.get('priorCurrent') == 'Current':
            return rating.findtext('rixml:PublisherDefinedValue', default='', namespaces=ns)
    return None

def parse_asset_class(security_elem) -> Optional[str]:
    ns = {'rixml': 'http://www.rixml.org/2005/3/RIXML'}
    ac = security_elem.find('.//rixml:AssetClass', ns)
    if ac is not None:
        return ac.attrib.get('assetClass', '')
    return None

def extract_xml_info(xml_path: str) -> Dict[str, Any]:
    ns = {'rixml': 'http://www.rixml.org/2005/3/RIXML'}
    tree = ET.parse(xml_path)
    root = tree.getroot()
    product = root.find('.//rixml:Product', ns)
    context = root.find('.//rixml:Context', ns)
    data = {}

    # Publication date
    pub_elem = product.find('.//rixml:ProductDetails', ns)
    data['publication_date'] = pub_elem.attrib.get('publicationDateTime') if pub_elem is not None else None

    # Broker name
    org = product.find('.//rixml:Source/rixml:Organization[@primaryIndicator="Yes"]', ns)
    data['broker_name'] = org.findtext('rixml:OrganizationName', default='', namespaces=ns) if org is not None else None

    # Analysts
    data['analysts'] = parse_analysts(org) if org is not None else []

    # Tickers/Identifiers (all issuers)
    data['issuers'] = []
    if context is not None:
        for issuer in context.findall('.//rixml:Issuer', ns):
            issuer_name = issuer.findtext('rixml:IssuerName/rixml:NameValue', default='', namespaces=ns)
            securities = issuer.findall('.//rixml:SecurityDetails/rixml:Security', ns)
            for sec in securities:
                entry = {
                    'issuer_name': issuer_name,
                    'tickers': parse_tickers(sec),
                    'asset_class': parse_asset_class(sec),
                    'price_target': parse_price_target(sec),
                    'rating': parse_rating(sec)
                }
                data['issuers'].append(entry)

    # Asset class (product-level if available)
    ac = product.find('.//rixml:AssetClass', ns)
    data['product_asset_class'] = ac.attrib.get('assetClass', '') if ac is not None else None

    # Report type & event type (from ProductClassifications/Subject)
    classifications = product.find('.//rixml:ProductClassifications', ns)
    data['report_types'] = []
    data['event_types'] = []
    if classifications is not None:
        for subj in classifications.findall('.//rixml:Subject', ns):
            publisher_val = subj.attrib.get('publisherDefinedValue', '')
            if publisher_val:
                if 'event' in publisher_val.lower():
                    data['event_types'].append(publisher_val)
                else:
                    data['report_types'].append(publisher_val)
        for discipline in classifications.findall('.//rixml:Discipline', ns):
            val = discipline.attrib.get('disciplineType', '')
            if val:
                data['report_types'].append(val)
    data['report_types'] = list(set(data['report_types']))
    data['event_types'] = list(set(data['event_types']))
    return data

def parse_directory(directory: str) -> List[Dict[str, Any]]:
    results = []
    for path in glob(os.path.join(directory, '*.xml')):
        try:
            info = extract_xml_info(path)
            info['filename'] = os.path.basename(path)
            results.append(info)
        except Exception as e:
            print(f"Error processing {path}: {e}")
    return results

# Example usage:
# directory = '/mnt/data/'
# results = parse_directory(directory)
# import json; print(json.dumps(results, indent=2))


--------------

import pandas as pd
from typing import List, Dict, Any, Optional

def format_common_info(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and format the common info shared across issuers in a doc."""
    return {
        'filename': doc.get('filename'),
        'publication_date': doc.get('publication_date'),
        'broker_name': doc.get('broker_name'),
        'analysts': ', '.join([a['name'] for a in doc.get('analysts', [])]),
        'product_asset_class': doc.get('product_asset_class'),
        'report_types': ', '.join(doc.get('report_types', [])),
        'event_types': ', '.join(doc.get('event_types', [])),
    }

def format_issuer_row(
    common_info: Dict[str, Any],
    issuer: Optional[Dict[str, Any]] = None,
    ticker: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Combine common info, issuer, and ticker info into one row."""
    row = common_info.copy()
    row.update({
        'issuer_name': issuer.get('issuer_name') if issuer else None,
        'asset_class': issuer.get('asset_class') if issuer else None,
        'ticker_id_type': ticker.get('id_type') if ticker else None,
        'ticker_id_value': ticker.get('id_value') if ticker else None,
        'ticker_exchange': ticker.get('exchange') if ticker else None,
        'price_target_value': (issuer.get('price_target') or {}).get('value') if issuer else None,
        'price_target_currency': (issuer.get('price_target') or {}).get('currency') if issuer else None,
        'rating': issuer.get('rating') if issuer else None,
    })
    return row

def flatten_issuer_rows(parsed_docs: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Returns a DataFrame with one row per issuer-ticker per document.
    """
    rows = []
    for doc in parsed_docs:
        common_info = format_common_info(doc)
        issuers = doc.get('issuers', [])
        if not issuers:
            # For macro/no-issuer reports
            rows.append(format_issuer_row(common_info))
            continue
        for issuer in issuers:
            tickers = issuer.get('tickers', []) or [{}]  # At least one row per issuer
            for ticker in tickers:
                rows.append(format_issuer_row(common_info, issuer, ticker))
    return pd.DataFrame(rows)

# Example usage:
# df = flatten_issuer_rows(parsed_docs)
