from django.core.management.base import BaseCommand
from routes.models import Location

class Command(BaseCommand):
    help = 'Créer des données d\'exemple pour le Cameroun'

    def handle(self, *args, **options):
        # Supprimer les anciennes données
        Location.objects.all().delete()
        
        # Créer des locations d'exemple au Cameroun
        locations = [
            {
                'name': 'Aéroport International de Yaoundé-Nsimalen',
                'address': 'Nsimalen, Yaoundé, Cameroun',
                'latitude': 3.7226,
                'longitude': 11.5533
            },
            {
                'name': 'Gare Routière de Yaoundé',
                'address': 'Mvan, Yaoundé, Cameroun',
                'latitude': 3.8480,
                'longitude': 11.5021
            },
            {
                'name': 'Aéroport International de Douala',
                'address': 'Douala, Cameroun',
                'latitude': 4.0061,
                'longitude': 9.7195
            },
            {
                'name': 'Port de Douala',
                'address': 'Port de Douala, Cameroun',
                'latitude': 4.0435,
                'longitude': 9.7095
            },
            {
                'name': 'Université de Yaoundé I',
                'address': 'Ngoa-Ekellé, Yaoundé, Cameroun',
                'latitude': 3.8634,
                'longitude': 11.5208
            },
            {
                'name': 'Marché Central de Yaoundé',
                'address': 'Centre-ville, Yaoundé, Cameroun',
                'latitude': 3.8676,
                'longitude': 11.5174
            },
            {
                'name': 'Gare de Douala',
                'address': 'Bessengue, Douala, Cameroun',
                'latitude': 4.0511,
                'longitude': 9.7679
            },
            {
                'name': 'Université de Dschang',
                'address': 'Dschang, Région de l\'Ouest, Cameroun',
                'latitude': 5.4467,
                'longitude': 10.0539
            },
            {
                'name': 'Marché de Mokolo - Yaoundé',
                'address': 'Mokolo, Yaoundé, Cameroun',
                'latitude': 3.8789,
                'longitude': 11.5123
            },
            {
                'name': 'Stade Omnisports de Yaoundé',
                'address': 'Mfandena, Yaoundé, Cameroun',
                'latitude': 3.8456,
                'longitude': 11.5123
            },
            {
                'name': 'Palais des Congrès de Yaoundé',
                'address': 'Tsinga, Yaoundé, Cameroun',
                'latitude': 3.8915,
                'longitude': 11.5204
            },
            {
                'name': 'Hôpital Central de Yaoundé',
                'address': 'Centre-ville, Yaoundé, Cameroun',
                'latitude': 3.8634,
                'longitude': 11.5174
            }
        ]
        
        for loc_data in locations:
            Location.objects.create(**loc_data)
            self.stdout.write(
                self.style.SUCCESS(f'Location créée: {loc_data["name"]}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Données d\'exemple pour le Cameroun créées avec succès!')
        )