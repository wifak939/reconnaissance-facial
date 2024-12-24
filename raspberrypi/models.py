from django.db import models


# Définition du modèle Capteurs pour stocker les données des capteurs environnementaux.
class Capteurs(models.Model):
    # Champ pour la température, enregistrée en tant que nombre à virgule flottante.
    temperature = models.FloatField()

    # Champ pour l'humidité, enregistrée en tant que chaîne de caractères (p.ex., "45%").
    humidity = models.CharField(max_length=10)

    # Champ booléen pour détecter la présence de gaz, par défaut à False (pas de gaz détecté).
    gas_detected = models.BooleanField(default=False)

    # Horodatage de l'enregistrement des données du capteur, ajouté automatiquement lors de la création.
    timestamp = models.DateTimeField(auto_now_add=True)

    # Méthode pour retourner une représentation en chaîne du modèle Capteurs.
    def __str__(self):
        return f"Temperature: {self.temperature}°C, Humidity: {self.humidity}, Gas: {'Oui' if self.gas_detected else 'Non'}, Time: {self.timestamp}"


# Définition du modèle FaceRecognition pour stocker les résultats de la reconnaissance faciale.
class FaceRecognition(models.Model):
    # Champ pour l'identité reconnue par le système de reconnaissance faciale.
    face_recognition_identity = models.CharField(max_length=50)

    # Horodatage de l'enregistrement de l'identité, ajouté automatiquement lors de la création.
    timestamp = models.DateTimeField(auto_now_add=True)

    # Méthode pour retourner une représentation en chaîne du modèle FaceRecognition.
    def __str__(self):
        return f"Face Recognition Identity: {self.face_recognition_identity}, Time: {self.timestamp}"
