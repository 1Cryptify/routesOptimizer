import google.generativeai as genai
from django.conf import settings
import json
import requests
import random
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class RouteOptimizer:
    def __init__(self):
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.EUR_TO_FCFA = 656
        except Exception as e:
            logger.error(f"Erreur d'initialisation RouteOptimizer: {e}")
            raise
    
    def get_coordinates(self, address: str) -> Tuple[float, float]:
        """Obtenir les coordonnées d'une adresse au Cameroun"""
        try:
            prompt = f"""
            Donnez-moi les coordonnées GPS précises (latitude, longitude) pour cette adresse au Cameroun:
            {address}
            
            Répondez uniquement avec les coordonnées au format JSON:
            {{
                "latitude": 0.0,
                "longitude": 0.0
            }}
            """
            
            response = self.model.generate_content(prompt)
            response_text = str(response.text).strip()
            
            # Nettoyage et validation du JSON
            if not response_text.startswith('{'): 
                response_text = response_text.split('{', 1)[1]
                response_text = '{' + response_text
            if not response_text.endswith('}'):
                response_text = response_text.rsplit('}', 1)[0] + '}'
                
            coords = json.loads(response_text)
            
            # Validation des coordonnées
            lat = float(coords["latitude"])
            lon = float(coords["longitude"])
            
            if not (2.0 <= lat <= 13.0 and 8.0 <= lon <= 16.0):
                raise ValueError("Coordonnées hors limites du Cameroun")
                
            return (lat, lon)
            
        except Exception as e:
            logger.warning(f"Erreur get_coordinates pour {address}: {e}")
            # Coordonnées par défaut sécurisées pour le Cameroun
            return (3.8480, 11.5021)  # Yaoundé
    
    def calculate_route_with_ai(self, departure: str, destination: str, transport_mode: str) -> Dict:
        """Utilise Gemini pour analyser et optimiser l'itinéraire au Cameroun"""
        try:
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
                    "estimated_time": 120,
                    "estimated_distance": 45.5,
                    "cost_estimate": 5000
                }},
                "alternatives": [
                    {{
                        "route": "description alternative",
                        "time": 150,
                        "distance": 50.0,
                        "cost": 6000
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
            """
            
            response = self.model.generate_content(prompt)
            response_text = str(response.text).strip()
            
            # Nettoyage et validation du JSON
            if not response_text.startswith('{'): 
                response_text = response_text.split('{', 1)[1]
                response_text = '{' + response_text
            if not response_text.endswith('}'):
                response_text = response_text.rsplit('}', 1)[0] + '}'
                
            route_data = json.loads(response_text)
            
            # Validation et conversion des données numériques
            try:
                route_data["optimal_route"]["estimated_time"] = float(route_data["optimal_route"]["estimated_time"])
                route_data["optimal_route"]["estimated_distance"] = float(route_data["optimal_route"]["estimated_distance"])
                route_data["optimal_route"]["cost_estimate"] = float(route_data["optimal_route"]["cost_estimate"])
                
                for alt in route_data["alternatives"]:
                    alt["time"] = float(alt["time"])
                    alt["distance"] = float(alt["distance"])
                    alt["cost"] = float(alt["cost"])
            except (ValueError, KeyError) as e:
                logger.error(f"Erreur de conversion des données: {e}")
                raise
                
            return route_data
            
        except Exception as e:
            logger.error(f"Erreur calculate_route_with_ai: {e}")
            # Données par défaut sécurisées
            return {
                "optimal_route": {
                    "steps": ["Départ", "Arrivée"],
                    "estimated_time": 120.0,
                    "estimated_distance": 45.5,
                    "cost_estimate": 5000.0
                },
                "alternatives": [
                    {
                        "route": "Route alternative",
                        "time": 150.0,
                        "distance": 50.0,
                        "cost": 6000.0
                    }
                ],
                "recommendations": ["Vérifiez la météo avant le départ", "Prévoyez de l'eau"],
                "points_of_interest": ["Station-service", "Marché local"],
                "local_info": {
                    "weather_considerations": "Vérifiez la météo locale",
                    "road_conditions": "État des routes variable",
                    "safety_tips": "Voyagez de préférence le jour"
                }
            }
    
    def optimize_route(self, departure_address: str, destination_address: str, transport_mode: str) -> Dict:
        """Méthode principale d'optimisation pour le Cameroun"""
        try:
            # Validation des entrées
            if not all([departure_address, destination_address, transport_mode]):
                raise ValueError("Tous les paramètres sont requis")
            
            # Obtenir les coordonnées
            dep_coords = self.get_coordinates(departure_address)
            dest_coords = self.get_coordinates(destination_address)
            
            # Analyser avec Gemini
            ai_analysis = self.calculate_route_with_ai(departure_address, destination_address, transport_mode)
            
            # Construction du résultat
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
            
        except Exception as e:
            logger.error(f"Erreur optimize_route: {e}")
            # Résultat par défaut sécurisé
            return {
                "departure": {
                    "address": departure_address,
                    "coordinates": (3.8480, 11.5021)  # Yaoundé
                },
                "destination": {
                    "address": destination_address,
                    "coordinates": (4.0511, 9.7679)  # Douala
                },
                "transport_mode": transport_mode,
                "ai_analysis": self.calculate_route_with_ai(departure_address, destination_address, transport_mode),
                "currency": "FCFA",
                "country": "Cameroun"
            }