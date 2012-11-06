from livesettings import config_value
from django.conf import settings


def schema():
    schema = {
        'facebook': (
            'SOCIALS_INFO', 'FACEBOOK_URL',
        ),
        'twitter': (
            'SOCIALS_INFO', 'TWITTER_URL',
        ),
        'linkedin': (
            'SOCIALS_INFO', 'LINKEDIN_URL',
        ),
        'skype': (
            'SOCIALS_INFO', 'SKYPE_CONTACT',
        ),
    }

    return schema


def compress_enabled(request):
    return {'COMPRESS_ENABLED': settings.COMPRESS_ENABLED}


def socials(request):
    socials_schema = schema()
    config = {}
    for key in socials_schema.keys():
        config_attribute = socials_schema[key]
        value = config_value(*config_attribute)
        config[key] = value
    return config
