# 🚗 Routes Optimizer - Optimiseur d'Itinéraires pour le Cameroun

## 📋 Description

Routes Optimizer est une application Django intelligente qui utilise l'IA (Google Gemini) pour optimiser les itinéraires au Cameroun. L'application fournit des recommandations personnalisées en tenant compte des conditions locales, des coûts en FCFA, et des spécificités du transport camerounais.

## ✨ Fonctionnalités

- 🤖 **Optimisation IA** : Utilise Google Gemini pour analyser et optimiser les itinéraires
- 🗺️ **Cartes interactives** : Visualisation avec Folium et Leaflet
- 📍 **Gestion des lieux** : CRUD complet pour les emplacements
- 💰 **Calculs en FCFA** : Estimations de coûts adaptées au Cameroun
- 🚌 **Modes de transport** : Voiture, transport public, marche, vélo
- 📊 **Statistiques** : Analyses des trajets et performances
- 📈 **Historique** : Suivi des routes calculées
- 📤 **Export** : Export CSV des données

## 🛠️ Technologies

- **Backend** : Django 5.0+, Python 3.8+
- **IA** : Google Gemini 2.0-flash
- **Cartes** : Folium, Leaflet
- **Frontend** : Bootstrap 5, JavaScript
- **Base de données** : SQLite (dev), PostgreSQL (prod)

## 📦 Installation

### 1. Cloner le repository

```bash
git clone https://github.com/1Cryptify/routesOptimizer.git
cd routesOptimizer
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
```

### 3. Activer l'environnement virtuel

**Windows :**
```bash
venv\Scripts\activate
```

**Linux/Mac :**
```bash
source venv/bin/activate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 5. Configuration

Créez un fichier `.env` à la racine du projet :

```env
# Configuration Django
SECRET_KEY=votre_cle_secrete_django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Configuration Gemini AI
GEMINI_API_KEY=votre_cle_api_gemini

# Base de données (optionnel pour prod)
DATABASE_URL=sqlite:///db.sqlite3
```

**⚠️ Important :** Obtenez votre clé API Gemini sur [Google AI Studio](https://makersuite.google.com/app/apikey)

### 6. Migrations de la base de données

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Créer les données d'exemple pour le Cameroun

```bash
python manage.py create_sample_data
```

Cette commande va créer 12 lieux stratégiques au Cameroun incluant :
- Aéroports (Yaoundé-Nsimalen, Douala)
- Gares (Yaoundé, Douala)
- Universités (Yaoundé I, Dschang)
- Marchés (Central Yaoundé, Mokolo)
- Points d'intérêt (Stade Omnisports, Palais des Congrès, etc.)

### 8. Créer un superutilisateur (optionnel)

```bash
python manage.py createsuperuser
```

### 9. Lancer le serveur de développement

```bash
python manage.py runserver
```

🎉 **L'application est maintenant accessible sur** : http://localhost:8000

## 🚀 Utilisation

### 1. Page d'accueil
- Visualisez la carte interactive du Cameroun
- Consultez les statistiques
- Accédez rapidement aux fonctionnalités

### 2. Planifier un trajet
1. Cliquez sur "Planifier un trajet"
2. Sélectionnez votre point de départ
3. Choisissez votre destination
4. Sélectionnez le mode de transport
5. Cliquez sur "Optimiser avec l'IA"

### 3. Ajouter des lieux
1. Cliquez sur "Ajouter un lieu"
2. Remplissez les informations :
   - Nom du lieu
   - Adresse complète
   - Coordonnées GPS (latitude/longitude)
3. Sauvegardez

### 4. Gérer les lieux
- Consultez la liste complète des lieux
- Modifiez ou supprimez des emplacements
- Recherchez des lieux spécifiques

## 📁 Structure du projet

```
routesOptimizer/
├── transport_optimizer/          # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── routes/                       # App principale
│   ├── management/
│   │   └── commands/
│   │       └── create_sample_data.py  # Données d'exemple
│   ├── models.py                 # Modèles de données
│   ├── views.py                  # Vues et logique
│   ├── services.py               # Service d'optimisation IA
│   ├── forms.py                  # Formulaires Django
│   └── urls.py                   # URLs de l'app
├── templates/                    # Templates HTML
│   ├── base.html
│   └── routes/
├── static/                       # Fichiers statiques
├── requirements.txt              # Dépendances Python
└── README.md
```

## 🔧 Commandes utiles

### Gestion des données

```bash
# Créer les données d'exemple du Cameroun
python manage.py create_sample_data

# Sauvegarder la base de données
python manage.py dumpdata > backup.json

# Restaurer la base de données
python manage.py loaddata backup.json

# Nettoyer la base de données
python manage.py flush
```

### Développement

```bash
# Lancer les tests
python manage.py test

# Collecter les fichiers statiques (production)
python manage.py collectstatic

# Créer une migration
python manage.py makemigrations routes

# Appliquer les migrations
python manage.py migrate
```

## 🌍 Données pré-configurées

La commande `create_sample_data` ajoute ces lieux stratégiques :

| Lieu | Type | Ville |
|------|------|-------|
| Aéroport International de Yaoundé-Nsimalen | Transport | Yaoundé |
| Aéroport International de Douala | Transport | Douala |
| Gare Routière de Yaoundé | Transport | Yaoundé |
| Port de Douala | Transport | Douala |
| Université de Yaoundé I | Éducation | Yaoundé |
| Université de Dschang | Éducation | Dschang |
| Marché Central de Yaoundé | Commerce | Yaoundé |
| Marché de Mokolo | Commerce | Yaoundé |
| Stade Omnisports | Sport | Yaoundé |
| Palais des Congrès | Événements | Yaoundé |
| Hôpital Central | Santé | Yaoundé |
| Gare de Douala | Transport | Douala |

## 📊 API et fonctionnalités avancées

### Endpoints AJAX disponibles

- `POST /locations/add-ajax/` - Ajouter un lieu via AJAX
- `GET /api/search-locations/` - Rechercher des lieux
- `POST /api/optimize-route/` - Optimiser un itinéraire
- `GET /api/route-details/<id>/` - Détails d'une route

### Export de données

- Export CSV des routes : `/export/routes/`
- Export CSV des lieux : `/export/locations/`

## 🤝 Contribution

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Poussez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour toute question ou problème :

1. Consultez les [Issues GitHub](https://github.com/1Cryptify/routesOptimizer/issues)
2. Créez une nouvelle issue si nécessaire
3. Contactez l'équipe de développement

## 🎯 Roadmap

- [ ] Intégration avec des APIs de géolocalisation réelles
- [ ] Support multilingue (Français/Anglais)
- [ ] Application mobile (React Native)
- [ ] API REST complète
- [ ] Notifications en temps réel
- [ ] Intégration avec les services de transport local

---

**Développé avec ❤️ pour optimiser les déplacements au Cameroun**
