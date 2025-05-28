from django.urls import path
from . import views

app_name = 'routes'

urlpatterns = [
    # Page d'accueil avec carte
    path('', views.index, name='index'),
    
    # Planification de routes
    path('plan/', views.plan_route, name='plan_route'),
    path('result/<int:route_id>/', views.route_result, name='route_result'),
    
    # Gestion des locations
    path('locations/', views.location_list, name='location_list'),
    path('locations/add/', views.add_location, name='add_location'),
    path('locations/add-ajax/', views.add_location_ajax, name='add_location_ajax'),
    path('locations/<int:location_id>/edit/', views.edit_location, name='edit_location'),
    path('locations/<int:location_id>/delete/', views.delete_location, name='delete_location'),
    
    # Historique des routes (nécessite une authentification)
    path('history/', views.route_history, name='route_history'),
    
    # Nouvelles routes pour les statistiques et comparaisons
    path('statistics/', views.statistics, name='statistics'),
    path('compare/', views.compare_routes, name='compare_routes'),
    path('export/routes/', views.export_routes, name='export_routes'),
    path('export/locations/', views.export_locations, name='export_locations'),
    
    # API AJAX
    path('api/search-locations/', views.search_locations, name='search_locations'),
    path('api/optimize-route/', views.optimize_route_ajax, name='optimize_route_ajax'),
    path('api/route-details/<int:route_id>/', views.get_route_details, name='get_route_details'),
]