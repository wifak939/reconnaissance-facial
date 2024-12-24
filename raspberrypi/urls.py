from django.urls import path
from . import views

# Définition du nom de l'application dans l'espace de nommage des URL.
app_name = 'raspberrypi'

# Définition des motifs d'URL pour l'application RaspberryPi.
urlpatterns = [
    # Route de base qui dirige vers la vue 'capteurs_view' de l'application.
    path('', views.capteurs_view, name='capteurs'),

    # Route pour la diffusion en direct de vidéo. Elle dirige vers la vue 'live_stream'.
    path('live_stream/', views.live_stream, name='live_stream'),

    # Route pour la vue de la caméra qui permet la reconnaissance faciale et l'inscription.
    path('camera/', views.camera_view, name='camera_view'),

    # Route pour capturer une image à partir du flux vidéo en direct.
    path('capture_image/', views.capture_image, name='capture_image'),
]

# Affichage des motifs d'URL pour vérification ou débogage.
print(urlpatterns)
