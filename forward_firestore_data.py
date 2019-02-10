#!/usr/bin/python3.7
"""Forwards Firebase Cloud Firestore data to Firebase Realtime Database.

The web-based pit scout uses Cloud Firestore, while the viewers use
Realtime Database.  This script takes pit scout data and uploads it to
the Realtime Database.  Periodically called by server.py."""
# No external imports
# Internal imports
import firebase_communicator
import firestore_communicator

REALTIME_DB = firebase_communicator.configure_firebase()
FIRESTORE_DB = firestore_communicator.configure_cloud_firestore()

TEAMS = FIRESTORE_DB.collection('Teams').get()

FINAL_DATA = {}
for team in TEAMS:
    # 'team.id' is the document name (e.g. 1678)
    for key, value in team.to_dict().items():
        FINAL_DATA[f'Teams/{team.id}/{key}'] = value

# Multi-location update (sends data all at once)
REALTIME_DB.update(FINAL_DATA)
