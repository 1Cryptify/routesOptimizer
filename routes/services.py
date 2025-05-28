import google.generativeai as genai
from django.conf import settings
import json
import requests
from typing import Dict, List, Tuple

class RouteOptimizer:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Taux de change EUR vers FCFA (approximatif)
        self.EUR_TO_FCFA = 656
    
    def get_coordinates(self, address: str) -> Tuple[float, float]:
        """Obtenir les coordonnées d'une adresse au Cameroun"""
        prompt = f"""
        Donnez-moi les coordonnées GPS précises (latitude, longitude) pour cette adresse au Cameroun:
        {address}
        
        Répondez uniquement avec les coordonnées au format JSON:
        {{
            "latitude": 0.0,
            "longitude": 0.0
        }}
        
        Exemple de réponse attendue:
        {{
            "latitude": 4.0511,
            "longitude": 9.7679
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = str(response.text).strip()
            if not response_text.startswith('{'): 
                response_text = response_text.split('{', 1)[1]
                response_text = '{' + response_text
            if not response_text.endswith('}'):
                response_text = response_text.rsplit('}', 1)[0] + '}'
            coords = json.loads(response_text)
            return (float(coords["latitude"]), float(coords["longitude"]))
        except Exception as e:
            # En cas d'erreur, demander à nouveau avec plus de contexte
            retry_prompt = f"""
            J'ai besoin des coordonnées GPS pour: {address}
            C'est au Cameroun. Utilisez vos connaissances des villes et régions camerounaises.
            Format JSON uniquement: {{"latitude": 4.0511, "longitude": 9.7679}}
            """
            response = self.model.generate_content(retry_prompt)
            response_text = str(response.text).strip()
            if not response_text.startswith('{'): 
                response_text = response_text.split('{', 1)[1]
                response_text = '{' + response_text
            if not response_text.endswith('}'):
                response_text = response_text.rsplit('}', 1)[0] + '}'
            coords = json.loads(response_text)
            return (float(coords["latitude"]), float(coords["longitude"]))
    
    def calculate_route_with_ai(self, departure: str, destination: str, transport_mode: str) -> Dict:
        """Utilise Gemini pour analyser et optimiser l'itinéraire au Cameroun"""
        
        prompt = f"""
        Je veux une analyse détaillée d'un itinéraire au Cameroun.
        
        DONNÉES:
        - Départ: {departure}
        - Destination: {destination}
        - Mode de transport: {transport_mode}
        
        CONTEXTE LOCAL:
        - Pays: Cameroun
        - Monnaie: Franc CFA (FCFA)
        - Conditions routières variables selon les régions
        - Impact saisonnier sur les trajets
        - Options de transport: bus, taxi-brousse, moto-taxi
        
        RÉPONDEZ STRICTEMENT AU FORMAT JSON SUIVANT:
        {{
            "optimal_route": {{
                "steps": ["étape 1", "étape 2"],
                "estimated_time": "120",
                "estimated_distance": "45.5",
                "cost_estimate": "5000"
            }},
            "alternatives": [
                {{
                    "route": "description alternative",
                    "time": "150",
                    "distance": "50.0",
                    "cost": "6000"
                }}
            ],
            "recommendations": ["conseil 1", "conseil 2"],
            "points_of_interest": ["point 1", "point 2"],
            "local_info": {{
                "weather_considerations": "Considérations météo",
                "road_conditions": "État des routes",
                "safety_tips": "Conseils de sécurité"
            }}
        }}

        IMPORTANT:
        - Toutes les valeurs numériques doivent être des chaînes de caractères
        - Respectez strictement la structure JSON fournie
        - Ne pas inclure d'explications ou de texte supplémentaire
        - Les étapes doivent être précises et réalistes
        """
        
        response = self.model.generate_content(prompt)
        response_text = str(response.text).strip()
        if not response_text.startswith('{'): 
            response_text = response_text.split('{', 1)[1]
            response_text = '{' + response_text
        if not response_text.endswith('}'):
            response_text = response_text.rsplit('}', 1)[0] + '}'
        route_data = json.loads(response_text)
        
        # Conversion des chaînes en valeurs numériques
        try:
            route_data["optimal_route"]["estimated_time"] = float(route_data["optimal_route"]["estimated_time"])
            route_data["optimal_route"]["estimated_distance"] = float(route_data["optimal_route"]["estimated_distance"])
            route_data["optimal_route"]["cost_estimate"] = float(route_data["optimal_route"]["cost_estimate"])
            
            for alt in route_data["alternatives"]:
                alt["time"] = float(alt["time"])
                alt["distance"] = float(alt["distance"])
                alt["cost"] = float(alt["cost"])
        except (ValueError, KeyError) as e:
            raise ValueError("Format de données invalide dans la réponse de l'IA")
            
        return route_data
    
    def optimize_route(self, departure_address: str, destination_address: str, transport_mode: str) -> Dict:
        """Méthode principale d'optimisation pour le Cameroun"""
        
        # Obtenir les coordonnées via l'IA
        dep_coords = self.get_coordinates(departure_address)
        dest_coords = self.get_coordinates(destination_address)
        
        # Analyser avec Gemini
        ai_analysis = self.calculate_route_with_ai(departure_address, destination_address, transport_mode)
        
        # Enrichir avec les coordonnées et informations locales
        result = {
            "departure": {
                "address": departure_address,
                "coordinates": dep_coords
            },
            "destination": {
                "address": destination_address,
                "coordinates": dest_coords
            },
            "transport_mode": transport_mode,
            "ai_analysis": ai_analysis,
            "currency": "FCFA",
            "country": "Cameroun"
        }
        
        return result