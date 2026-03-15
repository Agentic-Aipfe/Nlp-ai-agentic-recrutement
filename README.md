# NLP Agentic – Agent 1 CV Parser

Ce projet correspond actuellement à la **première partie** d’un système multi-agents pour le recrutement, plus précisément :

## Agent 1 – Analyse et structuration des CV
À ce stade, seule la **première étape** est implémentée :

- **Extraction du texte depuis des CV PDF**
- comparaison de plusieurs extracteurs (`pdfplumber`, `PyMuPDF`, `LlamaParse`)
- choix de `pdfplumber` comme extracteur principal

---

# 1. Prérequis

Avant de commencer, assurez-vous d’avoir installé :

- **Python 3.10+** recommandé
- **pip**
- **git**
- (optionnel) **VS Code**

Vérifier les versions :

```bash
python --version
pip --version
git --version
```

---

# 2. Cloner le projet

```bash
git clone <URL_DU_REPO>
cd NLP_AGENTIC
```

Remplacez `<URL_DU_REPO>` par le lien réel du dépôt GitHub.

---

# 3. Créer un environnement virtuel

## Sous Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## Sous Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

Une fois activé, vous devriez voir `(venv)` dans le terminal.

---

# 4. Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

# 5. Configuration du fichier `.env`

Créer un fichier `.env` dans le dossier :

```text
agent_1_cv_parser/
```

### Exemple minimal

```env
# Optionnel pour l’instant
LLAMAPARSE_API_KEY=your_api_key_here
```

> Remarque :
> - Pour les tests avec `pdfplumber` et `PyMuPDF`, ce fichier n’est généralement **pas nécessaire**
> - Il devient utile uniquement si vous utilisez un service externe comme **LlamaParse**

---

# 6. Structure actuelle du projet

```text
NLP_AGENTIC/
├── agent_1_cv_parser/
│   ├── models/
│   │   └── schemas.py
│   ├── tests/
│   │   ├── test_llamaparse.py
│   │   ├── test_pymupdf.py
│   │   └── test_pdfplumber.py
│   ├── tools/
│   │   └── extractor.py
│   ├── .env
│   └── test.py
├── venv/
├── README.md
└── requirements.txt
```

---

# 7. Lancer les tests

Les tests servent à comparer les extracteurs PDF sur différents CV.

Depuis la racine du projet :

```bash
pytest agent_1_cv_parser/tests/
```

Si `pytest` n’est pas reconnu :

```bash
python -m pytest agent_1_cv_parser/tests/
```

---

# 8. Utiliser l’extracteur

Le fichier principal actuel est :

```text
agent_1_cv_parser/tools/extractor.py
```

Son rôle est de :
- charger un fichier PDF
- extraire le texte page par page
- concaténer le contenu
- signaler éventuellement les pages très pauvres en texte

---

## Exemple d’utilisation simple

Selon l’implémentation de `extractor.py`, vous pouvez tester avec un script Python.

### Exemple

```python
from agent_1_cv_parser.tools.extractor import extract_text_from_pdf

pdf_path = "chemin/vers/votre_cv.pdf"
result = extract_text_from_pdf(pdf_path)

print("Nombre de pages :", result["num_pages"])
print("Pages image :", result["image_pages"])
print("Texte extrait :")
print(result["text"])
```

### Exécution

```bash
python agent_1_cv_parser/test.py
```

> Si le nom de la fonction dans `extractor.py` est différent, adaptez simplement :
> - `extract_text_from_pdf`
> - ou le nom réel utilisé dans votre code

---

# 9. Extracteur retenu

Après plusieurs tests sur différents CV :

- CV simples → résultats proches entre `pdfplumber` et `PyMuPDF`
- CV complexes / multi-colonnes → `pdfplumber` donne de meilleurs résultats
- certains cas avec `PyMuPDF` :
  - mélange des sections
  - mots éclatés lettre par lettre
  - ordre de lecture peu fiable

### Décision actuelle
Le projet retient :

```text
pdfplumber
```

comme extracteur principal pour l’Agent 1.

---

# 10. État actuel du projet

## Déjà fait
- structure initiale du projet
- tests comparatifs entre extracteurs
- implémentation de l’extraction de texte

## À venir
- nettoyage et prétraitement du texte
- extraction d’entités (formations, expériences, compétences, etc.)
- génération d’embeddings
- matching avec les offres d’emploi
- génération de tests techniques

---

# 11. Commandes utiles

## Activer l’environnement virtuel

### Windows
```bash
venv\Scripts\activate
```

### Linux / macOS
```bash
source venv/bin/activate
```

## Désactiver l’environnement

```bash
deactivate
```

## Réinstaller les dépendances proprement

```bash
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

---

# 12. Problèmes fréquents

## 1. `ModuleNotFoundError`
Vérifiez que :
- l’environnement virtuel est activé
- les dépendances sont bien installées avec `pip install -r requirements.txt`

---

## 2. `pytest` non reconnu
Utilisez :

```bash
python -m pytest agent_1_cv_parser/tests/
```

---

## 3. Erreur liée à `.env`
Si vous testez uniquement `pdfplumber` / `PyMuPDF`, ignorez temporairement `LlamaParse`.

---

## 4. PDF mal extrait
Tous les PDF ne sont pas égaux :
- certains sont de vrais PDF texte
- d’autres sont des scans / images
- certains ont des colonnes ou des éléments décoratifs

Pour ce projet, `pdfplumber` est actuellement l’outil le plus fiable parmi ceux testés.

---

# 13. Auteurs

Projet réalisé dans le cadre d’un PFE sur le recrutement intelligent basé sur NLP / IA agentique.

---

# 14. Remarque

Ce dépôt est en cours de développement.
Pour l’instant, il représente surtout la **première brique fonctionnelle** :
l’extraction robuste du texte des CV PDF.