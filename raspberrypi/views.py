from .models import Capteurs, FaceRecognition  # Importe les modèles Capteurs et FaceRecognition de Django
import paho.mqtt.client as mqtt  # Importe la bibliothèque MQTT pour la communication réseau
import json  # Importe la bibliothèque JSON pour la manipulation de données JSON
import threading  # Importe la bibliothèque de threading pour exécuter des processus en parallèle
import os  # Importe la bibliothèque os pour interagir avec le système d'exploitation
from datetime import datetime  # Importe la classe datetime pour manipuler les dates et heures
from PIL import Image  # Importe la bibliothèque PIL pour manipuler les images
import io  # Importe la bibliothèque io pour la gestion des flux de données

# Configuration du broker MQTT
broker_address = "192.168.19.234"  # Définit l'adresse du broker MQTT
received_messages = {"Capteurs": "", "Face Recognition": ""}  # Initialise un dictionnaire pour stocker les messages MQTT reçus

def reset_received_messages():
    global received_messages  # Déclare la variable received_messages comme globale
    received_messages = {"Capteurs": "", "Face Recognition": ""}  # Réinitialise le dictionnaire des messages reçus

# Fonctions MQTT
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")  # Affiche le code de résultat de la connexion MQTT
    for topic in received_messages.keys():
        client.subscribe(topic)  # S'abonne aux sujets définis dans received_messages

def on_message(client, userdata, msg):
    payload = msg.payload.decode()  # Décode le payload du message
    topic = msg.topic  # Récupère le sujet du message
    received_messages[topic] = payload  # Stocke le message dans le dictionnaire
    print(f"Received message '{payload}' on topic '{topic}'")  # Affiche le message reçu

# Configuration du client MQTT pour la souscription
mqtt_client = mqtt.Client("Django_MQTT_Subscriber")  # Crée un client MQTT pour Django
mqtt_client.on_connect = on_connect  # Définit la fonction à appeler lors de la connexion
mqtt_client.on_message = on_message  # Définit la fonction à appeler lors de la réception d'un message
mqtt_client.connect(broker_address)  # Connecte le client MQTT au broker

# Démarrage du thread MQTT
def mqtt_subscriber():
    mqtt_client.loop_forever()  # Démarre une boucle pour écouter les messages MQTT indéfiniment

mqtt_thread = threading.Thread(target=mqtt_subscriber)  # Crée un thread pour exécuter mqtt_subscriber
mqtt_thread.daemon = True  # Définit le thread comme un daemon
mqtt_thread.start()  # Démarre le thread

# Fonction pour gérer les images téléchargées
def handle_uploaded_image(image):
    folder = 'uploads/images'  # Définit le dossier de destination pour les images téléchargées
    file_path = os.path.join(folder, image.name)  # Construit le chemin complet du fichier

    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Crée le dossier s'il n'existe pas

    with open(file_path, 'wb') as destination:  # Ouvre le fichier en mode écriture binaire
        for chunk in image.chunks():  # Parcourt les morceaux de l'image
            destination.write(chunk)  # Écrit chaque morceau dans le fichier

    return file_path  # Retourne le chemin du fichier

# Configuration du client MQTT pour la publication
client = mqtt.Client("Django_MQTT_Publisher")  # Crée un client MQTT pour publier des messages
client.connect(broker_address)  # Connecte le client au broker MQTT

# Vue Django pour les capteurs
def capteurs_view(request):
    if request.method == 'POST':
        # Gère les images téléchargées
        if 'image' in request.FILES:
            image = request.FILES['image']
            if image.content_type.startswith('image'):
                file_path = handle_uploaded_image(image)  # Traite l'image téléchargée
                print("Image saved at:", file_path)

                image = Image.open(file_path)  # Ouvre l'image avec PIL

                with io.BytesIO() as buffer:
                    image.save(buffer, format="PNG")  # Sauvegarde l'image dans un buffer
                    image_bytes = buffer.getvalue()  # Récupère les données de l'image

                client.publish("Image_topic", payload=image_bytes, qos=0)  # Publie l'image sur le sujet "Image_topic"

                client.disconnect()  # Déconnecte le client MQTT

    # Traite les messages MQTT reçus
    for topic, message in received_messages.items():
        if topic == "Capteurs" and len(message) > 0:
            data = json.loads(message)  # Convertit le message JSON en dictionnaire
            temperature = data.get('Temperature')
            humidity = data.get('Humidity')
            gas_detected = data.get('Gas')
            timestamp = datetime.now()  # Récupère le timestamp actuel
            capteur = Capteurs(temperature=temperature, humidity=humidity, gas_detected=gas_detected,
                               timestamp=timestamp)  # Crée un objet Capteurs
            capteur.save()  # Enregistre l'objet dans la base de données

        elif topic == "Face Recognition" and len(message) > 0:
            face_recognition_identity = message  # Récupère l'identité reconnue
            timestamp = datetime.now()  # Récupère le timestamp actuel
            face_recognition = FaceRecognition(face_recognition_identity=face_recognition_identity, timestamp=timestamp)
            face_recognition.save()  # Enregistre l'objet dans la base de données

    reset_received_messages()  # Réinitialise les messages reçus
    capteurs = Capteurs.objects.all()  # Récupère tous les objets Capteurs de la base de données
    face_recognitions = FaceRecognition.objects.all()  # Récupère tous les objets FaceRecognition de la base de données

    context = {  # Prépare le contexte pour le template Django
        'capteurs': capteurs,
        'face_recognitions': face_recognitions,
    }
    return render(request, 'capteurs.html', context)  # Rend le template avec le contexte


from django.views.decorators import gzip
from django.http import StreamingHttpResponse
from django.shortcuts import render
import cv2
from django.http import JsonResponse

# Utilisation de gzip pour optimiser la transmission de données
@gzip.gzip_page
def live_stream(request):
    print('live_stream')
    # Diffusion en streaming de la vidéo capturée
    return StreamingHttpResponse(gen(), content_type="multipart/x-mixed-replace;boundary=frame")

# Fonction génératrice pour le streaming vidéo
def gen():
    cap = cv2.VideoCapture(0)  # Capture vidéo à partir de la première caméra
    while True:
        success, frame = cap.read()  # Lecture d'une image depuis la caméra
        if not success:
            continue  # Continue si la capture est réussie

        global current_image
        current_image = frame  # Stockage de l'image actuelle

        _, buffer = cv2.imencode('.jpg', frame)  # Encodage de l'image en JPEG
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')  # Envoi de l'image en tant que flux

# Vue pour capturer et sauvegarder une image du flux vidéo
def capture_image(request):
    global current_image
    if 'current_image' in globals() and current_image is not None:
        image_path = "uploads/saved_image.jpg"
        cv2.imwrite(image_path, current_image)  # Écriture de l'image actuelle dans un fichier
        return JsonResponse({'message': 'Image captured and saved successfully'})  # Réponse JSON de succès
    else:
        return JsonResponse({'error': 'Failed to capture image'})  # Réponse JSON d'erreur

# Reconnaissance faciale et inscription
import cv2
import face_recognition
from face_rec import database_cr, face_detection, visulize_identity, draw_rec, save_faces_database

# Fonction pour l'inscription via la reconnaissance faciale
def Signup_face_recognition(image, user_name):
    faces_database, names = database_cr()  # Chargement de la base de données des visages
    print(names)
    user_exist_db = False
    face_det = face_detection(image)  # Détection des visages dans l'image
    print(face_det)

    if len(face_det) > 0:  # Vérification de la présence d'un visage
        box, idx = face_det
        image = draw_rec(image, box)  # Dessin d'un rectangle autour du visage
        image_face = image
        face_encodings = face_recognition.face_encodings(image_face, [box])  # Encodage du visage

        if len(face_encodings) > 0:
            distance = face_recognition.face_distance(faces_database, face_encodings[0])  # Calcul de la distance
            print('distance:', distance)

            verified = face_recognition.compare_faces(faces_database, face_encodings[0], tolerance=0.45)  # Comparaison des visages
            print(verified)
            if True in verified:
                name = names[verified.index(True)]
                user_exist_db = True
                print('Bienvenu', name, 'vous êtes déjà enregisté dans la base des données')
                image = visulize_identity(image, name, box)  # Visualisation de l'identité

            else:
                print('Vous n\'êtes pas dans la base des données.')
                faces_database.append(face_encodings[0])  # Ajout du nouveau visage à la base de données
                image = visulize_identity(image, user_name, box)  # Visualisation de l'identité
                names.append(user_name)
                save_faces_database(faces_database, names)  # Sauvegarde de la base de données
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                print(len(faces_database))
                print(names)
                print('Visage enregisté avec succès.')

    return image, user_exist_db

# Vue pour gérer la capture de l'image et l'inscription
def camera_view(request):
    global current_image

    if request.method == "POST":
        user_name = request.POST.get("user_input")  # Récupération du nom d'utilisateur
        print(user_name)
        if current_image is not None:
            image_face_rec = current_image
            image_path = "uploads/saved_image.jpg"
            image, user_exist_db = Signup_face_recognition(image_face_rec, user_name)  # Traitement de l'image pour la reconnaissance faciale
            print('user_exist_db', user_exist_db)
            cv2.imwrite(image_path, current_image)  # Sauvegarde de l'image
            current_image = None
            files = ['names', 'faces_database']
            for filename in files:
                with open(filename, "rb") as file:
                    file_bytes = file.read()
                client.publish(filename, payload=file_bytes, qos=0)  # Publication des données via MQTT

            print('Database successfully sent, from Django to Raspberry Pi!')

    return render(request, 'camera.html')  # Affichage de la page HTML
