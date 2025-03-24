# utils/docking.py

import subprocess
from openbabel import pybel

def prepare_ligand(input_path, output_path):
    mol = next(pybel.readfile("sdf", input_path))
    mol.addh()
    mol.make3D()
    mol.write("pdbqt", output_path, overwrite=True)

def prepare_protein(input_path, output_path):
    mol = next(pybel.readfile("pdb", input_path))
    mol.addh()
    mol.write("pdbqt", output_path, overwrite=True)

def run_vina(protein_pdbqt, ligand_pdbqt, out_pdbqt, center, size, vina_path="vina"):
    x, y, z = center
    sx, sy, sz = size

    command = [
        vina_path,
        "--receptor", protein_pdbqt,
        "--ligand", ligand_pdbqt,
        "--out", out_pdbqt,
        "--center_x", str(x),
        "--center_y", str(y),
        "--center_z", str(z),
        "--size_x", str(sx),
        "--size_y", str(sy),
        "--size_z", str(sz),
        "--exhaustiveness", "8",
        "--num_modes", "9"
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout

    # Extract binding scores from Vina output
    scores = []
    for line in output.splitlines():
        if line.strip().startswith(("1", "2", "3")):
            try:
                pose_index = int(line.split()[0])
                score = float(line.split()[1])
                scores.append((pose_index, score))
            except:
                continue

    return output, scores
import tempfile
from openbabel import pybel
import io

def extract_and_convert_poses(pdbqt_path):
    """
    Extract ligand poses from a PDBQT file and convert each to PDB format using Open Babel.
    Returns a list of pose strings (in PDB format).
    """
    poses = []
    try:
        with open(pdbqt_path, "r") as file:
            content = file.read()

        split_poses = content.split("MODEL")
        if len(split_poses) <= 1:
            print("[DEBUG] No poses found.")
            return []

        for i, block in enumerate(split_poses[1:]):
            lines = block.splitlines()
            pose_lines = [line for line in lines if not line.startswith("ENDMDL")]
            pose_pdbqt = "MODEL\n" + "\n".join(pose_lines) + "\nENDMDL\n"

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdbqt") as tmp_in:
                tmp_in.write(pose_pdbqt.encode())
                in_path = tmp_in.name

            mol = next(pybel.readfile("pdbqt", in_path))
            output = io.StringIO()
            mol.write("pdb", output)
            pose_pdb = output.getvalue()
            poses.append(pose_pdb)
    except Exception as e:
        print(f"[ERROR] Failed to extract poses: {e}")
        return []

    return poses
