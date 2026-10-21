import firebase_admin
from firebase_admin import credentials
import streamlit as st

@st.cache_resource
def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(
            "serviceAccountKey.json"
        )
        firebase_admin.initialize_app(cred)

    return firebase_admin.get_app()

firebase_app = initialize_firebase()