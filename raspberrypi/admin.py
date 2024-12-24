from django.contrib import admin
from .models import Capteurs, FaceRecognition

@admin.register(Capteurs)
class CapteursAdmin(admin.ModelAdmin):
    list_display = ('temperature', 'gas_detected', 'timestamp')
    list_filter = ('gas_detected',)
    search_fields = ('temperature',)

@admin.register(FaceRecognition)
class FaceRecognitionAdmin(admin.ModelAdmin):
    list_display = ('face_recognition_identity', 'timestamp')
    search_fields = ('face_recognition_identity',)
