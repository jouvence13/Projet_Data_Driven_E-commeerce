# Structure du Projet - Architecture Professionnelle

## Overview
Le projet est maintenant structuré de manière modulaire et professionnelle.

## 📁 Structure

```
Projet_Data_Driven_E-commeerce/
├── code/
│   ├── app.py                  # Application Streamlit (MAIN)
│   ├── config.py               # Configuration centralisée
│   ├── data_loader.py          # Chargement & prétraitement données
│   ├── utils.py                # Fonctions utilitaires & helpers
│   ├── kpis.py                 # Calcul des KPIs
│   ├── cohorts.py              # Analyse de cohortes
│   └── ab_test.py              # Tests A/B et statistiques
├── Notebook/
│   ├── EDA_Professional.ipynb  # Exploration professionnelle (NEW!)
│   └── data_traitement.ipynb   # Ancien notebook
├── data/
│   ├── raw/                    # Données brutes (gitignore)
│   │   ├── events.csv
│   │   ├── category_tree.csv
│   │   └── item_properties_part*.csv
│   ├── clean/                  # Données nettoyées
│   │   └── events_clean.csv
│   └── processed/              # Données traitées (export)
├── tests/                      # Tests unitaires (TODO)
├── docs/                       # Documentation
├── config/                     # Fichiers de configuration
├── requirements.txt            # Dépendances production
├── requirements-dev.txt        # Dépendances développement (NEW!)
├── README.md                   # Documentation projet
├── .gitignore                  # Fichiers à ignorer Git
└── .env.example                # Template variables d'environnement
```

## 🔧 Modules

### `config.py`
- Centralise toutes les configurations
- Chemins des fichiers
- Paramètres Streamlit
- Constantes (funnel events, A/B test, etc.)

### `data_loader.py`
- Charge les données avec cache
- Prétraitement des colonnes
- Validation des données

### `utils.py`
- Formatage des nombres et pourcentages
- Fonctions de sécurité (division sûre)
- Validation de DataFrames

### `kpis.py`
- Calcul des KPIs journaliers
- KPIs globaux
- Rendering des cartes KPI

### `cohorts.py`
- Analyse de cohortes par semaine/mois
- Calcul de la rétention
- Insights sur les cohortes

### `ab_test.py`
- Z-test pour proportions
- Simulation A/B test
- Résultats statistiques

## 📊 Nouveau Notebook: EDA_Professional.ipynb

Refait de zéro avec:
- Audit complet des données
- Feature engineering organisé
- Visualisations modernes
- Export structuré
- Recommandations actionnables

## ✅ Améliorations

- ✓ **Code modulaire** : Séparation des responsabilités
- ✓ **Type hints** : Meilleure documentation du code
- ✓ **Docstrings** : Documentation de chaque fonction
- ✓ **Configuration centralisée** : Pas de hardcoding
- ✓ **Notebook professionnel** : EDA complète et structurée
- ✓ **Requirements séparés** : Dev vs Production
- ✓ **Error handling** : Gestion d'erreurs robuste
- ✓ **Caching optimisé** : Streamlit @cache_data

## 🚀 Prochaines étapes

1. [ ] Ajouter des tests unitaires (`tests/`)
2. [ ] CI/CD avec GitHub Actions
3. [ ] Linting avec Black/Flake8
4. [ ] API REST optionnelle
5. [ ] Dockerfile pour déploiement
6. [ ] Authentification Streamlit
7. [ ] Export de rapports (PDF)
8. [ ] Alertes automatiques

## 📋 Utilisation

### Lancer le dashboard
```bash
cd code
streamlit run app.py
```

### Exécuter le notebook
```bash
jupyter notebook Notebook/EDA_Professional.ipynb
```

### Installer dépendances dev
```bash
pip install -r requirements-dev.txt
```

## 🧪 Testing (à implémenter)

```bash
pytest tests/ --cov=code
black code/ --check
flake8 code/
```

## 📚 Références

- Streamlit Docs: https://docs.streamlit.io/
- Pandas: https://pandas.pydata.org/
- Plotly: https://plotly.com/python/
- Z-test: https://en.wikipedia.org/wiki/Z-test
