from django.apps import AppConfig
from django.db.models.signals import post_migrate

from scripts.communication import communication_manager as manager


class CommunicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gui.communication'

    def ready(self):
        post_migrate.connect(__load_available_language_models__, sender=self)


def __load_available_language_models__(sender, **kwargs):
    from .models import LanguageModel
    from .models import Property

    man = manager.CommunicatorManager()

    # load/update communicators on startup
    communicators = man.get_implementations()

    for com in communicators:
        if not LanguageModel.objects.filter(name=com.name).exists():
            new_llm = LanguageModel(name=com.name)
            new_llm.save()
            new_llm = LanguageModel.objects.filter(name=com.name)[0]

            for prop in com.properties:
                new_llm_prop = Property(name=prop.name, type=prop.type, mandatory=prop.mandatory,
                                        language_model=new_llm, default=str(prop.default),
                                        is_configuration=prop.configuration)
                new_llm_prop.save()
        else:
            existing_llm = LanguageModel.objects.filter(name=com.name)[0]

            for prop in com.properties:
                if Property.objects.filter(name=prop.name, language_model__name=existing_llm.name).exists():
                    existing_llm_prop = Property.objects.filter(name=prop.name,
                                                                language_model__name=existing_llm.name,
                                                                default=str(prop.default),
                                                                is_configuration=prop.configuration)[0]
                    existing_llm_prop.type = prop.type
                    existing_llm_prop.mandatory = prop.mandatory
                    existing_llm_prop.save()
                else:
                    new_llm_prop = Property(name=prop.name, type=prop.type, mandatory=prop.mandatory,
                                            language_model=existing_llm)
                    new_llm_prop.save()
