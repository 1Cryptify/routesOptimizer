from django.db import models
from django.contrib.auth.models import User

class Location(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom du lieu")
    address = models.CharField(max_length=500, verbose_name="Adresse")
    latitude = models.FloatField(verbose_name="Latitude")
    longitude = models.FloatField(verbose_name="Longitude")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Lieu"
        verbose_name_plural = "Lieux"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class RouteRequest(models.Model):
    TRANSPORT_CHOICES = [
        ('car', 'Voiture'),
        ('public', 'Transport Public'),
        ('walking', 'Marche'),
        ('bike', 'Vélo'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Utilisateur")
    departure = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='departures', verbose_name="Départ")
    destination = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='destinations', verbose_name="Destination")
    transport_mode = models.CharField(max_length=20, choices=TRANSPORT_CHOICES, default='car', verbose_name="Mode de transport")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    class Meta:
        verbose_name = "Demande de route"
        verbose_name_plural = "Demandes de routes"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.departure} -> {self.destination}"

class OptimizedRoute(models.Model):
    route_request = models.OneToOneField(RouteRequest, on_delete=models.CASCADE, verbose_name="Demande de route")
    route_data = models.JSONField(verbose_name="Données de route")  # Stocke les données de l'itinéraire optimisé
    distance = models.FloatField(null=True, blank=True, verbose_name="Distance (km)")  # Distance en km
    duration = models.IntegerField(null=True, blank=True, verbose_name="Durée (min)")  # Durée en minutes
    cost_estimate = models.FloatField(null=True, blank=True, verbose_name="Coût estimé (FCFA)")  # Coût estimé
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    class Meta:
        verbose_name = "Route optimisée"
        verbose_name_plural = "Routes optimisées"
        ordering = ['-created_at']

    def __str__(self):
        return f"Route optimisée pour {self.route_request}"
