"""
Dashboard E-Commerce - Application Streamlit principale
Analyse data-driven du comportement utilisateurs
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Imports locaux
import config
from data_loader import load_events
from kpis import build_kpi_daily, compute_global_kpis, render_kpi_cards
from cohorts import build_cohorts
from ab_test import simulate_ab_test
from utils import format_int, fmt_pct, safe_divide
from insights import InsightEngine, render_insights_panel


# ========================
# Page Config
# ========================
st.set_page_config(
    page_title=config.STREAMLIT_PAGE_TITLE,
    page_icon=config.STREAMLIT_PAGE_ICON,
    layout=config.STREAMLIT_LAYOUT,
    initial_sidebar_state=config.STREAMLIT_INITIAL_SIDEBAR_STATE,
)

# ========================
# CSS Styling
# ========================
st.markdown(
    """
<style>
html, body, [class*="css"] { 
    font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; 
}
.stApp { 
    background: #000000; 
    color: #FFFFFF; 
}
.block-container { 
    padding-top: 1.2rem; 
    max-width: 1300px; 
}
section[data-testid="stSidebar"] { 
    background: #000000; 
    border-right: 1px solid #e2e8f0; 
}
h1, h2, h3 { 
    color: #0f172a; 
    letter-spacing: -0.02em; 
}
h1 { 
    font-weight: 800; 
    margin-bottom: 0.2rem; 
}
hr { 
    border: none; 
    height: 1px; 
    background: #e2e8f0; 
    margin: 1.2rem 0; 
}

.kpi-grid { 
    display: grid; 
    grid-template-columns: repeat(4, minmax(0, 1fr)); 
    gap: 12px; 
    margin: 0.4rem 0 0.8rem 0; 
}
.kpi-card {
    background: #ffffff; 
    border: 1px solid #e2e8f0; 
    border-radius: 14px;
    padding: 14px 14px 12px 14px; 
    box-shadow: 0 1px 2px rgba(15,23,42,0.05);
}
.kpi-label { 
    font-size: 0.78rem; 
    color: #64748b; 
    font-weight: 700; 
    text-transform: uppercase; 
    letter-spacing: 0.06em; 
}
.kpi-value { 
    font-size: 1.7rem; 
    font-weight: 900; 
    color: #0f172a; 
    margin-top: 6px; 
    line-height: 1.1; 
}
.kpi-sub { 
    font-size: 0.85rem; 
    color: #475569; 
    margin-top: 6px; 
}

div[data-baseweb="tab-list"] { 
    gap: 8px; 
}
button[data-baseweb="tab"] {
    background: #ffffff !important; 
    border: 1px solid #e2e8f0 !important; 
    border-radius: 10px !important;
    padding: 10px 14px !important; 
    font-weight: 800 !important; 
    color: #0f172a !important;
}
button[aria-selected="true"][data-baseweb="tab"] {
    border-color: #0f172a !important; 
    box-shadow: 0 2px 10px rgba(15,23,42,0.08) !important;
}
[data-testid="stDataFrame"] { 
    border: 1px solid #e2e8f0; 
    border-radius: 12px; 
    overflow: hidden; 
}
</style>
""",
    unsafe_allow_html=True,
)

# ========================
# Data Loading
# ========================
st.markdown("# E-Commerce Dashboard")
st.caption("Pages: Overview | Cohortes | A/B Test")

try:
    events = load_events(config.EVENTS_CLEAN_PATH)
except FileNotFoundError as e:
    st.error(f"Erreur: {e}")
    st.info("Assurez-vous que `events_clean.csv` est dans `data/clean/`")
    st.stop()
except Exception as e:
    st.error(f"Erreur lors du chargement: {e}")
    st.stop()

kpi_daily = build_kpi_daily(events)

# ========================
# Sidebar Navigation & Filters
# ========================
st.sidebar.markdown("## Navigation")
page = st.sidebar.radio(
    "Sélectionnez une page",
    ["Overview", "Cohortes", "A/B Test"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("## Filtres")

# Date range filter
min_date = kpi_daily["date"].min().date()
max_date = kpi_daily["date"].max().date()

date_range = st.sidebar.date_input(
    "Période",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Ensure valid date range
if len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
else:
    start_date = pd.to_datetime(date_range[0])
    end_date = start_date + pd.Timedelta(days=1)

# Event type filter
event_types = st.sidebar.multiselect(
    "Types d'événements",
    options=config.FUNNEL_EVENTS,
    default=config.FUNNEL_EVENTS,
)

# Apply filters
events_filtered = events[
    (events["timestamp"] >= start_date)
    & (events["timestamp"] < end_date + pd.Timedelta(days=1))
    & (events["event"].isin(event_types))
].copy()

# ========================
# Page: Overview
# ========================
if page == "Overview":
    st.markdown("### Overview - Vue d'ensemble du site")
    
    # Render KPI cards
    kpis = compute_global_kpis(events_filtered)
    render_kpi_cards(kpis)
    
    # Insights section
    with st.expander("Insights clés (click pour voir)", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Panier moyen",
                format_int(kpis["avg_items_per_visitor"]),
                f"vs visiteurs: {format_int(kpis['unique_visitors'])}"
            )
        
        with col2:
            engagement_rate = safe_divide(kpis["views"], kpis["unique_visitors"])
            st.metric(
                "Engagement (vues/visiteur)",
                f"{engagement_rate:.1f}",
                "Plus élevé = Meilleur engagement"
            )
        
        with col3:
            atc_rate = safe_divide(kpis["addtocart"], kpis["views"])
            if atc_rate < 0.05:
                delta_color = "inverse"
            else:
                delta_color = "off"
            st.metric(
                "Taux d'intention (ATC/Vues)",
                fmt_pct(atc_rate),
                "Benchmark e-commerce: 2-5%",
                delta_color=delta_color
            )
    
    st.divider()
    
    # Intelligent recommendations
    render_insights_panel(events_filtered)
    
    st.divider()
    
    # Tabs for different visualizations
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Tendances", "Funnel", "Horaire", "Top Produits", "Distribution"])
    
    with tab1:
        st.markdown("#### Évolution temporelle des KPIs")
        st.caption("Visualisez l'évolution jour après jour")
        
        daily_filtered = kpi_daily[
            (kpi_daily["date"] >= start_date)
            & (kpi_daily["date"] <= end_date)
        ].copy()
        
        if len(daily_filtered) > 0:
            # KPI selector
            kpi_selector = st.multiselect(
                "Sélectionnez les KPIs à afficher",
                ["Vues", "Ajouts au panier", "Transactions"],
                default=["Vues", "Transactions"]
            )
            
            kpi_map = {
                "Vues": "views",
                "Ajouts au panier": "addtocart",
                "Transactions": "transactions"
            }
            selected_kpis = [kpi_map[k] for k in kpi_selector]
            
            # Events trend
            fig_events = px.line(
                daily_filtered,
                x="date",
                y=selected_kpis,
                markers=True,
                title="Événements par jour",
                labels={"value": "Nombre", "date": "Date", "variable": "Type"},
                color_discrete_map={
                    "views": "#1f77b4",
                    "addtocart": "#ff7f0e",
                    "transactions": "#2ca02c"
                }
            )
            fig_events.update_layout(height=400)
            st.plotly_chart(fig_events, width='stretch')
            
            # Conversion trend
            st.markdown("**Taux de conversion par jour**")
            fig_conv = px.area(
                daily_filtered,
                x="date",
                y=["conv_view_to_atc", "conv_atc_to_trx", "conv_view_to_trx"],
                markers=False,
                title=None,
                labels={"value": "Taux", "date": "Date", "variable": "Conversion"}
            )
            fig_conv.update_traces(opacity=0.7)
            fig_conv.update_yaxes(tickformat=".1%")
            fig_conv.update_layout(height=300)
            st.plotly_chart(fig_conv, width='stretch')
            
            # Summary stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Moyenne vues/jour", f"{daily_filtered['views'].mean():.0f}", f"({daily_filtered['views'].std():.0f} écart-type)")
            with col2:
                st.metric("Moyenne conversions/jour", f"{daily_filtered['transactions'].mean():.0f}")
            with col3:
                st.metric("Meilleur jour (vues)", f"{daily_filtered['views'].max():.0f}")
            with col4:
                st.metric("Taux conversion moyen", fmt_pct(daily_filtered['conv_view_to_trx'].mean()))
            
            # Download button
            csv = daily_filtered.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Télécharger KPI quotidiens (CSV)",
                data=csv,
                file_name="kpi_daily.csv",
                mime="text/csv",
            )
        else:
            st.info("Aucune donnée pour la période sélectionnée")
    
    with tab2:
        st.markdown("#### Funnel de conversion - Répartition des étapes")
        st.caption("Identifiez où vous perdez les clients")
        
        views = int(events_filtered["is_view"].sum())
        addtocart = int(events_filtered["is_addtocart"].sum())
        transactions = int(events_filtered["is_transaction"].sum())
        
        funnel_data = pd.DataFrame({
            "Étape": ["Vues", "Ajouts Panier", "Transactions"],
            "Nombre": [views, addtocart, transactions]
        })
        
        # Calculate drop rates
        funnel_data["Drop Rate"] = [
            0,
            safe_divide(views - addtocart, views) * 100,
            safe_divide(addtocart - transactions, addtocart) * 100
        ]
        
        fig_funnel = px.funnel(
            funnel_data,
            x="Nombre",
            y="Étape",
            title=None,
            color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c"]
        )
        fig_funnel.update_layout(height=400)
        st.plotly_chart(fig_funnel, width='stretch')
        
        # Detailed breakdown
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Vue → Panier", fmt_pct(safe_divide(addtocart, views)), "Taux d'intention")
        with col2:
            st.metric("Panier → Transaction", fmt_pct(safe_divide(transactions, addtocart)), "Checkout completion")
        with col3:
            st.metric("Vue → Transaction", fmt_pct(safe_divide(transactions, views)), "Conversion globale")
        
        st.dataframe(funnel_data, width='stretch', hide_index=True)
        
        # Recommendations
        recommendations = []
        if safe_divide(addtocart, views) < 0.02:
            recommendations.append("Ameliorer l'intention: Moins de 2% des vues ajoutent au panier")
        if safe_divide(transactions, addtocart) < 0.10:
            recommendations.append("Reduire la friction checkout: Moins de 10% des paniers se convertissent")
        
        if recommendations:
            st.info("\n\n".join(recommendations))
    
    with tab3:
        st.markdown("#### Analyse horaire - Patterns temporels")
        st.caption("Quand les clients sont-ils actifs?")
        
        if "hour" in events_filtered.columns:
            hourly = events_filtered.groupby("hour").agg({
                "is_view": "sum",
                "is_addtocart": "sum",
                "is_transaction": "sum",
                "visitorid": "nunique"
            }).reset_index()
            hourly["conv_view_to_trx"] = safe_divide(hourly["is_transaction"], hourly["is_view"])
            hourly["engagement"] = safe_divide(hourly["is_view"], hourly["visitorid"])
            
            # Events by hour
            fig_hourly = px.line(
                hourly,
                x="hour",
                y=["is_view", "is_addtocart", "is_transaction"],
                markers=True,
                title="Événements par heure",
                labels={"value": "Nombre", "hour": "Heure", "variable": "Type"},
                color_discrete_map={
                    "is_view": "#1f77b4",
                    "is_addtocart": "#ff7f0e",
                    "is_transaction": "#2ca02c"
                }
            )
            fig_hourly.update_layout(height=400)
            st.plotly_chart(fig_hourly, width='stretch')
            
            # Best hours for conversion
            best_hour = hourly.loc[hourly["conv_view_to_trx"].idxmax()]
            worst_hour = hourly.loc[hourly["conv_view_to_trx"].idxmin()]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Meilleure heure (conversion)",
                    f"{int(best_hour['hour'])}:00",
                    f"{fmt_pct(best_hour['conv_view_to_trx'])} de conversion"
                )
            with col2:
                st.metric(
                    "Heure de pointe",
                    f"{hourly.loc[hourly['is_view'].idxmax(), 'hour']:.0f}:00",
                    f"{hourly['is_view'].max():.0f} vues"
                )
            with col3:
                st.metric(
                    "Heures creuses",
                    f"{hourly.loc[hourly['is_view'].idxmin(), 'hour']:.0f}:00",
                    f"{hourly['is_view'].min():.0f} vues"
                )
        else:
            st.warning("Colonne 'hour' non trouvée dans les données")
    
    with tab4:
        st.markdown("#### Top produits - Quels articles performent?")
        st.caption("Analysez les produits qui génèrent le plus de revenus")
        
        n_items = st.slider("Nombre de produits à afficher", 5, 50, 20)
        
        top_items = (
            events_filtered.groupby("itemid")
            .agg({
                "is_view": "sum",
                "is_addtocart": "sum",
                "is_transaction": "sum",
                "visitorid": "nunique"
            })
            .reset_index()
            .sort_values("is_transaction", ascending=False)
            .head(n_items)
        )
        top_items["conv_view_to_trx"] = safe_divide(top_items["is_transaction"], top_items["is_view"])
        top_items.columns = ["Item ID", "Vues", "Panier", "Transactions", "Clients", "Conv %"]
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Produit #1", f"Item {top_items.iloc[0]['Item ID']:.0f}", f"{top_items.iloc[0]['Transactions']:.0f} ventes")
        with col2:
            st.metric("Ventes moyennes (top 20)", f"{top_items['Transactions'].mean():.1f}")
        with col3:
            st.metric("Concentration", f"{top_items.iloc[0]['Transactions'] / top_items['Transactions'].sum() * 100:.1f}%", "Top 1 vs total")
        
        # Visualizations
        fig_top = px.bar(
            top_items.head(10),
            y="Item ID",
            x=["Vues", "Panier", "Transactions"],
            orientation="h",
            barmode="group",
            title=f"Top {min(10, n_items)} produits par transactions",
            labels={"value": "Nombre"}
        )
        fig_top.update_layout(height=400)
        st.plotly_chart(fig_top, width='stretch')
        
        st.dataframe(top_items.head(20), width='stretch', hide_index=True)
        
        csv = top_items.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Télécharger Top produits (CSV)",
            data=csv,
            file_name="top_items.csv",
            mime="text/csv",
        )
    
    with tab5:
        st.markdown("#### Distribution des comportements")
        st.caption("Comprenez la variabilité des données")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Views per visitor
            views_per_visitor = events_filtered.groupby("visitorid")["is_view"].sum()
            fig_views = px.histogram(
                views_per_visitor,
                nbins=50,
                title="Distribution: Vues par visiteur",
                labels={"value": "Nombre de vues", "count": "Nombre de visiteurs"},
                color_discrete_sequence=["#1f77b4"]
            )
            fig_views.update_layout(height=350)
            st.plotly_chart(fig_views, width='stretch')
        
        with col2:
            # Items per transaction
            trx_data = events_filtered[events_filtered["event"] == "transaction"]
            if len(trx_data) > 0:
                items_per_trx = trx_data.groupby("visitorid").size()
                fig_items = px.histogram(
                    items_per_trx,
                    nbins=30,
                    title="Distribution: Items par transaction",
                    labels={"value": "Nombre d'items", "count": "Nombre de transactions"},
                    color_discrete_sequence=["#2ca02c"]
                )
                fig_items.update_layout(height=350)
                st.plotly_chart(fig_items, width='stretch')

# ========================
# Page: Cohortes
# ========================
elif page == "Cohortes":
    st.markdown("### Analyse de Cohortes - Rétention utilisateurs")
    st.caption("Analysez comment les utilisateurs reviennent à travers le temps")
    
    freq = st.radio("Granularité", ["Semaine", "Mois"], horizontal=True)
    freq_code = "W" if freq == "Semaine" else "M"
    
    try:
        cohort_counts, retention_rate = build_cohorts(events_filtered, freq=freq_code)
        
        if cohort_counts.empty:
            st.warning("Données insuffisantes pour construire les cohortes")
        else:
            # Key metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Nombre de cohortes", len(retention_rate))
            with col2:
                st.metric("Rétention J+7 (moyenne)", f"{retention_rate.iloc[:, min(1, retention_rate.shape[1]-1)].mean():.1%}")
            with col3:
                st.metric("Rétention à long terme", f"{retention_rate.iloc[:, -1].mean():.1%}", "Dernière période")
            
            st.divider()
            
            # Limit periods for readability
            max_periods = st.slider("Nombre de périodes affichées", 4, 20, 12)
            retention_limited = retention_rate.iloc[:, :max_periods]
            
            # Heatmap
            fig_heatmap = px.imshow(
                retention_limited,
                aspect="auto",
                labels={"x": "Période", "y": "Cohorte", "color": "Rétention (%)"},
                title="Matrice de rétention - Plus sombre = Meilleure rétention",
                color_continuous_scale="Greens"
            )
            fig_heatmap.update_layout(height=600)
            st.plotly_chart(fig_heatmap, width='stretch')
            
            # Cohort sizes
            st.markdown("#### Taille et santé des cohortes")
            cohort_sizes = cohort_counts.iloc[:, 0]
            fig_sizes = px.bar(
                x=cohort_sizes.index.astype(str),
                y=cohort_sizes.values,
                labels={"x": "Cohorte", "y": "Utilisateurs"},
                title="Utilisateurs par cohorte (première période)",
                color_discrete_sequence=["#1f77b4"]
            )
            fig_sizes.update_layout(height=350)
            st.plotly_chart(fig_sizes, width='stretch')
            
            # Insights
            latest_cohort = retention_rate.index[-1]
            latest_retention = retention_rate.iloc[-1, min(1, retention_rate.shape[1]-1)]
            st.info(f"**Cohorte la plus récente ({latest_cohort}):** {latest_retention:.1%} de rétention")
    
    except Exception as e:
        st.error(f"Erreur lors de l'analyse de cohortes: {e}")

# ========================
# Page: A/B Test
# ========================
else:
    st.markdown("### Simulation A/B Test - Test statistique rigoureux")
    st.caption("Déterminez si votre variante B performe vraiment mieux que la variante A")
    
    with st.expander("Comment ca marche?", expanded=False):
        st.write("""
        **A/B Test expliqué:**
        - **Groupe A (Contrôle):** Version actuelle de votre site
        - **Groupe B (Variante):** Nouvelle version avec changements
        - **Uplift:** Amélioration attendue (ex: +10% = 10% meilleure conversion)
        - **P-value:** Probabilité que la différence soit due au hasard
        - **Résultat significatif:** P-value < 0.05 = Résultat fiable
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        baseline = st.selectbox(
            "KPI cible",
            options=["view_to_transaction", "addtocart_to_transaction"],
            format_func=lambda x: "Vue → Transaction" if x == "view_to_transaction" else "Panier → Transaction",
        )
    
    with col2:
        uplift = st.slider(
            "Uplift relatif attendu (B vs A)",
            min_value=0.0,
            max_value=0.50,
            value=0.10,
            step=0.01,
            format="%.1f%%"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        seed = st.number_input("Seed (reproductibilité)", min_value=0, value=42, step=1)
    with col2:
        significance_level = config.SIGNIFICANCE_LEVEL
        st.metric("Seuil de significativité", f"{significance_level:.2%}", "Standard industriel")
    
    try:
        results = simulate_ab_test(
            events_filtered,
            baseline=baseline,
            uplift=float(uplift),
            seed=int(seed)
        )
        
        # KPI cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Groupe A (n)", format_int(results['group_a_size']))
        
        with col2:
            st.metric("Groupe B (n)", format_int(results['group_b_size']))
        
        with col3:
            st.metric("Conv. A", fmt_pct(results["conversion_a"]), "Baseline")
        
        with col4:
            st.metric("Conv. B", fmt_pct(results["conversion_b"]), "Variante")
        
        st.divider()
        
        # Visualization
        ab_data = pd.DataFrame({
            "Groupe": ["A (Contrôle)", "B (Variante)"],
            "Conversion": [results["conversion_a"], results["conversion_b"]],
            "Couleur": ["#1f77b4", "#2ca02c"]
        })
        
        fig_ab = px.bar(
            ab_data,
            x="Groupe",
            y="Conversion",
            title="Comparaison des taux de conversion",
            color="Couleur",
            color_discrete_map={"#1f77b4": "#1f77b4", "#2ca02c": "#2ca02c"}
        )
        fig_ab.update_yaxes(tickformat=".2%")
        fig_ab.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_ab, width='stretch')
        
        # Statistical results
        st.markdown("#### Résultats statistiques")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Z-statistic", f"{results['z_statistic']:.3f}", "Écart type (sigma)")
        with col2:
            st.metric("P-value", f"{results['p_value']:.6f}", "Probabilité hasard")
        with col3:
            uplift_rel = ((results["conversion_b"] - results["conversion_a"]) / results["conversion_a"] * 100) if results["conversion_a"] > 0 else 0
            st.metric("Uplift observé", f"{uplift_rel:.2f}%", f"vs {uplift*100:.2f}% attendu")
        with col4:
            power = max(0, 1 - results['p_value'] * 100)  # Simplified power calculation
            st.metric("Puissance du test", f"{min(99, power):.0f}%", "Capacité à détecter")
        
        st.divider()
        
        # Interpretation with recommendations
        if results["is_significant"]:
            st.success(f"Resultat SIGNIFICATIF (p = {results['p_value']:.4f} < {config.SIGNIFICANCE_LEVEL:.2%})")
            st.write("""
            La variante B performe **significativement mieux** que la variante A.
            
            **Recommandations:**
            - Déployez la variante B en production
            - Continuez à monitorer les performances
            - Testez d'autres hypothèses
            """)
        else:
            st.info(f"Resultat NON SIGNIFICATIF (p = {results['p_value']:.4f} >= {config.SIGNIFICANCE_LEVEL:.2%})")
            st.write(f"""
            La différence observée n'est **pas suffisamment probante** pour affirmer que B est meilleur.
            
            **Actions possibles:**
            - Augmenter la taille d'échantillon (besoin ~{max(1000, results['group_a_size']*2)} observations)
            - Laisser le test tourner plus longtemps
            - Réévaluer la variante B
            - Tester une hypothèse différente
            """)
        
        st.divider()
        
        # Confidence interval
        st.markdown("#### Intervalle de confiance")
        margin_of_error = 1.96 * np.sqrt(results["conversion_a"] * (1 - results["conversion_a"]) / results['group_a_size'])
        ci_lower = max(0, results["conversion_a"] - margin_of_error)
        ci_upper = min(1, results["conversion_a"] + margin_of_error)
        
        st.write(f"""
        **Groupe A:** {fmt_pct(results["conversion_a"])} ± {fmt_pct(margin_of_error)} 
        (IC 95%: [{fmt_pct(ci_lower)}, {fmt_pct(ci_upper)}])
        """)
    
    except Exception as e:
        st.error(f"Erreur lors de la simulation: {e}")

# ========================
# Footer
# ========================
st.markdown("---")
st.caption(f"Mise à jour: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
