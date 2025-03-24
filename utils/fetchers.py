# utils/fetchers.py

import requests

def fetch_pdb_structure(pdb_id):
    """
    Fetch the PDB file content for a given PDB ID.
    Returns the raw PDB string or None if failed.
    """
    url = f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None
