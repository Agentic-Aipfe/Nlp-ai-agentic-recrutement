# NLP Agentic – Agent 1 CV Parser

Cette partie correspond actuellement à la **première partie** d'un système multi-agents pour le recrutement, plus précisément :

## Agent 1 – Analyse et structuration des CV

À ce stade, seule la **première étape** est implémentée :

- **Extraction du texte depuis des CV PDF**
- Comparaison de plusieurs extracteurs (`pdfplumber`, `PyMuPDF`, `LlamaParse`)
- Choix de `pdfplumber` comme extracteur principal

---

# 1. Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Python 3.10+** recommandé
- **pip** et **git**
- **Tesseract-OCR** (Requis pour l'OCR des CV scannés via `pytesseract`)
  - *Windows* : Téléchargez l'installateur depuis le dépôt GitHub et ajoutez-le au PATH.
  - *Linux* : `sudo apt install tesseract-ocr tesseract-ocr-fra`
  - *macOS* : `brew install tesseract tesseract-lang`
- **Poppler** (Requis pour convertir les PDF en images via `pdf2image`)
  - *Windows* : Téléchargez les binaires Poppler, extrayez-les et ajoutez le dossier `bin` au PATH.
  - *Linux* : `sudo apt install poppler-utils`
  - *macOS* : `brew install poppler`

Vérifier les versions (Python et Git) :

```bash
python --version
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
# Optionnel pour l'instant
LLAMAPARSE_API_KEY=your_api_key_here
```

> Remarque :
> - Pour les tests avec `pdfplumber` et `PyMuPDF`, ce fichier n'est généralement **pas nécessaire**
> - Il devient utile uniquement si vous utilisez un service externe comme **LlamaParse**

---

# 6. Structure actuelle du projet

```text
NLP_AGENTIC/
├── agent_1_cv_parser/
│   ├── models/
│   │   └── schemas.py
│   ├── resumes/
│   │   └── badr.pdf
│   ├── tests/
│   │   ├── test_llamaparse.py
│   │   ├── test_mypupdf.py
│   │   └── test_pdfplumber.py
│   ├── tools/
│   │   └── extractor.py
│   ├── .env
│   ├── .gitignore
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

Si `pytest` n'est pas reconnu :

```bash
python -m pytest agent_1_cv_parser/tests/
```

---

# 8. Utiliser l'extracteur

Le fichier principal actuel est :

```text
agent_1_cv_parser/tools/extractor.py
```

Son rôle est de :
- charger un fichier PDF
- extraire le texte natif page par page via `pdfplumber`
- identifier si le PDF contient principalement des images (CV scannés)
- relancer une extraction complète avec OCR (`pytesseract`) en cas de fichier scanné
- concaténer et retourner le contenu structuré

---

## Exemple d'utilisation simple

Le script fonctionne comme un module ou peut être exécuté directement en invite de commande :

### Exécution directe en terminal

Si vous ne passez pas d'argument, le script vous demandera le chemin :

```bash
python agent_1_cv_parser/tools/extractor.py "chemin/vers/votre_cv.pdf"
```

Il affichera les informations et **sauvegardera le texte extrait dans un fichier `*_raw.txt`**.

### Via un script Python

```python
from agent_1_cv_parser.tools.extractor import extract_text_from_pdf

pdf_path = "chemin/vers/votre_cv.pdf"
result = extract_text_from_pdf(pdf_path)

print(f"Fichier    : {result['file_name']}")
print(f"Pages      : {result['num_pages']}")
print(f"Pages image: {result['image_pages']}")
print(f"Scanné     : {result['is_scannable']}")
print(f"OCR requis : {result['needs_ocr']}")
print("Texte extrait :")
print(result["text"][:100] + "...")  # Afficher un extrait
```

---

# 9. Extracteur retenu

Après plusieurs tests sur différents CV :

- CV simples → résultats proches entre `pdfplumber` et `PyMuPDF`
- CV complexes / multi-colonnes → `pdfplumber` donne de meilleurs résultats
- Certains cas avec `PyMuPDF` :
  - mélange des sections
  - mots éclatés lettre par lettre
  - ordre de lecture peu fiable

### Décision actuelle

Le système hybride suivant a été mis en place :

1. **Extraction native**
   - Utilisation de `pdfplumber` en première intention pour une extraction précise.
2. **Fallback sur OCR**
   - Si la majorité des pages ont très peu de texte natif (probablement un scan), le script bascule sur `pdf2image` et `pytesseract` pour récupérer le contenu textuel.

---

# 10. Ma contribution – Extraction de texte des CV PDF

Dans l'Agent 1, ma partie concerne principalement l'**extraction du texte à partir des CV PDF**. L'objectif est de transformer un document brut en texte exploitable pour les étapes suivantes du pipeline.

## Fonctionnement

Le processus d'extraction suit trois étapes principales :

**1. Extraction native avec `pdfplumber`**

On commence par extraire le texte natif du PDF page par page via `pdfplumber`, qui offre les meilleurs résultats sur les CV complexes (multi-colonnes, mise en forme avancée).

**2. Détection des documents scannés**

On évalue la qualité de l'extraction avec une règle simple : si un nombre significatif de pages contient très peu de texte natif, le document est probablement scanné ou peu extractible en mode natif.

**3. Fallback OCR**

Dans ce cas, on active automatiquement un fallback avec `pdf2image` et `pytesseract` : le PDF est converti en images page par page, puis l'OCR permet de récupérer le texte à partir de ces images.

## Données retournées

En plus du texte extrait, la fonction retourne plusieurs métadonnées utiles pour les étapes suivantes :

| Champ | Description |
|---|---|
| `text` | Texte complet extrait |
| `num_pages` | Nombre total de pages |
| `image_pages` | Liste des pages identifiées comme images |
| `is_scannable` | Indique si le document semble scanné |
| `needs_ocr` | Indique si le fallback OCR a été activé |

## Pourquoi c'est important

Cette étape est critique : **toute la qualité du reste du pipeline dépend directement de la qualité du texte extrait**. Un texte mal extrait — mots découpés, sections mélangées, contenu manquant — impacte négativement toutes les étapes suivantes : nettoyage, extraction d'entités, génération d'embeddings et matching.

---

# 11. État actuel du projet

## Déjà fait

- Structure initiale du projet
- Tests comparatifs entre extracteurs
- Implémentation de l'extraction hybride avec `pdfplumber`
- Bascule dynamique vers l'OCR pour le traitement des CV scannés

## À venir

- Nettoyage et prétraitement du texte
- Extraction d'entités (formations, expériences, compétences, etc.)
- Génération d'embeddings
- Matching avec les offres d'emploi
- Génération de tests techniques

---

# 12. Commandes utiles

## Activer l'environnement virtuel

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

## Désactiver l'environnement

```bash
deactivate
```

## Réinstaller les dépendances proprement

```bash
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

---

# 13. Problèmes fréquents

## 1. `ModuleNotFoundError`

Vérifiez que :
- l'environnement virtuel est activé
- les dépendances sont bien installées avec `pip install -r requirements.txt`

## 2. `pytest` non reconnu

Utilisez :

```bash
python -m pytest agent_1_cv_parser/tests/
```

## 3. Erreur liée à `.env`

Si vous testez uniquement `pdfplumber` / `PyMuPDF`, ignorez temporairement `LlamaParse`.

## 4. PDF mal extrait

Tous les PDF ne sont pas égaux :
- certains sont de vrais PDF texte
- d'autres sont des scans / images
- certains ont des colonnes ou des éléments décoratifs

Pour ce projet, `pdfplumber` est actuellement l'outil le plus fiable parmi ceux testés.

---

# 14. Auteurs

Projet réalisé dans le cadre d'un PFE sur le recrutement intelligent basé sur NLP / IA agentique.

---

# 15. Remarque

Ce dépôt est en cours de développement.
Pour l'instant, il représente surtout la **première brique fonctionnelle** :
L'extraction robuste du texte des CV PDF.
