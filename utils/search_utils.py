# utils/search_utils.py

import requests

def search_pdb_by_virus_name(virus_name, max_results=10):
    """
    Search RCSB PDB by virus/organism name.
    Returns a list of matching PDB entries (with ID and title).
    """
    search_url = "https://search.rcsb.org/rcsbsearch/v2/query"

    query = {
        "query": {
            "type": "terminal",
            "service": "text",
            "parameters": {
                "attribute": "rcsb_entity_source_organism.taxonomy_lineage.name",
                "operator": "exact_match",
                "value": virus_name
            }
        },
        "return_type": "entry",
        "request_options": {
            "paginate": {
                "start": 0,
                "rows": max_results
            },
            "scoring_strategy": "combined"
        }
    }

    response = requests.post(search_url, json=query)
    if response.status_code != 200:
        return []

    result = response.json().get("result_set", [])
    pdb_ids = [entry["identifier"] for entry in result]

    # Fetch metadata (titles) for each PDB ID
    entries = []
    for pdb_id in pdb_ids:
        metadata_url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
        meta_response = requests.get(metadata_url)
        if meta_response.status_code == 200:
            data = meta_response.json()
            title = data.get("struct", {}).get("title", "No description")
            entries.append({"pdb_id": pdb_id, "title": title})
        else:
            entries.append({"pdb_id": pdb_id, "title": "Unknown title"})

    return entries
