"""
Module d'analyse de cohortes pour le tracking de rétention.
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Tuple

import config


@st.cache_data(show_spinner=False)
def build_cohorts(events: pd.DataFrame, freq: str = config.COHORT_DEFAULT_FREQ) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Construit l'analyse de cohortes basée sur la première activité du visiteur.
    
    Args:
        events: DataFrame des événements
        freq: Fréquence ("W" pour semaine, "M" pour mois)
        
    Returns:
        Tuple (cohort_counts, retention_rate)
            - cohort_counts: Nombre d'utilisateurs par cohorte
            - retention_rate: Taux de rétention (%)
    """
    df = events[["visitorid", "timestamp"]].dropna().copy()
    df["period"] = df["timestamp"].dt.to_period(freq).dt.start_time
    
    # Première période du visiteur = sa cohorte
    first_period = df.groupby("visitorid")["period"].min().rename("cohort").reset_index()
    df = df.merge(first_period, on="visitorid", how="left")
    
    # Pivot: index=cohort, columns=period, values=unique_users
    cohort_counts = (
        df.groupby(["cohort", "period"])["visitorid"]
        .nunique()
        .reset_index(name="users")
        .pivot(index="cohort", columns="period", values="users")
        .fillna(0)
        .sort_index()
    )
    
    # Retention = users(t) / users(t0)
    cohort_sizes = cohort_counts.iloc[:, 0]
    retention_rate = cohort_counts.divide(cohort_sizes, axis=0) * 100
    
    return cohort_counts, retention_rate


@st.cache_data(show_spinner=False)
def build_cohort_engagement(events: pd.DataFrame, freq: str = config.COHORT_DEFAULT_FREQ) -> pd.DataFrame:
    """
    Analyse l'engagement (nombre d'événements) par cohorte.
    
    Args:
        events: DataFrame des événements
        freq: Fréquence de cohorte
        
    Returns:
        DataFrame avec engagement par cohorte et période
    """
    df = events[["visitorid", "event", "timestamp"]].dropna().copy()
    df["period"] = df["timestamp"].dt.to_period(freq).dt.start_time
    
    first_period = df.groupby("visitorid")["period"].min().rename("cohort").reset_index()
    df = df.merge(first_period, on="visitorid", how="left")
    
    # Événements par cohorte et période
    engagement = (
        df.groupby(["cohort", "period"])
        .agg(events_count=("event", "count"))
        .reset_index()
        .pivot(index="cohort", columns="period", values="events_count")
        .fillna(0)
        .sort_index()
    )
    
    return engagement


def get_cohort_insights(cohort_counts: pd.DataFrame, retention_rate: pd.DataFrame) -> dict:
    """
    Extrait des insights de l'analyse de cohortes.
    
    Args:
        cohort_counts: Nombre d'utilisateurs par cohorte
        retention_rate: Taux de rétention
        
    Returns:
        Dict avec insights
    """
    return {
        "total_cohorts": len(cohort_counts),
        "users_first_cohort": cohort_counts.iloc[0, 0],
        "users_last_cohort": cohort_counts.iloc[-1, 0],
        "avg_retention_week_2": retention_rate.iloc[:, 1].mean() if retention_rate.shape[1] > 1 else np.nan,
        "avg_retention_week_4": retention_rate.iloc[:, 3].mean() if retention_rate.shape[1] > 3 else np.nan,
    }
