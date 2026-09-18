import os
import subprocess
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Vérificateur de Code",
    layout="wide",
)

st.title("Outil de Vérification de Code & IA")

# -------------------- État de navigation --------------------
if "current_path" not in st.session_state:
    st.session_state.current_path = os.getcwd()

if "selected_target" not in st.session_state:
    st.session_state.selected_target = st.session_state.current_path

# -------------------- Barre latérale --------------------
st.sidebar.header("Configuration")
api_key = os.getenv("GROQ_API_KEY", "")
if api_key:
    st.sidebar.success("Clé API Groq active")
else:
    st.sidebar.error("Clé API Groq manquante dans .env")
    new_key = st.sidebar.text_input("Entrez votre clé Groq :", type="password")
    if st.sidebar.button("Enregistrer la clé") and new_key.strip():
        with open(".env", "w", encoding="utf-8") as f:
            f.write(f"GROQ_API_KEY={new_key.strip()}\n")
        st.sidebar.success("Clé enregistrée ! Rechargez la page.")
        st.rerun()

# -------------------- Helpers --------------------
DOSSIERS_EXCLUS = {
    "__pycache__",
    "node_modules",
    ".venv",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".streamlit",
}

EXTENSIONS_OK = (".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs")


def lister_contenu(chemin: str):
    try:
        elements = os.listdir(chemin)
    except PermissionError:
        return [], []
    except FileNotFoundError:
        return [], []

    dossiers = []
    fichiers = []

    for nom in sorted(elements, key=str.lower):
        chemin_complet = os.path.join(chemin, nom)
        if os.path.isdir(chemin_complet):
            if nom not in DOSSIERS_EXCLUS and not nom.startswith("."):
                dossiers.append(nom)
        elif os.path.isfile(chemin_complet):
            if nom.endswith(EXTENSIONS_OK) and nom not in ("app.py", "verifier_ia.py"):
                fichiers.append(nom)

    return dossiers, fichiers


# -------------------- Interface principale --------------------
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Sélection du fichier ou dossier à analyser")

    mode = st.radio(
        "Méthode de sélection :",
        ["Explorateur de dossiers", "Saisie manuelle"],
        horizontal=True,
    )

    if mode == "Explorateur de dossiers":
        st.markdown("**Emplacement actuel :**")
        st.code(st.session_state.current_path)

        # Navigation rapide
        nav1, nav2, nav3 = st.columns(3)
        with nav1:
            if st.button("Dossier parent", use_container_width=True):
                parent = os.path.dirname(st.session_state.current_path)
                if parent and os.path.exists(parent):
                    st.session_state.current_path = parent
                    st.session_state.selected_target = parent
                    st.rerun()
        with nav2:
            if st.button("Racine du projet", use_container_width=True):
                st.session_state.current_path = os.getcwd()
                st.session_state.selected_target = os.getcwd()
                st.rerun()
        with nav3:
            if st.button("Analyser ce dossier", use_container_width=True):
                st.session_state.selected_target = st.session_state.current_path
                st.rerun()

        st.divider()

        dossiers, fichiers = lister_contenu(st.session_state.current_path)

        # ---------- Dossiers en boutons cliquables ----------
        st.markdown("### Dossiers")
        if dossiers:
            # Affichage en grille de boutons (4 par ligne)
            cols_per_row = 4
            for i in range(0, len(dossiers), cols_per_row):
                row = st.columns(cols_per_row)
                for j, col in enumerate(row):
                    if i + j < len(dossiers):
                        nom_dossier = dossiers[i + j]
                        with col:
                            if st.button(
                                nom_dossier,
                                key=f"dir_{st.session_state.current_path}_{nom_dossier}",
                                use_container_width=True,
                            ):
                                nouveau_chemin = os.path.join(
                                    st.session_state.current_path, nom_dossier
                                )
                                st.session_state.current_path = nouveau_chemin
                                st.session_state.selected_target = nouveau_chemin
                                st.rerun()
        else:
            st.caption("Aucun sous-dossier ici.")

        st.divider()

        # ---------- Fichiers en boutons cliquables ----------
        st.markdown("### Fichiers analysables")
        if fichiers:
            cols_per_row = 3
            for i in range(0, len(fichiers), cols_per_row):
                row = st.columns(cols_per_row)
                for j, col in enumerate(row):
                    if i + j < len(fichiers):
                        nom_fichier = fichiers[i + j]
                        chemin_fichier = os.path.join(
                            st.session_state.current_path, nom_fichier
                        )
                        # Mise en avant si sélectionné
                        est_selectionne = (
                            st.session_state.selected_target == chemin_fichier
                        )
                        label = (
                            f"[Sélectionné] {nom_fichier}"
                            if est_selectionne
                            else nom_fichier
                        )
                        with col:
                            if st.button(
                                label,
                                key=f"file_{chemin_fichier}",
                                use_container_width=True,
                                type="primary" if est_selectionne else "secondary",
                            ):
                                st.session_state.selected_target = chemin_fichier
                                st.rerun()
        else:
            st.caption(
                "Aucun fichier .py / .js / .ts dans ce dossier. "
                "Vous pouvez analyser le dossier entier via le bouton 'Analyser ce dossier'."
            )

        fichier_cible = st.session_state.selected_target

    else:
        # Saisie manuelle
        saisie = st.text_input(
            "Chemin complet du fichier ou dossier :",
            value=st.session_state.selected_target,
        ).strip()
        if saisie:
            st.session_state.selected_target = saisie
        fichier_cible = st.session_state.selected_target

with col2:
    st.markdown("### Cible")
    st.info(f"`{fichier_cible}`")

    existe = os.path.exists(fichier_cible) if fichier_cible else False
    if fichier_cible and not existe:
        st.error("Ce chemin n'existe pas.")
    elif fichier_cible and os.path.isdir(fichier_cible):
        st.caption("Type : **Dossier** (analyse récursive des fichiers supportés)")
    elif fichier_cible:
        st.caption("Type : **Fichier**")

    st.write("")
    lancer = st.button(
        "Lancer l'analyse",
        type="primary",
        use_container_width=True,
        disabled=not (fichier_cible and existe),
    )

# -------------------- Exécution --------------------
if lancer and fichier_cible and os.path.exists(fichier_cible):
    with st.spinner("Analyse du code et consultation de l'IA..."):
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        resultat = subprocess.run(
            ["python", "verifier_ia.py", fichier_cible],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )

        stdout = resultat.stdout or ""
        stderr = resultat.stderr or ""

        st.subheader("Résultats")

        if resultat.returncode == 0:
            st.success(
                f"Succès ! La cible `{fichier_cible}` est propre et sans erreur."
            )
            if stdout.strip():
                st.code(stdout)
        else:
            st.error("Des erreurs ont été détectées !")

            if "--- SYNTHESE IA ---" in stdout:
                partie_outils, partie_ia = stdout.split("--- SYNTHESE IA ---", 1)

                st.markdown("### Synthèse de l'IA")
                st.markdown(partie_ia)

                with st.expander(
                    "Voir les détails techniques (Ruff, ESLint, Mypy...)"
                ):
                    st.code(partie_outils)
            else:
                if stdout.strip():
                    st.code(stdout)
                if stderr.strip():
                    st.code(stderr)