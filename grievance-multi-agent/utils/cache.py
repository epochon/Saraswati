import streamlit as st
import hashlib


def cache_key(text: str) -> str:
    """
    Generates a stable hash for caching based on user input.
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
