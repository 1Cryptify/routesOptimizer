from django import forms
from .models import RouteRequest, Location

class RouteRequestForm(forms.ModelForm):
    class Meta:
        model = RouteRequest
        fields = ['departure', 'destination', 'transport_mode']
        widgets = {
            'departure': forms.Select(attrs={'class': 'form-control'}),
            'destination': forms.Select(attrs={'class': 'form-control'}),
            'transport_mode': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['departure'].queryset = Location.objects.all()
        self.fields['destination'].queryset = Location.objects.all()
        
        # Ajouter des options vides
        self.fields['departure'].empty_label = "Choisir un point de départ"
        self.fields['destination'].empty_label = "Choisir une destination"
    
    def clean(self):
        cleaned_data = super().clean()
        departure = cleaned_data.get('departure')
        destination = cleaned_data.get('destination')
        
        if departure and destination and departure == destination:
            raise forms.ValidationError(
                "Le point de départ et la destination ne peuvent pas être identiques."
            )
        
        return cleaned_data

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'address', 'latitude', 'longitude']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
        }
        labels = {
            'name': 'Nom du lieu',
            'address': 'Adresse',
            'latitude': 'Latitude',
            'longitude': 'Longitude',
        }
        help_texts = {
            'latitude': 'Coordonnée géographique (décimal)',
            'longitude': 'Coordonnée géographique (décimal)',
        }
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 2:
            raise forms.ValidationError("Le nom doit contenir au moins 2 caractères.")
        return name
    
    def clean_address(self):
        address = self.cleaned_data['address']
        if len(address) < 5:
            raise forms.ValidationError("L'adresse doit être plus détaillée.")
        return address
    
    def clean_latitude(self):
        latitude = self.cleaned_data['latitude']
        if not (-90 <= latitude <= 90):
            raise forms.ValidationError("La latitude doit être comprise entre -90 et 90.")
        return latitude
    
    def clean_longitude(self):
        longitude = self.cleaned_data['longitude']
        if not (-180 <= longitude <= 180):
            raise forms.ValidationError("La longitude doit être comprise entre -180 et 180.")
        return longitude

class RouteSearchForm(forms.Form):
    """Formulaire de recherche rapide d'itinéraire"""
    departure_search = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher un point de départ...',
            'autocomplete': 'off'
        }),
        label='Départ'
    )
    destination_search = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher une destination...',
            'autocomplete': 'off'
        }),
        label='Destination'
    )
    transport_mode = forms.ChoiceField(
        choices=RouteRequest.TRANSPORT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Mode de transport'
    )

class LocationSearchForm(forms.Form):
    """Formulaire de recherche de lieux"""
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher un lieu...'
        })
    )

class RouteComparisonForm(forms.Form):
    """Formulaire pour comparer différents modes de transport"""
    departure = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Point de départ',
        empty_label="Choisir un point de départ"
    )
    destination = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Destination',
        empty_label="Choisir une destination"
    )
    transport_modes = forms.MultipleChoiceField(
        choices=RouteRequest.TRANSPORT_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Modes de transport à comparer'
    )
    
    def clean_transport_modes(self):
        modes = self.cleaned_data['transport_modes']
        if len(modes) < 2:
            raise forms.ValidationError(
                "Veuillez sélectionner au moins 2 modes de transport pour la comparaison."
            )
        return modes
    
    def clean(self):
        cleaned_data = super().clean()
        departure = cleaned_data.get('departure')
        destination = cleaned_data.get('destination')
        
        if departure and destination and departure == destination:
            raise forms.ValidationError(
                "Le point de départ et la destination ne peuvent pas être identiques."
            )
        
        return cleaned_data

class BulkLocationImportForm(forms.Form):
    """Formulaire pour importer plusieurs lieux en masse"""
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        label='Fichier CSV',
        help_text='Format: nom,adresse,latitude,longitude'
    )
    
    def clean_csv_file(self):
        file = self.cleaned_data['csv_file']
        if not file.name.endswith('.csv'):
            raise forms.ValidationError("Le fichier doit être au format CSV.")
        return file

class RouteFilterForm(forms.Form):
    """Formulaire de filtrage pour l'historique des routes"""
    transport_mode = forms.ChoiceField(
        choices=[('', 'Tous les modes')] + list(RouteRequest.TRANSPORT_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Mode de transport'
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Du'
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Au'
    )
    min_distance = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'placeholder': 'Distance minimale (km)'
        }),
        label='Distance min (km)'
    )
    max_distance = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'placeholder': 'Distance maximale (km)'
        }),
        label='Distance max (km)'
    )

class QuickRouteForm(forms.Form):
    """Formulaire rapide pour créer un itinéraire"""
    departure_coords = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    destination_coords = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    departure_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cliquez sur la carte pour le départ'
        }),
        label='Point de départ'
    )
    destination_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cliquez sur la carte pour la destination'
        }),
        label='Destination'
    )
    transport_mode = forms.ChoiceField(
        choices=RouteRequest.TRANSPORT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Mode de transport'
    )