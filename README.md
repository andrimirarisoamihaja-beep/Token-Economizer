# Code Verifier AI - Outil de Vérification de Code & Synthèse IA

> Un outil intelligent d'analyse statique et d'intégrité de code pour **Python**, **JavaScript / TypeScript** et **Java**, couplé à une **IA (Groq)** pour la synthèse et la correction automatique des erreurs.

---

## Fonctionnalités

- **Multi-langages** :
  - **Python** : Analyse avec `Ruff` (qualité/syntaxe), `Mypy` (typage), et `Pytest` (tests unitaires).
  - **JavaScript / TypeScript** : Analyse avec `ESLint`, `tsc` (compilateur TypeScript), et scripts `npm test`.
  - **Java** : Compilation `javac` ou via **Maven** (`pom.xml`) / **Gradle** (`build.gradle`) + tests unitaires.
- **Analyse Hybride (Ultra-précise & Rapide)** :
  1. **Détection locale** via les vrais compilateurs/linters officiels (0 hallucination).
  2. **Explication IA (Groq)** uniquement en cas d'erreur pour fournir une synthèse ultra-claire avec le code de correction exact.
- **Interface Web Interactive (Streamlit)** :
  - Explorateur de fichiers interactif avec grilles de boutons cliquables.
  - Saisie manuelle de chemin ou navigation de dossier en dossier.
- **Déploiement Simplifié sur Windows** :
  - Scripts `.bat` pour l'installation automatique et le lancement en un double-clic.

---

## Architecture du Projet

```text
[ Votre Code Source (.py, .js, .ts, .java) ]
                     |
                     v
       1. ANALYSE STATIQUE LOCALE
  (Ruff, ESLint, Mypy, Javac, Maven, Pytest...)
                     |
         +-----------+-----------+
         v                       v
    [Aucune erreur]        [Erreurs détectées]
         |                       |
         v                       v
     Succès               2. SYNTHÈSE IA (Groq)
                             (Génère la solution)
                                 |
                                 v
                     Interface Web Streamlit
```

---

## Prérequis

Avant d'exécuter l'application, assurez-vous d'avoir installé :

- **Python 3.10+** → [Télécharger Python](https://www.python.org/downloads/) (Cocher "Add Python to PATH")
- **Node.js** (pour JS/TS) → [Télécharger Node.js](https://nodejs.org/)
- **JDK 17+** (pour Java) → [Télécharger Eclipse Adoptium JDK](https://adoptium.net/) (Cocher "Add to PATH")

---

## Installation & Lancement Rapide (Windows)

### Méthode 1 : Lancement en un clic (Recommandé)

1. Double-cliquez sur `installer.bat` (à exécuter une seule fois au début).
   Il crée l'environnement virtuel `.venv` et installe toutes les dépendances.
2. Double-cliquez sur `lancer.bat`.
   Au premier lancement, le script vous demandera votre clé API Groq (gratuite).
   Elle sera sauvegardée automatiquement dans le fichier `.env`.
3. Votre navigateur s'ouvrira automatiquement sur `http://localhost:8501`.

### Méthode 2 : Installation Manuelle (Terminal)

1. Cloner ou télécharger le projet :

```bash
git clone <URL_DU_DEPOT>
cd verificateur-code
```

2. Créer et activer un environnement virtuel :

```bash
python -m venv .venv
# Sur Windows :
.venv\Scripts\activate
# Sur Linux/Mac :
source .venv/bin/activate
```

3. Installer les dépendances Python :

```bash
pip install -r requirements.txt
```

4. Configurer la clé API Groq :
   Créez un fichier `.env` à la racine du projet :

```env
GROQ_API_KEY=votre_cle_api_groq_ici
```

   (Obtenez une clé gratuite sur [console.groq.com](https://console.groq.com))

5. Lancer l'interface Streamlit :

```bash
python -m streamlit run app.py
```

---

## Obtenir une clé API Groq (Gratuite)

1. Rendez-vous sur [Groq Console](https://console.groq.com).
2. Créez un compte gratuit.
3. Allez dans **API Keys** → **Create API Key**.
4. Copiez la clé et collez-la dans le fichier `.env` ou lors de l'invitation dans `lancer.bat`.

---

## Structure des Fichiers

```text
.
├── app.py                   # Interface Web Streamlit (GUI)
├── verifier_ia.py           # Moteur d'analyse (Python, JS/TS, Java + IA)
├── installer.bat            # Script d'installation automatique Windows
├── lancer.bat                # Script de lancement 1-Click
├── requirements.txt         # Dépendances Python (streamlit, groq, ruff, mypy...)
├── .env                      # Clé API Groq (non versionné)
└── .gitignore                # Fichiers exclus de Git
```

---

## Outils utilisés sous le capot

| Langage          | Qualité & Style | Typage  | Tests Unitaires   |
|-------------------|------------------|---------|--------------------|
| Python            | Ruff             | Mypy    | Pytest             |
| JavaScript / TS   | ESLint           | tsc     | npm test           |
| Java              | javac / Maven    | javac   | mvn test / gradle test |

---

## Licence

Projet distribué sous licence MIT. Libre d'utilisation et de modification.