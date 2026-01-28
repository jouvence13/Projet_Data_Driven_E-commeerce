# Dashboard Data-Driven – Analyse E-commerce

Un dashboard interactif et performant pour analyser le comportement des utilisateurs e-commerce.

---

## Vue d'ensemble

Ce projet est un **dashboard d'analyse data-driven** développé en Python avec **Streamlit**, permettant d'explorer et d'analyser le comportement des utilisateurs sur une plateforme e-commerce à partir de millions d'événements.

Le dashboard fournit des **indicateurs clés (KPIs)** et des **visualisations interactives** pour soutenir la prise de décision stratégique :

- **Engagement des utilisateurs** – Taux de conversion, événements par utilisateur
- **Rétention client** – Analyse de cohortes et taux de rétention
- **Tendances temporelles** – Évolution de l'activité par jour/heure
- **Tests A/B** – Comparaison de variantes et performance
- **Interface intuitive** – Exploration interactive et filtrage en temps réel  

---

## Démarrage rapide

### Prérequis
- Python 3.9+
- Git

### Installation

**1. Cloner le dépôt**

```bash
git clone https://github.com/jouvence13/Projet_Data_Driven_E-commeerce.git
cd Projet_Data_Driven_E-commeerce
```

**2. Créer et activer un environnement virtuel**

```bash
# macOS / Linux
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

**3. Installer les dépendances**

```bash
pip install -r requirements.txt
```

**4. Lancer le dashboard**

```bash
streamlit run code/app.py
```

L'application ouvrira automatiquement sur `http://localhost:8501`

---

## Données

| Propriété | Détails |
|-----------|---------|
| **Type** | Événements e-commerce (views, addtocart, transactions) |
| **Format** | CSV |
| **Taille** | ~192 MB |
| **Colonnes** | event_id, user_id, event, timestamp, cohort, et autres |
| **Localisation** | `data/clean/events_clean.csv` |

> **Note** : Le dataset est chargé dynamiquement avec mise en cache Streamlit pour optimiser les performances.

---

## Fonctionnalités principales

### Overview / KPIs
- Nombre total d'utilisateurs et événements
- Taux de conversion global
- Événements par utilisateur (moyenne)
- Indicateurs clés en temps réel

### Analyse de Cohortes
- Création de cohortes par date de premier événement
- Matrice de rétention (semaines/jours)
- Visualisation heatmap des taux de rétention
- Suivi de la fidélité utilisateur

### Analyse Temporelle
- Tendances journalières et horaires
- Répartition des événements par type
- Distribution par jour de la semaine
- Graphiques interactifs Plotly

### Tests A/B (optionnel)
- Comparaison de variantes
- Statistiques significatives
- Courbes de conversion

### Design & UX
- Interface épurée (noir/blanc)
- Responsive et rapide
- KPI cards avec styling moderne
- Tabs et filtres interactifs

---

## Stack Technologique

### Langages
- **Python 3.9+**

### Bibliothèques & Frameworks

| Catégorie | Outils |
|-----------|--------|
| **Web** | [Streamlit](https://streamlit.io/) – Interface interactive |
| **Data** | [Pandas](https://pandas.pydata.org/) – Manipulation de données |
| **Calcul** | [NumPy](https://numpy.org/) – Opérations numériques |
| **Visualisation** | [Plotly](https://plotly.com/) – Graphiques interactifs |
| | [Matplotlib](https://matplotlib.org/) – Visualisations statistiques |
| | [Seaborn](https://seaborn.pydata.org/) – Graphiques avancés |
| **ML** | [Scikit-learn](https://scikit-learn.org/) – Modélisation |

### Outils
- **Git / GitHub** – Versionnement du code
- **Jupyter Notebook** – Exploration et prototypage
- **Streamlit Community Cloud** – Déploiement
- **MongoDB** (optionnel) – Stockage des données

---

## Structure du projet

```
Projet_Data_Driven_E-commeerce/
├── code/
│   └── app.py                          # Application Streamlit principale
├── data/
│   ├── raw/                            # Données brutes
│   │   ├── events.csv
│   │   ├── category_tree.csv
│   │   └── item_properties_part*.csv
│   └── clean/
│       └── events_clean.csv            # Données nettoyées (~192 MB)
├── Notebook/
│   ├── data_traitement.ipynb           # Exploration & nettoyage
│   └── data/                           # Données de travail
├── data_collection/
│   └── insertion_versmongo.py          # Scripts MongoDB
├── src/
│   └── test_mongo.py                   # Tests
├── config/                             # Configuration
├── data_viz/                           # Scripts de visualisation
├── docs/                               # Documentation
├── requirements.txt                    # Dépendances Python
├── README.md                           # Ce fichier
└── .env                                # Variables d'environnement
```

---

## Configuration

Les paramètres principaux se trouvent dans `code/app.py` :

```python
# Chemin des données
EVENTS_CLEAN_PATH = PROJECT_ROOT / "data" / "clean" / "events_clean.csv"

# Configuration Streamlit
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="📊",
    layout="wide"
)
```

---

## Utilisation

### Pages principales

1. **Overview** – Vue d'ensemble des KPIs et tendances
2. **Cohortes** – Analyse de rétention par cohorte
3. **Analyse Temporelle** – Évolution jour/heure
4. **Tests A/B** – Comparaison de variantes

### Filtres disponibles
- Sélection de période (date range)
- Filtrage par cohort
- Filtrage par type d'événement
- Sélection de variante (A/B)

---

## Déploiement

### Sur Streamlit Cloud
1. Pousser le code sur GitHub
2. Se connecter à [Streamlit Cloud](https://streamlit.io/cloud)
3. Créer une nouvelle app en pointant vers ce dépôt
4. L'URL sera : `https://<username>-<appname>.streamlit.app`

### Sur un serveur personnel
```bash
# Installation de Streamlit sur le serveur
pip install streamlit

# Lancer avec Gunicorn (optionnel)
gunicorn --bind 0.0.0.0:8501 streamlit run code/app.py
```

---

## Améliorations futures

- [ ] Export des rapports (PDF/Excel)
- [ ] Prédictions et forecasting
- [ ] API REST pour l'intégration
- [ ] Dashboard mobile responsive
- [ ] Alertes automatiques sur les anomalies
- [ ] Multi-langue support
- [ ] Authentification utilisateurs

---

## Troubleshooting

### Les données ne se chargent pas
```bash
# Vérifier que le fichier existe
ls -la data/clean/events_clean.csv

# Vérifier les permissions
chmod 644 data/clean/events_clean.csv
```

### Erreurs de mémoire avec le dataset
- Utiliser le cache Streamlit (`@st.cache_data`)
- Réduire la portée temporelle des analyses
- Charger les données par chunks

### Port 8501 déjà utilisé
```bash
streamlit run code/app.py --server.port 8502
```

---

## Documentation additionnelle

- [Documentation Streamlit](https://docs.streamlit.io/)
- [Guide Pandas](https://pandas.pydata.org/docs/)
- [Plotly Charts](https://plotly.com/python/)

---

## Auteur

- **Jouvence13** – [GitHub Profile](https://github.com/jouvence13)

---

## License

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## Contribution

Les contributions sont bienvenues ! 

1. Forker le dépôt
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

---

Made by [Jouvence13](https://github.com/jouvence13)
