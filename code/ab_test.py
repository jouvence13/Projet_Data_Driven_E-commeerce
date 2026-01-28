"""
Module de tests A/B et statistiques.
"""

import numpy as np
import pandas as pd
import streamlit as st
from typing import Tuple, Dict
from math import erf, sqrt

import config


def normal_cdf(x: float) -> float:
    """
    Fonction de répartition normale standard (approximation).
    
    Args:
        x: Valeur
        
    Returns:
        P(X <= x) pour X ~ N(0,1)
    """
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def z_test_proportions(success_a: int, n_a: int, success_b: int, n_b: int) -> Tuple[float, float]:
    """
    Z-test pour deux proportions indépendantes.
    
    Args:
        success_a: Nombre de succès dans le groupe A
        n_a: Taille du groupe A
        success_b: Nombre de succès dans le groupe B
        n_b: Taille du groupe B
        
    Returns:
        Tuple (z_statistic, p_value)
    """
    if n_a == 0 or n_b == 0:
        return np.nan, np.nan
    
    p_a = success_a / n_a
    p_b = success_b / n_b
    p_pool = (success_a + success_b) / (n_a + n_b)
    
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    if se == 0:
        return np.nan, np.nan
    
    z = (p_b - p_a) / se
    p_value = 2 * (1 - normal_cdf(abs(z)))
    
    return float(z), float(p_value)


@st.cache_data(show_spinner=False)
def simulate_ab_test(
    events_period: pd.DataFrame,
    baseline: str = "view_to_transaction",
    uplift: float = config.AB_TEST_DEFAULT_UPLIFT,
    seed: int = config.AB_TEST_SEED,
) -> Dict:
    """
    Simule un A/B test à partir des données réelles.
    
    Args:
        events_period: DataFrame filtré sur la période
        baseline: Métrique de base ("view_to_transaction" ou "addtocart_to_transaction")
        uplift: Uplift en pourcentage (ex: 0.10 = +10%)
        seed: Seed pour la reproductibilité
        
    Returns:
        Dict avec résultats du test
    """
    np.random.seed(seed)
    
    # Split 50/50
    unique_visitors = events_period["visitorid"].unique()
    np.random.shuffle(unique_visitors)
    split = len(unique_visitors) // 2
    
    visitors_a = set(unique_visitors[:split])
    visitors_b = set(unique_visitors[split:])
    
    events_a = events_period[events_period["visitorid"].isin(visitors_a)]
    events_b = events_period[events_period["visitorid"].isin(visitors_b)]
    
    # Calcul de la métrique de base
    if baseline == "view_to_transaction":
        views_a = events_a["is_view"].sum()
        transactions_a = events_a["is_transaction"].sum()
        
        views_b = events_b["is_view"].sum()
        transactions_b_baseline = events_b["is_transaction"].sum()
        transactions_b = int(transactions_b_baseline * (1 + uplift))
    
    elif baseline == "addtocart_to_transaction":
        atc_a = events_a["is_addtocart"].sum()
        transactions_a = events_a["is_transaction"].sum()
        
        atc_b = events_b["is_addtocart"].sum()
        transactions_b_baseline = events_b["is_transaction"].sum()
        transactions_b = int(transactions_b_baseline * (1 + uplift))
    
    else:
        raise ValueError(f"Baseline inconnue: {baseline}")
    
    # Z-test
    z_stat, p_value = z_test_proportions(
        transactions_a, events_a["visitorid"].nunique(),
        transactions_b, events_b["visitorid"].nunique()
    )
    
    is_significant = p_value < config.SIGNIFICANCE_LEVEL if not np.isnan(p_value) else False
    
    conv_a = transactions_a / events_a["visitorid"].nunique() if len(events_a) > 0 else 0
    conv_b = transactions_b / events_b["visitorid"].nunique() if len(events_b) > 0 else 0
    
    return {
        "group_a_size": events_a["visitorid"].nunique(),
        "group_b_size": events_b["visitorid"].nunique(),
        "conversion_a": conv_a,
        "conversion_b": conv_b / (1 + uplift),  # Normaliser pour afficher
        "transactions_a": int(transactions_a),
        "transactions_b": transactions_b,
        "z_statistic": z_stat,
        "p_value": p_value,
        "is_significant": is_significant,
        "uplift_observed": (conv_b - conv_a) / conv_a if conv_a > 0 else 0,
        "uplift_simulated": uplift,
    }
