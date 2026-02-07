import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd

# Initialize Firebase (Ensure you use the same credentials as app.py)
if not firebase_admin._apps:
    cred = credentials.Certificate("credentials.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.set_page_config(page_title="Multi-Agent Complaint Monitor", layout="wide")
st.title("🛰️ Agent-to-Agent (A2A) Consensus Dashboard")

# Function to fetch logs
def get_data():
    docs = db.collection('complaints').order_by('metadata.timestamp', direction=firestore.Query.DESCENDING).limit(10).get()
    return [doc.to_dict() for doc in docs]

data = get_data()

if data:
    for entry in data:
        with st.expander(f"Complaint from {entry.get('phone')} - {entry['metadata']['timestamp'].strftime('%H:%M:%S')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("📝 **Raw Transcript**")
                st.write(entry.get('raw_transcript'))
                
            with col2:
                st.success("🤖 **Consensus Output**")
                st.json(entry.get('consensus_data'))
            
            st.divider()
            st.markdown(f"**Agent interaction:** `{entry['metadata'].get('interaction_log', 'No log available')}`")
else:
    st.write("Waiting for incoming calls...")

# Auto-refresh button
if st.button('🔄 Refresh Logs'):
    st.rerun()