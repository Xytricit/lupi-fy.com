from django.apps import AppConfig

class MainConfig(AppConfig):  # rename the class if you want
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'  # <-- make sure this matches your app folder name
