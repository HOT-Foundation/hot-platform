from conf import settings
from raven import Client

client = None
if settings['SENTRY_ENDPOINT']:
    client = Client(settings['SENTRY_ENDPOINT'])

def capture_exception():
    if client:
        client.captureException()
