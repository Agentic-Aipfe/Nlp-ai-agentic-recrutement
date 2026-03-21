# NLP Agentic – Agent 1 CV Parser

Cette partie correspond actuellement à la **première partie** d'un système multi-agents pour le recrutement, plus précisément :

## Agent 1 – Analyse et structuration des CV

À ce stade, seule la **première étape** est implémentée :

- **Extraction du texte depuis des CV PDF**
- **Validation du type de document via un modèle local (llama3)**
- Comparaison de plusieurs extracteurs (`pdfplumber`, `PyMuPDF`, `LlamaParse`)
- Choix de `pdfplumber` comme extracteur principal

---

# 1. Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Python 3.10+** recommandé
- **pip** et **git**
- **Ollama** (Requis pour la validation du document via llama3)
  - *Linux* : `curl -fsSL https://ollama.com/install.sh | sh`
  - *Windows / macOS* : Téléchargez l'installateur depuis https://ollama.com/download
  - Après installation : `ollama pull llama3`
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

Pour cette partie, **aucun fichier `.env` n'est nécessaire** — tout fonctionne localement via Ollama, sans clé API.

Le fichier `.env` deviendra utile uniquement si vous intégrez un service externe comme **Groq** ou **LlamaParse** dans les étapes suivantes.

```env
# Optionnel pour l'instant
LLAMAPARSE_API_KEY=your_api_key_here
GROQ_API_KEY=your_api_key_here
```

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
│   │   └── extractor.py        ← extraction + validation
│   ├── .env
│   ├── .gitignore
│   └── test.py
├── venv/
├── README.md
└── requirements.txt
```

---

# 7. Tester l'extracteur

Pour tester, placez votre fichier PDF dans le dossier `resumes/` puis lancez depuis le terminal :

```bash
cd agent_1_cv_parser/tools
python extractor.py "../resumes/votre_cv.pdf"
```

Résultat attendu pour un CV valide :

```
Extraction en cours...
Fichier    : votre_cv.pdf
Pages      : 2
Caractères : 3400
Pages image: []
OCR requis : False
============================================================
Validation en cours...
Est un CV  : True
Type doc   : CV
Raison     : Le document contient des sections typiques d'un CV
============================================================
✅ Texte sauvegardé dans : votre_cv_raw.txt
```

Résultat attendu pour un document rejeté :

```
❌ Document rejeté — ce n'est pas un CV (Rapport)
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
- valider le type du document via `llama3` (CV, Facture, Rapport, etc.)
- rejeter automatiquement tout document qui n'est pas un CV
- concaténer et retourner le contenu structuré

---

## Utilisation via un script Python

```python
from agent_1_cv_parser.tools.extractor import extract_text, validate_document

# étape 1 — extraction
result = extract_text("chemin/vers/votre_cv.pdf")

print(f"Fichier    : {result['file_name']}")
print(f"Pages      : {result['num_pages']}")
print(f"Pages image: {result['image_pages']}")
print(f"OCR requis : {result['needs_ocr']}")

# étape 2 — validation
validation = validate_document(result)

print(f"Est un CV  : {validation['is_cv']}")
print(f"Type doc   : {validation['document_type']}")
print(f"Raison     : {validation['reason']}")

# utiliser le texte uniquement si c'est un CV
if validation["is_cv"]:
    print(result["text"][:100] + "...")
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
3. **Validation par LLM**
   - Le texte extrait est envoyé à `llama3` (via Ollama) pour vérifier que le document est bien un CV avant de continuer le pipeline.

---

# 10. Ma contribution – Extraction et Validation des CV PDF

Dans l'Agent 1, ma partie concerne principalement l'**extraction du texte à partir des CV PDF** ainsi que la **validation automatique du type de document**. L'objectif est de transformer un document brut en texte exploitable et vérifié pour les étapes suivantes du pipeline.

## Fonctionnement

Le processus suit trois étapes principales :

**1. Extraction native avec `pdfplumber`**

On commence par extraire le texte natif du PDF page par page via `pdfplumber`, qui offre les meilleurs résultats sur les CV complexes (multi-colonnes, mise en forme avancée).

**2. Détection des documents scannés et fallback OCR**

On évalue la qualité de l'extraction avec une règle simple : si un nombre significatif de pages contient très peu de texte natif, le document est probablement scanné. Dans ce cas, on active automatiquement un fallback avec `pdf2image` et `pytesseract` pour récupérer le texte via OCR.

**3. Validation du type de document via llama3**

Les premiers 1500 caractères du texte extrait sont envoyés au modèle local `llama3` (via Ollama) avec un prompt structuré. Le modèle retourne un JSON indiquant si le document est bien un CV, son type, et une explication courte. Tout document qui n'est pas un CV est rejeté avant d'entrer dans le pipeline.

## Données retournées

### Par `extract_text()`

| Champ | Description |
|---|---|
| `text` | Texte complet extrait |
| `num_pages` | Nombre total de pages |
| `file_name` | Nom du fichier PDF |
| `image_pages` | Liste des pages identifiées comme images |
| `needs_ocr` | Indique si le fallback OCR a été activé |

### Par `validate_document()`

| Champ | Description |
|---|---|
| `is_cv` | `true` si le document est un CV, `false` sinon |
| `document_type` | Type détecté : CV / Facture / Rapport / Médical / Juridique / Autre |
| `reason` | Explication courte de la décision du modèle |

## Pourquoi c'est important

Cette étape est critique : **toute la qualité du reste du pipeline dépend directement de la qualité du texte extrait et de la fiabilité de la validation**. Un texte mal extrait ou un document mal classifié impacte négativement toutes les étapes suivantes : nettoyage, extraction d'entités, génération d'embeddings et matching.

---

# 11. État actuel du projet

## Déjà fait

- Structure initiale du projet
- Tests comparatifs entre extracteurs
- Implémentation de l'extraction hybride avec `pdfplumber`
- Bascule dynamique vers l'OCR pour le traitement des CV scannés
- Validation automatique du type de document via `llama3` (Ollama, 100% local)
- Rejet automatique des documents qui ne sont pas des CV

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

## Ollama

```bash
# vérifier que ollama tourne
ollama list

# lancer ollama si pas encore démarré
ollama serve

# pull llama3 si pas encore téléchargé
ollama pull llama3
```

---

# 13. Problèmes fréquents

## 1. `ModuleNotFoundError`

Vérifiez que :
- l'environnement virtuel est activé
- les dépendances sont bien installées avec `pip install -r requirements.txt`

## 2. PDF mal extrait

Tous les PDF ne sont pas égaux :
- certains sont de vrais PDF texte
- d'autres sont des scans / images
- certains ont des colonnes ou des éléments décoratifs

Pour ce projet, `pdfplumber` est actuellement l'outil le plus fiable parmi ceux testés.

## 3. Ollama ne répond pas

Vérifiez que le service tourne :

```bash
ollama serve
```

Si vous obtenez `bind: Only one usage of each socket address` — c'est que Ollama tourne déjà en arrière-plan, pas besoin de le relancer.

---

# 14. Auteurs

Projet réalisé dans le cadre d'un PFE sur le recrutement intelligent basé sur NLP / IA agentique.

---

# 15. Remarque

Ce dépôt est en cours de développement.
Pour l'instant, il représente les **deux premières briques fonctionnelles** :
L'extraction robuste du texte des CV PDF et la validation automatique du type de document.
# 15. Remarque

Ce dépôt est en cours de développement.
Pour l'instant, il représente les **deux premières briques fonctionnelles** :
L'extraction robuste du texte des CV PDF et la validation automatique du type de document.
