"""
Dashboard E-Commerce (Streamlit) — White UI + Pages (Overview / Cohortes / A-B Test)
Source: data/clean/events_clean.csv
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------
# Minimal white UI (no stickers)
# ----------------------------
st.markdown(
    """
<style>
html, body, [class*="css"]  { font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; }
.stApp { background: #000000; color: #FFFFFF; }
.block-container { padding-top: 1.2rem; max-width: 1300px; }
section[data-testid="stSidebar"] { background: #000000; border-right: 1px solid #e2e8f0; }
h1, h2, h3 { color: #0f172a; letter-spacing: -0.02em; }
h1 { font-weight: 800; margin-bottom: 0.2rem; }
hr { border: none; height: 1px; background: #e2e8f0; margin: 1.2rem 0; }

.kpi-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 0.4rem 0 0.8rem 0; }
.kpi-card {
  background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px;
  padding: 14px 14px 12px 14px; box-shadow: 0 1px 2px rgba(15,23,42,0.05);
}
.kpi-label { font-size: 0.78rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }
.kpi-value { font-size: 1.7rem; font-weight: 900; color: #0f172a; margin-top: 6px; line-height: 1.1; }
.kpi-sub { font-size: 0.85rem; color: #475569; margin-top: 6px; }

div[data-baseweb="tab-list"] { gap: 8px; }
button[data-baseweb="tab"] {
  background: #ffffff !important; border: 1px solid #e2e8f0 !important; border-radius: 10px !important;
  padding: 10px 14px !important; font-weight: 800 !important; color: #0f172a !important;
}
button[aria-selected="true"][data-baseweb="tab"] {
  border-color: #0f172a !important; box-shadow: 0 2px 10px rgba(15,23,42,0.08) !important;
}
[data-testid="stDataFrame"] { border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; }
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------
# Paths (robust)
# ----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # code/ -> projet/
EVENTS_CLEAN_PATH = PROJECT_ROOT / "data" / "clean" / "events_clean.csv"

# ----------------------------
# Helpers
# ----------------------------
def format_int(x: float | int) -> str:
    return f"{int(x):,}".replace(",", " ")

def fmt_pct(x: float) -> str:
    return "—" if pd.isna(x) else f"{x*100:.2f}%"

@st.cache_data(show_spinner=False)
def load_events(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    df = pd.read_csv(path, low_memory=False)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Ensure columns exist
    if "date" not in df.columns:
        df["date"] = df["timestamp"].dt.date
    if "hour" not in df.columns:
        df["hour"] = df["timestamp"].dt.hour
    if "day_of_week" not in df.columns:
        df["day_of_week"] = df["timestamp"].dt.day_name()

    if "is_view" not in df.columns:
        df["is_view"] = (df["event"] == "view").astype(int)
    if "is_addtocart" not in df.columns:
        df["is_addtocart"] = (df["event"] == "addtocart").astype(int)
    if "is_transaction" not in df.columns:
        df["is_transaction"] = (df["event"] == "transaction").astype(int)

    return df

@st.cache_data(show_spinner=False)
def build_kpi_daily(df: pd.DataFrame) -> pd.DataFrame:
    kpi = (
        df.groupby("date")
        .agg(
            total_events=("event", "count"),
            views=("is_view", "sum"),
            addtocart=("is_addtocart", "sum"),
            transactions=("is_transaction", "sum"),
            unique_visitors=("visitorid", "nunique"),
        )
        .reset_index()
    )
    kpi["date"] = pd.to_datetime(kpi["date"], errors="coerce")
    kpi["conv_view_to_atc"] = kpi["addtocart"] / kpi["views"].replace(0, np.nan)
    kpi["conv_atc_to_trx"] = kpi["transactions"] / kpi["addtocart"].replace(0, np.nan)
    kpi["conv_view_to_trx"] = kpi["transactions"] / kpi["views"].replace(0, np.nan)
    return kpi

def compute_global_kpis(df: pd.DataFrame) -> dict:
    views = int(df["is_view"].sum())
    atc = int(df["is_addtocart"].sum())
    trx = int(df["is_transaction"].sum())

    unique_visitors = df["visitorid"].nunique()
    buyers = df.loc[df["event"] == "transaction", "visitorid"].nunique() if trx else 0

    return {
        "total_events": len(df),
        "unique_visitors": unique_visitors,
        "unique_items": df["itemid"].nunique(),
        "views": views,
        "addtocart": atc,
        "transactions": trx,
        "conv_view_to_atc": (atc / views) if views else np.nan,
        "conv_atc_to_trx": (trx / atc) if atc else np.nan,
        "conv_view_to_trx": (trx / views) if views else np.nan,
        "buyers": buyers,
        "buyer_rate": (buyers / unique_visitors) if unique_visitors else np.nan,
    }

def render_kpi_cards(k: dict) -> None:
    st.markdown(
        f"""
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-label">Visiteurs uniques</div>
    <div class="kpi-value">{format_int(k["unique_visitors"])}</div>
    <div class="kpi-sub">Acheteurs: {format_int(k["buyers"])} ({fmt_pct(k["buyer_rate"])})</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Transactions</div>
    <div class="kpi-value">{format_int(k["transactions"])}</div>
    <div class="kpi-sub">Conversion vue→achat: {fmt_pct(k["conv_view_to_trx"])}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Vues</div>
    <div class="kpi-value">{format_int(k["views"])}</div>
    <div class="kpi-sub">Vue→Panier: {fmt_pct(k["conv_view_to_atc"])}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Ajouts panier</div>
    <div class="kpi-value">{format_int(k["addtocart"])}</div>
    <div class="kpi-sub">Panier→Achat: {fmt_pct(k["conv_atc_to_trx"])}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

# ----------------------------
# Cohortes
# ----------------------------
@st.cache_data(show_spinner=False)
def build_cohorts(events: pd.DataFrame, freq: str = "W") -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Cohortes basées sur la première activité du visiteur.
    freq: "W" (semaine) ou "M" (mois)
    Retourne:
      - cohort_counts: nb users par cohort et période
      - retention: retention rate (%)
    """
    df = events[["visitorid", "timestamp"]].dropna().copy()
    df["period"] = df["timestamp"].dt.to_period(freq).dt.start_time

    first_period = df.groupby("visitorid")["period"].min().rename("cohort").reset_index()
    df = df.merge(first_period, on="visitorid", how="left")

    # index = cohort, columns = period, values = unique users
    cohort_counts = (
        df.groupby(["cohort", "period"])["visitorid"]
        .nunique()
        .reset_index(name="users")
        .pivot(index="cohort", columns="period", values="users")
        .sort_index()
    )

    # Retention = users(period) / users(cohort start)
    cohort_sizes = cohort_counts.iloc[:, 0]
    retention = cohort_counts.divide(cohort_sizes, axis=0)

    return cohort_counts, retention

# ----------------------------
# A/B Test simulation
# ----------------------------
def z_test_proportions(success_a: int, n_a: int, success_b: int, n_b: int) -> tuple[float, float]:
    """
    Z-test 2 proportions (approx normal).
    Returns: z, p_value (two-sided)
    """
    if n_a == 0 or n_b == 0:
        return np.nan, np.nan

    p1 = success_a / n_a
    p2 = success_b / n_b
    p_pool = (success_a + success_b) / (n_a + n_b)

    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    if se == 0:
        return np.nan, np.nan

    z = (p2 - p1) / se

    # two-sided p-value without scipy: use normal CDF approx via erf
    # p = 2*(1 - Phi(|z|))
    from math import erf, sqrt
    def phi(x):  # CDF standard normal
        return 0.5 * (1.0 + erf(x / sqrt(2.0)))

    p_value = 2 * (1 - phi(abs(z)))
    return float(z), float(p_value)

@st.cache_data(show_spinner=False)
def simulate_ab(
    events_period: pd.DataFrame,
    unit: str = "visitor",
    baseline: str = "view_to_transaction",
    uplift: float = 0.10,
    seed: int = 42,
) -> dict:
    """
    Simule un A/B test à partir des données de la période.
    unit: "visitor" (par visiteur)
    baseline:
      - "view_to_transaction": conversion = buyers / visitors_with_view
      - "addtocart_to_transaction": conversion = buyers / visitors_with_addtocart
    uplift: +10% relatif (0.10)
    """
    rng = np.random.default_rng(seed)

    df = events_period.copy()

    # Population & succès
    # On travaille au niveau visiteur (plus logique)
    v = df["visitorid"].dropna().astype("int64").unique()
    if len(v) == 0:
        return {"error": "Aucun visiteur dans la période."}

    assign = rng.choice(["A", "B"], size=len(v), replace=True)
    assign_df = pd.DataFrame({"visitorid": v, "group": assign})

    # Flags par visiteur
    by_v = df.groupby("visitorid").agg(
        has_view=("is_view", "max"),
        has_addtocart=("is_addtocart", "max"),
        has_transaction=("is_transaction", "max"),
    ).reset_index()

    m = assign_df.merge(by_v, on="visitorid", how="left").fillna(0)

    if baseline == "view_to_transaction":
        pop = m[m["has_view"] == 1].copy()
        denom_col = "has_view"
    else:
        pop = m[m["has_addtocart"] == 1].copy()
        denom_col = "has_addtocart"

    if len(pop) == 0:
        return {"error": "Population vide (aucun visiteur éligible)."}

    # Baseline conversion sur A (observée)
    a = pop[pop["group"] == "A"].copy()
    b = pop[pop["group"] == "B"].copy()

    # Si un groupe est vide à cause de l'aléa, on réassigne
    if len(a) == 0 or len(b) == 0:
        assign = rng.choice(["A", "B"], size=len(pop), replace=True)
        pop["group"] = assign
        a = pop[pop["group"] == "A"].copy()
        b = pop[pop["group"] == "B"].copy()

    # Conversion observée A
    p_a = a["has_transaction"].mean() if len(a) else 0.0
    # Conversion simulée B = A * (1 + uplift), bornée à 1
    p_b = min(1.0, p_a * (1.0 + uplift))

    # On simule les transactions de B (comme si la variante améliorait)
    b_sim = b.copy()
    b_sim["has_transaction_sim"] = rng.binomial(1, p_b, size=len(b_sim))

    # A garde l'observé
    a_sim = a.copy()
    a_sim["has_transaction_sim"] = a_sim["has_transaction"].astype(int)

    # Résultats
    n_a = len(a_sim)
    n_b = len(b_sim)
    s_a = int(a_sim["has_transaction_sim"].sum())
    s_b = int(b_sim["has_transaction_sim"].sum())

    rate_a = s_a / n_a if n_a else np.nan
    rate_b = s_b / n_b if n_b else np.nan

    z, p = z_test_proportions(s_a, n_a, s_b, n_b)

    lift_abs = rate_b - rate_a
    lift_rel = (lift_abs / rate_a) if rate_a and rate_a > 0 else np.nan

    return {
        "unit": unit,
        "baseline": baseline,
        "uplift": uplift,
        "n_a": n_a,
        "n_b": n_b,
        "s_a": s_a,
        "s_b": s_b,
        "rate_a": rate_a,
        "rate_b": rate_b,
        "lift_abs": lift_abs,
        "lift_rel": lift_rel,
        "z": z,
        "p_value": p,
        "pop_size": len(pop),
    }

# ----------------------------
# Load data
# ----------------------------
st.markdown("## E-Commerce Dashboard")
st.caption("Pages : Overview • Cohortes • A/B Test (simulation)")

try:
    events = load_events(EVENTS_CLEAN_PATH)
except Exception as e:
    st.error(str(e))
    st.info("Vérifie que `events_clean.csv` est bien dans `data/clean/` (racine du projet).")
    st.stop()

kpi_daily = build_kpi_daily(events)

# ----------------------------
# Sidebar: navigation + global filters
# ----------------------------
st.sidebar.subheader("Navigation")
page = st.sidebar.radio("Page", ["Overview", "Cohortes", "A/B Test"], index=0)

st.sidebar.subheader("Filtres (global)")
min_d = kpi_daily["date"].min().date()
max_d = kpi_daily["date"].max().date()
date_range = st.sidebar.date_input("Période", value=(min_d, max_d), min_value=min_d, max_value=max_d)

start = pd.to_datetime(date_range[0])
end = pd.to_datetime(date_range[1])

event_types = st.sidebar.multiselect(
    "Types d'événements",
    options=["view", "addtocart", "transaction"],
    default=["view", "addtocart", "transaction"],
)

events_f = events[
    (events["timestamp"] >= start)
    & (events["timestamp"] < end + pd.Timedelta(days=1))
    & (events["event"].isin(event_types))
].copy()

# ----------------------------
# Page: Overview
# ----------------------------
if page == "Overview":
    st.markdown("### Overview")
    kpis = compute_global_kpis(events_f)
    render_kpi_cards(kpis)
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["Tendances", "Funnel", "Horaire", "Top produits"])

    with tab1:
        daily = kpi_daily[(kpi_daily["date"] >= start) & (kpi_daily["date"] <= end)].copy()

        fig = px.line(
            daily,
            x="date",
            y=["views", "addtocart", "transactions"],
            markers=True,
            title="Évolution (views / addtocart / transactions)",
            labels={"value": "Nombre", "date": "Date", "variable": "Métrique"},
        )
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.line(
            daily,
            x="date",
            y=["conv_view_to_trx", "conv_view_to_atc", "conv_atc_to_trx"],
            markers=True,
            title="Taux de conversion (jour)",
            labels={"value": "Taux", "date": "Date", "variable": "Conversion"},
        )
        fig2.update_yaxes(tickformat=".2%")
        st.plotly_chart(fig2, use_container_width=True)

        st.download_button(
            "Télécharger KPI journaliers (CSV)",
            data=daily.to_csv(index=False).encode("utf-8"),
            file_name="kpi_daily_filtered.csv",
            mime="text/csv",
        )

    with tab2:
        views = int(events_f["is_view"].sum())
        atc = int(events_f["is_addtocart"].sum())
        trx = int(events_f["is_transaction"].sum())

        funnel_plot = pd.DataFrame(
            {"Étape": ["Vues", "Ajouts panier", "Transactions"], "Nombre": [views, atc, trx]}
        )

        fig = px.funnel(funnel_plot, x="Nombre", y="Étape", title="Funnel global")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(funnel_plot, use_container_width=True, hide_index=True)

    with tab3:
        if "hour" not in events_f.columns:
            st.info("La colonne 'hour' n'existe pas dans events_clean.csv.")
        else:
            hourly = (
                events_f.groupby("hour")[["is_view", "is_addtocart", "is_transaction"]]
                .sum()
                .reset_index()
            )
            hourly["conv_view_to_trx"] = hourly["is_transaction"] / hourly["is_view"].replace(0, np.nan)

            fig = px.line(
                hourly,
                x="hour",
                y=["is_view", "is_addtocart", "is_transaction"],
                markers=True,
                title="Événements par heure",
                labels={"value": "Nombre", "hour": "Heure", "variable": "Type"},
            )
            st.plotly_chart(fig, use_container_width=True)

            fig2 = px.bar(hourly, x="hour", y="conv_view_to_trx", title="Conversion vue→achat par heure")
            fig2.update_yaxes(tickformat=".2%")
            st.plotly_chart(fig2, use_container_width=True)

    with tab4:
        top = (
            events_f.groupby("itemid")[["is_view", "is_addtocart", "is_transaction"]]
            .sum()
            .reset_index()
            .sort_values("is_view", ascending=False)
            .head(20)
        )

        fig = px.bar(
            top,
            x="is_view",
            y=top["itemid"].astype(str),
            orientation="h",
            title="Top 20 produits par vues",
            labels={"is_view": "Vues", "y": "itemid"},
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(top, use_container_width=True, hide_index=True)

        st.download_button(
            "Télécharger Top produits (CSV)",
            data=top.to_csv(index=False).encode("utf-8"),
            file_name="top_items_period.csv",
            mime="text/csv",
        )

# ----------------------------
# Page: Cohortes
# ----------------------------
elif page == "Cohortes":
    st.markdown("### Cohortes")
    st.caption("Cohortes basées sur la première activité du visiteur (semaine ou mois).")

    freq = st.radio("Granularité", ["Semaine", "Mois"], horizontal=True)
    freq_code = "W" if freq == "Semaine" else "M"

    # Cohorts sur la période filtrée (tu peux aussi faire sur events complet)
    cohort_counts, retention = build_cohorts(events_f, freq=freq_code)

    if cohort_counts.empty:
        st.warning("Impossible de construire les cohortes (données insuffisantes sur la période).")
        st.stop()

    # Retention heatmap (Plotly)
    # Limit columns for readability
    max_periods = st.slider("Nombre de périodes affichées", min_value=4, max_value=20, value=12)
    retention_limited = retention.iloc[:, :max_periods].copy()

    
    fig = px.imshow(
        retention_limited,
        aspect="auto",
        labels=dict(x="Période", y="Cohorte", color="Rétention"),
        title="Rétention (cohorte vs périodes)",
    )

    fig.update_layout(
        height=520,
        coloraxis_colorbar=dict(
            title="Rétention",
            tickformat=".0%"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Taille des cohortes (utilisateurs)")

    cohort_sizes = cohort_counts.iloc[:, 0].sort_index()

    fig2 = px.bar(
        x=cohort_sizes.index.astype(str),
        y=cohort_sizes.values,
        labels={"x": "Cohorte", "y": "Utilisateurs"},
        title="Taille des cohortes (première période)",
    )

    st.plotly_chart(fig2, use_container_width=True)


# ----------------------------
# Page: A/B Test
# ----------------------------
else:
    st.markdown("### A/B Test (simulation)")
    st.caption("Simulation conforme : assignation A/B + uplift sur un KPI de conversion, basé sur les données du projet.")

    c1, c2 = st.columns(2)
    with c1:
        baseline = st.selectbox(
            "KPI cible",
            options=["view_to_transaction", "addtocart_to_transaction"],
            format_func=lambda x: "Vue → Achat" if x == "view_to_transaction" else "Panier → Achat",
        )
    with c2:
        uplift = st.slider("Uplift relatif (B vs A)", min_value=0.0, max_value=0.50, value=0.10, step=0.01)

    seed = st.number_input("Seed (reproductibilité)", min_value=0, max_value=999999, value=42, step=1)

    res = simulate_ab(events_f, baseline=baseline, uplift=float(uplift), seed=int(seed))

    if "error" in res:
        st.warning(res["error"])
        st.stop()

    # KPI cards for AB
    st.markdown(
        f"""
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-label">Population éligible</div>
    <div class="kpi-value">{format_int(res["pop_size"])}</div>
    <div class="kpi-sub">Unit: visiteur</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">A conversion</div>
    <div class="kpi-value">{fmt_pct(res["rate_a"])}</div>
    <div class="kpi-sub">n={format_int(res["n_a"])}, succ={format_int(res["s_a"])}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">B conversion (simulée)</div>
    <div class="kpi-value">{fmt_pct(res["rate_b"])}</div>
    <div class="kpi-sub">n={format_int(res["n_b"])}, succ={format_int(res["s_b"])}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Lift & p-value</div>
    <div class="kpi-value">{fmt_pct(res["lift_abs"])}</div>
    <div class="kpi-sub">Lift rel: {fmt_pct(res["lift_rel"]) if not pd.isna(res["lift_rel"]) else "—"} • p={res["p_value"]:.4f}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Visual: bar comparison
    ab_df = pd.DataFrame(
        {
            "Groupe": ["A", "B"],
            "Conversion": [res["rate_a"], res["rate_b"]],
        }
    )
    fig = px.bar(ab_df, x="Groupe", y="Conversion", title="Conversion A vs B")
    fig.update_yaxes(tickformat=".2%")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Interprétation")
    alpha = 0.05
    if not pd.isna(res["p_value"]) and res["p_value"] < alpha:
        st.success(f"Résultat significatif (p < {alpha}). Variante B performe mieux (simulation).")
    else:
        st.info(f"Résultat non significatif (p ≥ {alpha}). Il faut plus de données ou un uplift plus fort.")

# Footer
st.caption(f"Mise à jour : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
