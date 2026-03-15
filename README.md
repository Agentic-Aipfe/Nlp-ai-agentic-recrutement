# Agent 1 – Analyse et Structuration des CV

Cet agent est le **premier maillon** du système multi-agents de recrutement.
Il est responsable de la transformation d’un CV brut (PDF) en une représentation
structurée et exploitable par les agents suivants.

---

## 🎯 Objectif

Transformer un CV PDF hétérogène (formats, layouts, colonnes, designs)
en une **représentation textuelle et vectorielle fiable**.

Agent 1 garantit que :
- le texte est correctement extrait
- les mots ne sont pas dégradés
- la structure globale du CV est préservée
- les données sont prêtes pour le matching sémantique

---

## 🧠 Pattern agentique utilisé

**Pattern : Pipeline Séquentiel (non ReAct)**

Agent 1 n’est **pas un agent décisionnel**.
C’est un pipeline déterministe avec des étapes clairement définies.
