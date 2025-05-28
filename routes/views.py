from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import json
import csv
import folium
from folium import plugins
from .models import Location, RouteRequest, OptimizedRoute
from .forms import LocationForm, RouteRequestForm
from .services import RouteOptimizer
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# VUES PRINCIPALES
# ============================================================================

def index(request):
    """Page d'accueil avec carte interactive et statistiques"""
    try:
        # Récupération des données
        locations = Location.objects.all().order_by('-created_at')[:10]
        total_locations = Location.objects.count()
        total_routes = OptimizedRoute.objects.count()
        recent_routes = OptimizedRoute.objects.select_related(
            'route_request__departure', 
            'route_request__destination'
        ).order_by('-created_at')[:5]
        
        # Statistiques
        stats = {
            'total_locations': total_locations,
            'total_routes': total_routes,
            'recent_routes': recent_routes,
        }
        
        # Création de la carte
        map_html = create_main_map(locations)
        
        context = {
            'locations': locations,
            'stats': stats,
            'map_html': map_html,
        }
        
        return render(request, 'routes/index.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans index: {e}")
        messages.error(request, "Erreur lors du chargement de la page")
        return render(request, 'routes/index.html', {
            'locations': [],
            'stats': {'total_locations': 0, 'total_routes': 0, 'recent_routes': []},
            'map_html': create_default_map(),
        })

def plan_route(request):
    """Planification d'itinéraire avec IA"""
    if request.method == 'POST':
        form = RouteRequestForm(request.POST)
        if form.is_valid():
            try:
                # Création de la demande de route
                route_request = form.save(commit=False)
                if request.user.is_authenticated:
                    route_request.user = request.user
                route_request.save()
                
                # Optimisation avec l'IA
                optimizer = RouteOptimizer()
                route_data = optimizer.optimize_route(
                    departure_address=route_request.departure.address,
                    destination_address=route_request.destination.address,
                    transport_mode=route_request.transport_mode
                )
                
                # Extraction des données pour sauvegarde
                ai_analysis = route_data.get('ai_analysis', {})
                optimal_route = ai_analysis.get('optimal_route', {})
                
                # Création de la route optimisée
                optimized_route = OptimizedRoute.objects.create(
                    route_request=route_request,
                    route_data=route_data,
                    distance=float(optimal_route.get('estimated_distance', '0').replace(' km', '').replace(',', '.')),
                    duration=int(optimal_route.get('estimated_time', '0').replace(' minutes', '').replace(' min', '')),
                    cost_estimate=float(optimal_route.get('cost_estimate', '0').replace(' FCFA', '').replace(',', ''))
                )
                
                messages.success(request, f"Itinéraire optimisé avec succès! Distance: {optimized_route.distance} km, Durée: {optimized_route.duration} min")
                return redirect('routes:route_result', route_id=optimized_route.id)
                
            except Exception as e:
                logger.error(f"Erreur lors de l'optimisation: {e}")
                messages.error(request, f"Erreur lors de l'optimisation de l'itinéraire: {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire")
    else:
        form = RouteRequestForm()
    
    return render(request, 'routes/plan_route.html', {'form': form})

def route_result(request, route_id):
    """Affichage du résultat d'optimisation"""
    try:
        optimized_route = get_object_or_404(
            OptimizedRoute.objects.select_related(
                'route_request__departure',
                'route_request__destination'
            ),
            id=route_id
        )
        
        # Création de la carte pour cet itinéraire
        map_html = create_route_map(optimized_route)
        
        context = {
            'optimized_route': optimized_route,
            'route_data': optimized_route.route_data,
            'map_html': map_html,
        }
        
        return render(request, 'routes/route_result.html', context)
        
    except Exception as e:
        logger.error(f"Erreur dans route_result: {e}")
        messages.error(request, "Erreur lors de l'affichage du résultat")
        return redirect('routes:index')

# ============================================================================
# GESTION DES LIEUX
# ============================================================================

def location_list(request):
    """Liste paginée des lieux"""
    search_query = request.GET.get('search', '')
    locations = Location.objects.all().order_by('-created_at')
    
    if search_query:
        locations = locations.filter(
            Q(name__icontains=search_query) | 
            Q(address__icontains=search_query)
        )
    
    paginator = Paginator(locations, 12)  # 12 lieux par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'locations': page_obj,
        'search_query': search_query,
        'total_count': locations.count(),
    }
    
    return render(request, 'routes/location_list.html', context)

def add_location(request):
    """Ajout d'un nouveau lieu"""
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            try:
                location = form.save()
                messages.success(request, f"Lieu '{location.name}' ajouté avec succès!")
                return redirect('routes:location_list')
            except Exception as e:
                logger.error(f"Erreur lors de l'ajout du lieu: {e}")
                messages.error(request, "Erreur lors de l'ajout du lieu")
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire")
    else:
        form = LocationForm()
    
    return render(request, 'routes/add_location.html', {'form': form})

def edit_location(request, location_id):
    """Modification d'un lieu existant"""
    location = get_object_or_404(Location, id=location_id)
    
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            try:
                location = form.save()
                messages.success(request, f"Lieu '{location.name}' modifié avec succès!")
                return redirect('routes:location_list')
            except Exception as e:
                logger.error(f"Erreur lors de la modification: {e}")
                messages.error(request, "Erreur lors de la modification")
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire")
    else:
        form = LocationForm(instance=location)
    
    context = {
        'form': form,
        'location': location,
    }
    
    return render(request, 'routes/edit_location.html', context)

def delete_location(request, location_id):
    """Suppression d'un lieu"""
    location = get_object_or_404(Location, id=location_id)
    
    if request.method == 'POST':
        try:
            # Vérifier s'il y a des routes associées
            routes_count = RouteRequest.objects.filter(
                Q(departure=location) | Q(destination=location)
            ).count()
            
            if routes_count > 0:
                messages.warning(
                    request, 
                    f"Attention: Ce lieu est utilisé dans {routes_count} route(s). "
                    "Les routes associées seront également affectées."
                )
            
            location_name = location.name
            location.delete()
            messages.success(request, f"Lieu '{location_name}' supprimé avec succès!")
            return redirect('routes:location_list')
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression: {e}")
            messages.error(request, "Erreur lors de la suppression")
    
    context = {
        'location': location,
        'routes_count': RouteRequest.objects.filter(
            Q(departure=location) | Q(destination=location)
        ).count(),
    }
    
    return render(request, 'routes/delete_location.html', context)

# ============================================================================
# HISTORIQUE ET STATISTIQUES
# ============================================================================

@login_required
def route_history(request):
    """Historique des routes de l'utilisateur"""
    routes = OptimizedRoute.objects.filter(
        route_request__user=request.user
    ).select_related(
        'route_request__departure',
        'route_request__destination'
    ).order_by('-created_at')
    
    paginator = Paginator(routes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques personnelles
    total_distance = sum(route.distance or 0 for route in routes)
    total_cost = sum(route.cost_estimate or 0 for route in routes)
    avg_distance = routes.aggregate(Avg('distance'))['distance__avg'] or 0
    
    context = {
        'routes': page_obj,
        'stats': {
            'total_routes': routes.count(),
            'total_distance': total_distance,
            'total_cost': total_cost,
            'avg_distance': round(avg_distance, 2),
        }
    }
    
    return render(request, 'routes/route_history.html', context)

def statistics(request):
    """Page de statistiques générales"""
    # Statistiques générales
    total_locations = Location.objects.count()
    total_routes = OptimizedRoute.objects.count()
    
    # Statistiques par mode de transport
    transport_stats = RouteRequest.objects.values('transport_mode').annotate(
        count=Count('id'),
        avg_distance=Avg('optimizedroute__distance'),
        avg_cost=Avg('optimizedroute__cost_estimate')
    ).order_by('-count')
    
    # Routes récentes (30 derniers jours)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_routes = OptimizedRoute.objects.filter(
        created_at__gte=thirty_days_ago
    ).count()
    
    # Lieux les plus utilisés
    popular_locations = Location.objects.annotate(
        departure_count=Count('departures'),
        destination_count=Count('destinations')
    ).order_by('-departure_count', '-destination_count')[:10]
    
    context = {
        'total_locations': total_locations,
        'total_routes': total_routes,
        'recent_routes': recent_routes,
        'transport_stats': transport_stats,
        'popular_locations': popular_locations,
    }
    
    return render(request, 'routes/statistics.html', context)

# ============================================================================
# VUES AJAX ET API
# ============================================================================

@require_http_methods(["POST"])
def add_location_ajax(request):
    """Ajout de lieu via AJAX"""
    try:
        data = json.loads(request.body)
        
        location = Location.objects.create(
            name=data['name'],
            address=data['address'],
            latitude=data['latitude'],
            longitude=data['longitude']
        )
        
        return JsonResponse({
            'success': True,
            'location': {
                'id': location.id,
                'name': location.name,
                'address': location.address,
                'coordinates': [location.latitude, location.longitude]
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur AJAX add_location: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def search_locations(request):
    """Recherche de lieux via AJAX"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'locations': []})
    
    locations = Location.objects.filter(
        Q(name__icontains=query) | 
        Q(address__icontains=query)
    )[:10]
    
    locations_data = [{
        'id': loc.id,
        'name': loc.name,
        'address': loc.address,
        'coordinates': [loc.latitude, loc.longitude]
    } for loc in locations]
    
    return JsonResponse({'locations': locations_data})

@require_http_methods(["POST"])
def optimize_route_ajax(request):
    """Optimisation de route via AJAX"""
    try:
        data = json.loads(request.body)
        
        departure = get_object_or_404(Location, id=data['departure_id'])
        destination = get_object_or_404(Location, id=data['destination_id'])
        transport_mode = data['transport_mode']
        
        # Création de la demande
        route_request = RouteRequest.objects.create(
            departure=departure,
            destination=destination,
            transport_mode=transport_mode,
            user=request.user if request.user.is_authenticated else None
        )
        
        # Optimisation
        optimizer = RouteOptimizer()
        route_data = optimizer.optimize_route(
            departure_address=departure.address,
            destination_address=destination.address,
            transport_mode=transport_mode
        )
        
        # Sauvegarde
        ai_analysis = route_data.get('ai_analysis', {})
        optimal_route = ai_analysis.get('optimal_route', {})
        
        optimized_route = OptimizedRoute.objects.create(
            route_request=route_request,
            route_data=route_data,
            distance=float(optimal_route.get('estimated_distance', '0').replace(' km', '').replace(',', '.')),
            duration=int(optimal_route.get('estimated_time', '0').replace(' minutes', '').replace(' min', '')),
            cost_estimate=float(optimal_route.get('cost_estimate', '0').replace(' FCFA', '').replace(',', ''))
        )
        
        return JsonResponse({
            'success': True,
            'route_id': optimized_route.id,
            'route_data': route_data
        })
        
    except Exception as e:
        logger.error(f"Erreur AJAX optimize_route: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

def get_route_details(request, route_id):
    """Récupération des détails d'une route via AJAX"""
    try:
        route = get_object_or_404(OptimizedRoute, id=route_id)
        
        return JsonResponse({
            'success': True,
            'route': {
                'id': route.id,
                'departure': route.route_request.departure.name,
                'destination': route.route_request.destination.name,
                'transport_mode': route.route_request.get_transport_mode_display(),
                'distance': route.distance,
                'duration': route.duration,
                'cost_estimate': route.cost_estimate,
                'ai_analysis': route.route_data.get('ai_analysis', {}),
                'created_at': route.created_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur get_route_details: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

# ============================================================================
# COMPARAISON ET EXPORT
# ============================================================================

def compare_routes(request):
    """Comparaison de routes"""
    route_ids = request.GET.getlist('routes')
    
    if len(route_ids) < 2:
        messages.error(request, "Veuillez sélectionner au moins 2 routes à comparer")
        return redirect('routes:route_history')
    
    routes = OptimizedRoute.objects.filter(
        id__in=route_ids
    ).select_related(
        'route_request__departure',
        'route_request__destination'
    )
    
    # Analyse comparative
    comparison_data = {
        'routes': routes,
        'fastest': min(routes, key=lambda r: r.duration or float('inf')),
        'shortest': min(routes, key=lambda r: r.distance or float('inf')),
        'cheapest': min(routes, key=lambda r: r.cost_estimate or float('inf')),
    }
    
    return render(request, 'routes/compare_routes.html', comparison_data)

def export_routes(request):
    """Export des routes en CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="routes_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Date', 'Départ', 'Destination', 'Mode Transport', 
        'Distance (km)', 'Durée (min)', 'Coût (FCFA)'
    ])
    
    routes = OptimizedRoute.objects.select_related(
        'route_request__departure',
        'route_request__destination'
    ).order_by('-created_at')
    
    for route in routes:
        writer.writerow([
            route.created_at.strftime('%Y-%m-%d %H:%M'),
            route.route_request.departure.name,
            route.route_request.destination.name,
            route.route_request.get_transport_mode_display(),
            route.distance or 0,
            route.duration or 0,
            route.cost_estimate or 0
        ])
    
    return response

def export_locations(request):
    """Export des lieux en CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="locations_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Adresse', 'Latitude', 'Longitude', 'Date création'])
    
    locations = Location.objects.all().order_by('-created_at')
    
    for location in locations:
        writer.writerow([
            location.name,
            location.address,
            location.latitude,
            location.longitude,
            location.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    return response

# ============================================================================
# FONCTIONS UTILITAIRES POUR LES CARTES
# ============================================================================

def create_main_map(locations):
    """Crée la carte principale avec tous les lieux"""
    # Centre par défaut: Yaoundé, Cameroun
    center_lat, center_lon = 3.8480, 11.5021
    
    if locations:
        # Centrer sur la moyenne des coordonnées
        center_lat = sum(loc.latitude for loc in locations) / len(locations)
        center_lon = sum(loc.longitude for loc in locations) / len(locations)
    
    # Création de la carte
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=10,
        tiles='OpenStreetMap'
    )
    
    # Ajout des marqueurs pour chaque lieu
    for location in locations:
        folium.Marker(
            [location.latitude, location.longitude],
            popup=f"""
                <b>{location.name}</b><br>
                {location.address}<br>
                <small>Lat: {location.latitude}, Lon: {location.longitude}</small>
            """,
            tooltip=location.name,
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)
    
    # Ajout du contrôle de couches
    folium.LayerControl().add_to(m)
    
    return m._repr_html_()

def create_route_map(optimized_route):
    """Crée une carte pour un itinéraire spécifique"""
    departure = optimized_route.route_request.departure
    destination = optimized_route.route_request.destination
    
    # Centre entre départ et destination
    center_lat = (departure.latitude + destination.latitude) / 2
    center_lon = (departure.longitude + destination.longitude) / 2
    
    # Création de la carte
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12
    )
    
    # Marqueur de départ
    folium.Marker(
        [departure.latitude, departure.longitude],
        popup=f"<b>Départ:</b> {departure.name}",
        tooltip="Point de départ",
        icon=folium.Icon(color='green', icon='play')
    ).add_to(m)
    
    # Marqueur de destination
    folium.Marker(
        [destination.latitude, destination.longitude],
        popup=f"<b>Destination:</b> {destination.name}",
        tooltip="Point d'arrivée",
        icon=folium.Icon(color='red', icon='stop')
    ).add_to(m)
    
    # Ligne entre départ et destination
    folium.PolyLine(
        locations=[
            [departure.latitude, departure.longitude],
            [destination.latitude, destination.longitude]
        ],
        weight=4,
        color='blue',
        opacity=0.8
    ).add_to(m)
    
    # Ajustement du zoom pour inclure tous les points
    m.fit_bounds([
        [departure.latitude, departure.longitude],
        [destination.latitude, destination.longitude]
    ])
    
    return m._repr_html_()

def create_default_map():
    """Crée une carte par défaut centrée sur le Cameroun"""
    m = folium.Map(
        location=[3.8480, 11.5021],  # Yaoundé
        zoom_start=7,
        tiles='OpenStreetMap'
    )
    
    # Marqueur pour Yaoundé
    folium.Marker(
        [3.8480, 11.5021],
        popup="Yaoundé - Capitale du Cameroun",
        tooltip="Yaoundé",
        icon=folium.Icon(color='red', icon='star')
    ).add_to(m)
    
    return m._repr_html_()
