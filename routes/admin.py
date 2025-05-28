from django.contrib import admin
from .models import Location, RouteRequest, OptimizedRoute

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'latitude', 'longitude', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'address']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'address')
        }),
        ('Coordonnées', {
            'fields': ('latitude', 'longitude')
        }),
    )

@admin.register(RouteRequest)
class RouteRequestAdmin(admin.ModelAdmin):
    list_display = ['departure', 'destination', 'transport_mode', 'user', 'created_at']
    list_filter = ['transport_mode', 'created_at']
    search_fields = ['departure__name', 'destination__name', 'user__username']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Itinéraire', {
            'fields': ('departure', 'destination', 'transport_mode')
        }),
        ('Utilisateur', {
            'fields': ('user',)
        }),
    )

@admin.register(OptimizedRoute)
class OptimizedRouteAdmin(admin.ModelAdmin):
    list_display = ['route_request', 'distance', 'duration', 'cost_estimate', 'created_at']
    list_filter = ['created_at', 'route_request__transport_mode']
    search_fields = ['route_request__departure__name', 'route_request__destination__name']
    ordering = ['-created_at']
    readonly_fields = ['route_data']
    
    fieldsets = (
        ('Demande de route', {
            'fields': ('route_request',)
        }),
        ('Résultats d\'optimisation', {
            'fields': ('distance', 'duration', 'cost_estimate')
        }),
        ('Données détaillées', {
            'fields': ('route_data',),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Si on modifie un objet existant
            return self.readonly_fields + ['route_request']
        return self.readonly_fields
