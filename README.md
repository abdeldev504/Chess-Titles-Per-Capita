# Analyse et Visualisation des Titres d'Échecs par Habitant

## 📝 Vue d'ensemble du projet

Ce projet analyse la répartition des titres d'échecs par million d'habitants dans différents pays. L'objectif est de mettre en lumière les pays qui excellent dans la formation de joueurs d'échecs de haut niveau par rapport à leur taille de population.

## 📊 Fonctionnalités principales

- **Scraping de données** : Récupération automatique des dernières données sur les titres d'échecs depuis le site de la FIDE.
- **Données de population** : Intégration des données de population provenant de Wikipedia pour calculer les titres par million d'habitants.
- **Analyse géospatiale** : Visualisation des données sur une carte du monde, avec une codification par couleur des pays en fonction de leur densité de titres par habitant.
- **Gestion personnalisée** : Prise en charge des cas spéciaux, comme la fusion de territoires disputés ou de petits pays, pour une visualisation précise.

## 🚀 Pour commencer

### Prérequis

Pour exécuter le projet, vous aurez besoin de :

- Python 3.x
- Les bibliothèques Python suivantes :
  - `pandas`
  - `requests`
  - `beautifulsoup4`
  - `geopandas`
  - `matplotlib`
  - `shapely`

### Installation

1. Clonez ce dépôt sur votre machine locale :
   ```bash
   git clone https://github.com/votre_nom_utilisateur/Chess-Titles-Per-Capita.git

2. Installer les dépendances requises :
   pip install pandas requests beautifulsoup4 geopandas matplotlib shapely

3. Exécutez le script principal :
   python map_fide_population.py

