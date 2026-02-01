# Dashboard Data‑Driven – Analyse E‑commerce

Dashboard interactif en Python (Streamlit) pour analyser le comportement utilisateur sur une plateforme e‑commerce.

---

## Objectif

Explorer des millions d’événements e‑commerce et produire :
- des KPIs (conversion, activité, engagement) ;
- des analyses de cohortes et de rétention ;
- des tendances temporelles ;
- des visualisations interactives.

---

## Prérequis

- Python 3.9+ (recommandé 3.10)
- Git

---

## Démarrage rapide

### 1) Cloner le dépôt

```bash
git clone https://github.com/jouvence13/Projet_Data_Driven_E-commeerce.git
cd Projet_Data_Driven_E-commeerce
```

### 2) Créer et activer un environnement virtuel

**Windows (PowerShell)**
```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python -m venv venv
source venv/bin/activate
```

### 3) Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4) Lancer l’application Streamlit

```bash
streamlit run code/app.py
```

L’app s’ouvre sur http://localhost:8501

---

## Données

Le dashboard utilise un fichier nettoyé :

- Chemin attendu : `data/clean/events_clean.csv`
- Taille ~ 192 MB

> Si vous clonez le projet sans les données, placez le fichier CSV nettoyé à cet emplacement.

---

## Structure du projet (résumé)

```
Projet_Data_Driven_E-commeerce/
├── code/                       # Application Streamlit
│   ├── app.py
│   ├── kpis.py
│   ├── cohorts.py
│   ├── insights.py
│   └── utils.py
├── data/
│   ├── row/                     # Données brutes (source)
│   └── clean/                   # Données nettoyées
├── Notebook/                    # EDA et exploration
├── data_collection/             # Scripts MongoDB (optionnel)
├── data_viz/                    # Scripts de visualisation
├── docs/                        # Documentation
├── requirements.txt
└── README.md
```

---

## Fonctionnalités

- **KPIs** : conversion, événements par utilisateur, activité globale
- **Cohortes** : matrice de rétention, heatmap
- **Analyse temporelle** : tendances jour/heure, distributions
- **A/B tests** : comparaison de variantes (optionnel)

---

## Configuration

Les chemins et paramètres sont centralisés dans le code :

- Chemin dataset : `data/clean/events_clean.csv`
- Page Streamlit : configurée dans `code/app.py`

---

## Dépannage rapide

### Le fichier CSV n’est pas trouvé
- Vérifier la présence de `data/clean/events_clean.csv`
- Vérifier l’orthographe des dossiers : `clean` et `row`

### Erreur de mémoire
- Utiliser le cache Streamlit (déjà prévu dans le code)
- Réduire la plage temporelle de filtrage

### Port déjà utilisé
```bash
streamlit run code/app.py --server.port 8502
```

---

## Déploiement (optionnel)

### Streamlit Cloud
1. Pousser le dépôt sur GitHub
2. Créer une app sur https://streamlit.io/cloud
3. Pointer sur `code/app.py`

---

## Contribuer

1. Fork du dépôt
2. Nouvelle branche : `git checkout -b feature/ma-feature`
3. Commit : `git commit -m "Add feature"`
4. Push : `git push origin feature/ma-feature`
5. Pull Request

---

## Auteur

Jouvence13 — https://github.com/jouvence13
