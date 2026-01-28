"""
Générateur d'insights automatiques pour le dashboard.
Fournit des recommandations basées sur les données.
"""

from typing import Dict, List, Tuple
import pandas as pd
from utils import safe_divide


class InsightEngine:
    """Moteur d'insights pour générer des recommandations automatiques."""
    
    ALERT_THRESHOLD_ATC_RATE = 0.02  # 2% - Taux d'intention (ATC/Views)
    ALERT_THRESHOLD_CONVERSION = 0.01  # 1% - Conversion globale
    ALERT_THRESHOLD_CHECKOUT_COMPLETION = 0.10  # 10% - Panier→Achat
    
    @staticmethod
    def analyze_funnel(events: pd.DataFrame) -> List[str]:
        """
        Analyse le funnel de conversion et génère des insights.
        
        Args:
            events: DataFrame des événements
            
        Returns:
            Liste des insights/alertes
        """
        insights = []
        
        views = int(events["is_view"].sum())
        atc = int(events["is_addtocart"].sum())
        trx = int(events["is_transaction"].sum())
        
        atc_rate = safe_divide(atc, views)
        checkout_completion = safe_divide(trx, atc)
        conversion = safe_divide(trx, views)
        
        # Alertes sur l'intention
        if atc_rate < InsightEngine.ALERT_THRESHOLD_ATC_RATE:
            insights.append(
                f"ALERTE: Faible taux d'intention ({atc_rate:.2%})\n"
                "Moins de 2% des vues genèrent un ajout au panier.\n"
                "Actions: Améliorer les fiches produits, ajouter avis clients, réduire friction"
            )
        elif atc_rate > 0.10:
            insights.append(
                f"Excellent taux d'intention ({atc_rate:.2%})\n"
                "Vos produits et présentation convertissent bien en intention d'achat."
            )
        
        # Alertes sur le checkout
        if atc > 0 and checkout_completion < InsightEngine.ALERT_THRESHOLD_CHECKOUT_COMPLETION:
            insights.append(
                f"ALERTE: Friction au checkout ({checkout_completion:.2%} conversion panier)\n"
                "Moins de 10% des paniers se convertissent.\n"
                "Actions: Réduire étapes checkout, offrir guest checkout, afficher sécurité"
            )
        
        # Conversion globale
        if conversion < InsightEngine.ALERT_THRESHOLD_CONVERSION:
            insights.append(
                f"ALERTE: Très faible conversion globale ({conversion:.2%})\n"
                "Le site ne convertit qu'1% des vues en achats.\n"
                "Actions: Audit UX complet, test A/B landing pages, retargeting"
            )
        
        return insights
    
    @staticmethod
    def analyze_hourly_patterns(events: pd.DataFrame) -> Dict[str, any]:
        """
        Analyse les patterns horaires.
        
        Args:
            events: DataFrame des événements
            
        Returns:
            Dict avec insights sur les patterns
        """
        if "hour" not in events.columns:
            return {}
        
        hourly = events.groupby("hour").agg({
            "is_view": "sum",
            "is_transaction": "sum",
            "visitorid": "nunique"
        }).reset_index()
        
        hourly["conv"] = safe_divide(hourly["is_transaction"], hourly["is_view"])
        
        peak_hour = hourly.loc[hourly["is_view"].idxmax()]
        best_conv_hour = hourly.loc[hourly["conv"].idxmax()]
        worst_hour = hourly.loc[hourly["is_view"].idxmin()]
        
        return {
            "peak_hour": int(peak_hour["hour"]),
            "peak_volume": int(peak_hour["is_view"]),
            "best_conversion_hour": int(best_conv_hour["hour"]),
            "best_conversion": float(best_conv_hour["conv"]),
            "slow_hour": int(worst_hour["hour"]),
            "slow_volume": int(worst_hour["is_view"])
        }
    
    @staticmethod
    def analyze_products(events: pd.DataFrame, top_n: int = 5) -> Dict[str, any]:
        """
        Analyse les performances des produits.
        
        Args:
            events: DataFrame des événements
            top_n: Nombre de produits à analyser
            
        Returns:
            Dict avec insights produits
        """
        top_items = (
            events.groupby("itemid")
            .agg({
                "is_view": "sum",
                "is_transaction": "sum",
                "visitorid": "nunique"
            })
            .reset_index()
            .sort_values("is_transaction", ascending=False)
            .head(top_n)
        )
        
        if len(top_items) == 0:
            return {}
        
        total_transactions = events["is_transaction"].sum()
        concentration = safe_divide(top_items["is_transaction"].sum(), total_transactions)
        
        return {
            "top_product": int(top_items.iloc[0]["itemid"]),
            "top_product_sales": int(top_items.iloc[0]["is_transaction"]),
            "top_n_concentration": float(concentration),
            "avg_sales_top_n": float(top_items["is_transaction"].mean()),
            "diversity_warning": concentration > 0.3  # Si top 5 > 30%
        }
    
    @staticmethod
    def get_recommendations(events: pd.DataFrame) -> List[str]:
        """
        Génère une liste de recommandations prioritaires.
        
        Args:
            events: DataFrame des événements
            
        Returns:
            Liste de recommandations
        """
        recommendations = []
        
        # Funnel analysis
        funnel_insights = InsightEngine.analyze_funnel(events)
        recommendations.extend(funnel_insights)
        
        # Product concentration
        product_analysis = InsightEngine.analyze_products(events, top_n=5)
        if product_analysis.get("diversity_warning"):
            concentration = product_analysis["top_n_concentration"]
            recommendations.append(
                f"Portfolio concentré ({concentration:.1%} des ventes dans top 5)\n"
                "Opportunité: Promouvoir les produits moins vendus pour diversifier"
            )
        
        # Hourly patterns
        hourly_analysis = InsightEngine.analyze_hourly_patterns(events)
        if hourly_analysis:
            peak = hourly_analysis["peak_hour"]
            slow = hourly_analysis["slow_hour"]
            recommendations.append(
                f"Pattern temporel detecté\n"
                f"Pic: {peak}h00 | Creux: {slow}h00\n"
                "Opportunité: Ajuster staffing, promotions hors-peak"
            )
        
        return recommendations[:3]  # Top 3 recommandations


def render_insights_panel(events: pd.DataFrame) -> None:
    """
    Affiche un panneau d'insights dans Streamlit.
    
    Args:
        events: DataFrame des événements
    """
    import streamlit as st
    
    recommendations = InsightEngine.get_recommendations(events)
    
    if recommendations:
        st.markdown("### Recommandations intelligentes")
        for i, rec in enumerate(recommendations, 1):
            st.write(f"**{i}.** {rec}")
    else:
        st.info("Pas de recommandations à ce stade - Vos performances sont stables")
