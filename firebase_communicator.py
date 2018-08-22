"""Used to configure and setup firebase databases given a database URL."""
import pyrebase

def configure_firebase(url=None):
    """Returns a firebase database instance based on a database URL.

    If no URL is given, the default URL is used."""
    # 'main' + 'server' are shortcuts for the main and server database,
    # respectively. This allows the main or server database to be easily
    # hot-swapped without needing to change the URL in multiple files.
    if url is None or url == 'main':
        url = 'scouting-2018-houston'
    elif url == 'server':
        url = 'server-2018-3209b'
    config = {
        'apiKey': 'mykey',
        'authDomain': url + '.firebaseapp.com',
        'databaseURL': 'https://' + url + '.firebaseio.com/',
        'storageBucket': url + '.appspot.com',
    }
    firebase = pyrebase.initialize_app(config)
    return firebase.database()
