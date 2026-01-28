"""
Module de chargement et prétraitement des données.
"""

import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path
from typing import Optional

import config
from utils import validate_dataframe


@st.cache_data(show_spinner=False)
def load_events(path: Path = config.EVENTS_CLEAN_PATH) -> pd.DataFrame:
    """
    Charge le fichier des événements nettoyés.
    
    Args:
        path: Chemin vers le fichier events_clean.csv
        
    Returns:
        DataFrame avec les événements
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
    """
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable: {path}")
    
    df = pd.read_csv(path, low_memory=False)
    
    # Validation des colonnes essentielles
    required_cols = ["event", "visitorid", "itemid", "timestamp"]
    validate_dataframe(df, required_cols)
    
    # Conversion du timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    
    # Ajout des features temporelles si manquantes
    if "date" not in df.columns:
        df["date"] = df["timestamp"].dt.date
    if "hour" not in df.columns:
        df["hour"] = df["timestamp"].dt.hour
    if "day_of_week" not in df.columns:
        df["day_of_week"] = df["timestamp"].dt.day_name()
    
    # Ajout des indicateurs funnel
    if "is_view" not in df.columns:
        df["is_view"] = (df["event"] == config.EVENT_VIEW).astype(int)
    if "is_addtocart" not in df.columns:
        df["is_addtocart"] = (df["event"] == config.EVENT_ADDTOCART).astype(int)
    if "is_transaction" not in df.columns:
        df["is_transaction"] = (df["event"] == config.EVENT_TRANSACTION).astype(int)
    
    return df


def preprocess_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prétraite les données d'événements.
    
    Args:
        df: DataFrame brut
        
    Returns:
        DataFrame prétraité
    """
    df = df.copy()
    
    # Nettoyage
    df = df.dropna(subset=["itemid", "visitorid"])
    df["itemid"] = df["itemid"].astype(int)
    df["visitorid"] = df["visitorid"].astype(int)
    
    # Conversion timestamp si nécessaire
    if df["timestamp"].dtype == "int64":
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit=config.TIMESTAMP_UNIT)
    elif not isinstance(df["timestamp"].dtype, type(pd.Timestamp)):
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    
    return df
