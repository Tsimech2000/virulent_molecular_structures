# app.py

import streamlit as st
import os
from utils.search_utils import search_pdb_by_virus_name
from utils.fetchers import fetch_pdb_structure
from utils.docking import extract_and_convert_poses
from utils.visualization import show_pdb_structure, show_pose_on_receptor

st.set_page_config(page_title="Pathogen–Host Interaction Simulator", layout="wide")

st.title("🧬 Pathogen–Host Interaction Simulator")
st.markdown("Simulate and visualize how pathogen molecules interact with host proteins.")

# Sidebar for interaction type
interaction_type = st.sidebar.selectbox(
    "Select Interaction Type",
    ["Protein–Protein Interaction", "Small Molecule–Protein Interaction"]
)

# ----------------------------
# 🔍 Virus Name Search Section
# ----------------------------

st.sidebar.markdown("### Search by Virus Name")
virus_query = st.sidebar.text_input("Enter virus/organism name (e.g., SARS-CoV-2)")

selected_pdb_id = None
pdb_content = None

if virus_query:
    st.sidebar.info("Searching PDB...")
    results = search_pdb_by_virus_name(virus_query)

    if results:
        options = [f"{r['pdb_id']} – {r['title']}" for r in results]
        selected = st.sidebar.selectbox("Select a structure", options)
        selected_pdb_id = selected.split(" – ")[0]
        st.success(f"Selected PDB ID: {selected_pdb_id}")

        # Fetch PDB structure
        pdb_content = fetch_pdb_structure(selected_pdb_id)

        if pdb_content:
            st.markdown("### 🧾 Fetched PDB Structure")
            st.code(pdb_content[:1000] + "\n...", language="pdb")

            # Save to local file
            os.makedirs("data", exist_ok=True)
            with open(f"data/{selected_pdb_id}.pdb", "w") as f:
                f.write(pdb_content)
            st.success(f"PDB structure saved to data/{selected_pdb_id}.pdb")

            # 3D Viewer
            st.markdown("### 🧬 3D Structure Viewer")
            view_style = st.selectbox("Rendering style", ["cartoon", "stick", "surface", "sphere"])
            show_pdb_structure(pdb_content, style=view_style)

        else:
            st.error("❌ Failed to fetch structure for selected PDB ID.")
    else:
        st.sidebar.warning("No matching structures found.")

# ----------------------------
# Upload Interface
# ----------------------------

st.sidebar.markdown("---")
st.sidebar.markdown("### Or Upload Your Own Structures")

if interaction_type == "Protein–Protein Interaction":
    protein_a = st.sidebar.file_uploader("Upload Pathogen Protein (PDB format)", type=["pdb"])
    protein_b = st.sidebar.file_uploader("Upload Host Protein (PDB format)", type=["pdb"])

    if protein_a and protein_b:
        st.success("Both protein structures uploaded!")
        st.write("🚧 Protein–protein docking coming soon...")

elif interaction_type == "Small Molecule–Protein Interaction":
    receptor = st.sidebar.file_uploader("Upload Host Protein (PDB format)", type=["pdb"])
    ligand = st.sidebar.file_uploader("Upload Pathogen Molecule (SDF/MOL format)", type=["sdf", "mol"])

    if receptor and ligand:
        st.success("Protein and ligand uploaded!")

        # Save files temporarily
        os.makedirs("data", exist_ok=True)
        receptor_path = "data/receptor.pdb"
        ligand_path = "data/ligand.sdf"

        with open(receptor_path, "wb") as f:
            f.write(receptor.read())
        with open(ligand_path, "wb") as f:
            f.write(ligand.read())

        # Convert to PDBQT
        st.info("Preparing files for docking...")
        receptor_pdbqt = "data/receptor.pdbqt"
        ligand_pdbqt = "data/ligand.pdbqt"
        output_pdbqt = "data/docked_output.pdbqt"

        prepare_protein(receptor_path, receptor_pdbqt)
        prepare_ligand(ligand_path, ligand_pdbqt)

        # Docking box settings (default box, can be improved)
        center = (0, 0, 0)
        size = (20, 20, 20)

                # ---- Docked Pose Viewer with Toggle Slider ----
        from utils.docking import extract_and_convert_poses
        from utils.visualization import show_pose_on_receptor

        st.markdown("### 🧬 Docked Pose Viewer")

        poses = extract_and_convert_poses(output_pdbqt)

        if poses:
            st.markdown("### 🧬 Docked Pose Viewer")

            pose_index = st.slider("Select Docking Pose", 0, len(poses) - 1, 0)
            label_text = f"Pose {pose_index + 1}"
            show_labels = st.checkbox("Show atom labels on ligand")

            # Load receptor safely
            if os.path.exists("data/receptor.pdb"):
                with open("data/receptor.pdb", "r") as f:
                    receptor_pdb_text = f.read()
            elif selected_pdb_id and pdb_content:
                receptor_pdb_text = pdb_content
            else:
                receptor_pdb_text = ""

            if receptor_pdb_text:
                show_pose_on_receptor(receptor_pdb_text, poses, pose_index, label_text, show_atom_labels=show_labels)
            else:
                st.warning("No receptor structure available.")

        if scores:
            import pandas as pd
            import matplotlib.pyplot as plt

            df = pd.DataFrame(scores, columns=["Pose", "Binding Affinity (kcal/mol)"])
            st.markdown("### 📊 Binding Affinities (Top Poses)")
            st.dataframe(df)

            fig, ax = plt.subplots()
            df.plot.bar(x="Pose", y="Binding Affinity (kcal/mol)", ax=ax, legend=False)
            ax.set_ylabel("Binding Affinity (kcal/mol)")
            ax.set_title("Docking Scores")
            st.pyplot(fig)


        with open(output_pdbqt, "r") as f:
            docked_pose = f.read()

            st.markdown("### 🧬 Docked Complex (Receptor + Ligand)")

        # Load receptor again
        with open(receptor_path, "r") as f:
            receptor_pdb_text = f.read()

        from utils.visualization import show_complex_structure
        show_complex_structure(receptor_pdb_text, docked_pose)

        # --- DOWNLOAD BUTTONS ---
        st.markdown("### 💾 Download Docking Results")

        # Docked ligand (PDBQT)
        with open(output_pdbqt, "rb") as f:
            st.download_button("Download Docked Ligand (.pdbqt)", f, file_name="docked_ligand.pdbqt")

        # Combined complex (receptor + ligand as single PDB file)
        combined_pdb = receptor_pdb_text + "\n" + docked_pose
        st.download_button("Download Docked Complex (.pdb)", combined_pdb, file_name="docked_complex.pdb")


