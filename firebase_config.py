
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore


@st.cache_resource
def initialize_firebase():
    if not firebase_admin._apps:
        firebase_credentials = dict(
            st.secrets["firebase_service_account"]
        )

        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred)

    return firebase_admin.get_app()


firebase_app = initialize_firebase()
db = firestore.client(firebase_app)
