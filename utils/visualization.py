# utils/visualization.py

import streamlit as st
import streamlit.components.v1 as components
import py3Dmol

def show_pdb_structure(pdb_string, style="cartoon", width=200, height=300):
    """
    Render a single molecule in 3D from PDB string.
    """
    view = py3Dmol.view(width=width, height=height)
    view.addModel(pdb_string, "pdb")
    view.setStyle({style: {}})
    view.zoomTo()
    view.setBackgroundColor("white")

    # Center the viewer on the page
    col1, col2, col3 = st.columns([1, 5, 1])
    with col2:
        return components.html(view._make_html(), height=height)

def show_complex_structure(receptor_pdb, ligand_pdb, width=200, height=300):
    """
    Render receptor and ligand together in one 3D window.
    Receptor = cartoon, Ligand = stick.
    """
    view = py3Dmol.view(width=width, height=height)
    view.addModel(receptor_pdb, "pdb")
    view.setStyle({"model": 0}, {"cartoon": {"color": "spectrum"}})
    view.addModel(ligand_pdb, "pdb")
    view.setStyle({"model": 1}, {"stick": {"colorscheme": "greenCarbon"}})
    view.zoomTo()
    view.setBackgroundColor("white")

    # Center the viewer on the page
    col1, col2, col3 = st.columns([1, 5, 1])
    with col2:
        return components.html(view._make_html(), height=height)
def show_pose_on_receptor(receptor_pdb, ligand_poses, pose_index=0, label_text=None, show_atom_labels=False, width=1000, height=600):
    import py3Dmol

    view = py3Dmol.view(width=width, height=height)
    view.addModel(receptor_pdb, "pdb")
    view.setStyle({"model": 0}, {"cartoon": {"color": "spectrum"}})

    if pose_index < len(ligand_poses):
        ligand_pdb = ligand_poses[pose_index]
        view.addModel(ligand_pdb, "pdb")
        view.setStyle({"model": 1}, {"stick": {"colorscheme": "greenCarbon"}})

        lines = ligand_pdb.splitlines()

        # Add pose label
        if label_text:
            for line in lines:
                if line.startswith("ATOM") or line.startswith("HETATM"):
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    view.addLabel(label_text, {
                        "position": {"x": x, "y": y, "z": z},
                        "backgroundColor": "black",
                        "fontColor": "white",
                        "fontSize": 14
                    })
                    break

        # Add atom labels if enabled
        if show_atom_labels:
            for line in lines:
                if line.startswith("ATOM") or line.startswith("HETATM"):
                    atom_name = line[12:16].strip()
                    res_name = line[17:20].strip()
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    label = f"{atom_name} ({res_name})"
                    view.addLabel(label, {
                        "position": {"x": x, "y": y, "z": z},
                        "backgroundColor": "blue",
                        "fontColor": "white",
                        "fontSize": 10,
                        "borderThickness": 0.5
                    })

    view.zoomTo()
    view.setBackgroundColor("white")
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.components.v1.html(view._make_html(), height=height)

