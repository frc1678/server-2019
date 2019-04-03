"""Used to configure and setup firebase databases given a database URL."""
# External imports
import pyrebase
# No internal imports

URL = 'scouting-2019-avr-cacf9'

def configure_firebase(url=None):
    """Returns a firebase database instance based on a database URL.

    If no URL is given, the default URL is used."""
    if url is None:
        url = URL
    config = {
        'apiKey': 'mykey',
        'authDomain': f'{url}.firebaseapp.com',
        'databaseURL': f'https://{url}.firebaseio.com/',
        'storageBucket': f'{url}.appspot.com',
    }
    firebase = pyrebase.initialize_app(config)
    return firebase.database()
