"""
Calcul des KPIs e-commerce.
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict

import config
from utils import safe_divide, fmt_pct, format_int


@st.cache_data(show_spinner=False)
def build_kpi_daily(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construit les KPIs journaliers.
    
    Args:
        df: DataFrame des événements
        
    Returns:
        DataFrame avec KPIs par date
    """
    kpi = df.groupby("date").agg(
        total_events=("event", "count"),
        views=("is_view", "sum"),
        addtocart=("is_addtocart", "sum"),
        transactions=("is_transaction", "sum"),
        unique_visitors=("visitorid", "nunique"),
    ).reset_index()
    
    kpi["date"] = pd.to_datetime(kpi["date"], errors="coerce").dt.normalize()
    
    # Conversions
    kpi["conv_view_to_atc"] = safe_divide(kpi["addtocart"], kpi["views"])
    kpi["conv_atc_to_trx"] = safe_divide(kpi["transactions"], kpi["addtocart"])
    kpi["conv_view_to_trx"] = safe_divide(kpi["transactions"], kpi["views"])
    
    return kpi


@st.cache_data(show_spinner=False)
def compute_global_kpis(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calcule les KPIs globaux.
    
    Args:
        df: DataFrame des événements
        
    Returns:
        Dict avec les KPIs
    """
    views = int(df["is_view"].sum())
    atc = int(df["is_addtocart"].sum())
    trx = int(df["is_transaction"].sum())
    
    unique_visitors = df["visitorid"].nunique()
    buyers = df.loc[df["event"] == config.EVENT_TRANSACTION, "visitorid"].nunique() if trx > 0 else 0
    unique_items = df["itemid"].nunique()
    
    return {
        "total_events": len(df),
        "unique_visitors": unique_visitors,
        "unique_items": unique_items,
        "views": views,
        "addtocart": atc,
        "transactions": trx,
        "conv_view_to_atc": safe_divide(atc, views),
        "conv_atc_to_trx": safe_divide(trx, atc),
        "conv_view_to_trx": safe_divide(trx, views),
        "buyers": buyers,
        "buyer_rate": safe_divide(buyers, unique_visitors),
        "avg_items_per_visitor": safe_divide(unique_items, unique_visitors),
    }


def render_kpi_cards(kpis: Dict[str, float]) -> None:
    """
    Affiche les KPIs sous forme de cartes.
    
    Args:
        kpis: Dict des KPIs
    """
    import streamlit as st
    
    st.markdown(
        f"""
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-label">Visiteurs uniques</div>
    <div class="kpi-value">{format_int(kpis["unique_visitors"])}</div>
    <div class="kpi-sub">Acheteurs: {format_int(kpis["buyers"])} ({fmt_pct(kpis["buyer_rate"])})</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Transactions</div>
    <div class="kpi-value">{format_int(kpis["transactions"])}</div>
    <div class="kpi-sub">Conversion vue→achat: {fmt_pct(kpis["conv_view_to_trx"])}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Vues</div>
    <div class="kpi-value">{format_int(kpis["views"])}</div>
    <div class="kpi-sub">Vue→Panier: {fmt_pct(kpis["conv_view_to_atc"])}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Ajouts panier</div>
    <div class="kpi-value">{format_int(kpis["addtocart"])}</div>
    <div class="kpi-sub">Panier→Achat: {fmt_pct(kpis["conv_atc_to_trx"])}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
