from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field= 'django.db.models.BigAutoField'
    name = 'accounts'

    #ready function is overriden that is used to make signals work in the signals.py file
    def ready(self):
        import accounts.signals
