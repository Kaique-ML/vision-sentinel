"""
VisionSentinel Dashboard — Interface Streamlit de Business Intelligence.
Lê o banco de dados SQLite e exibe KPIs, gráficos e registros em tempo real.

Execução:
    streamlit run dashboard/app.py
"""

import sqlite3
import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "data/detections.db")

# ── Configuração da página ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="VisionSentinel · Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS customizado ────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; }
    .block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)


# ── Funções de acesso ao banco ────────────────────────────────────────────────

@st.cache_resource
def get_connection():
    """
    Retorna uma conexão persistente ao banco SQLite (cached pelo Streamlit).

    Returns:
        sqlite3.Connection: Conexão ao banco de dados.
    """
    if not os.path.exists(DB_PATH):
        st.error(f"Banco de dados não encontrado em `{DB_PATH}`. Execute `python seed_data.py` primeiro.")
        st.stop()
    return sqlite3.connect(DB_PATH, check_same_thread=False)


@st.cache_data(ttl=30)
def load_data(days_back: int) -> pd.DataFrame:
    """
    Carrega os registros de detecção dos últimos N dias.

    Args:
        days_back (int): Quantidade de dias para olhar para trás.

    Returns:
        pd.DataFrame: DataFrame com colunas timestamp, class_name, confidence e bbox.
    """
    conn = get_connection()
    since = (datetime.now() - timedelta(days=days_back)).isoformat()
    df = pd.read_sql_query(
        "SELECT timestamp, class_name, confidence FROM logs_deteccao WHERE timestamp >= ? ORDER BY timestamp",
        conn,
        params=(since,),
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/security-camera.png", width=72)
    st.title("VisionSentinel")
    st.caption("Motor de Visão Computacional")
    st.divider()

    days_back = st.slider("📅 Período de análise (dias)", 1, 30, 7)
    selected_classes = st.multiselect(
        "🎯 Classes",
        options=["person", "car", "truck", "bicycle"],
        default=["person", "car", "truck", "bicycle"],
    )
    min_conf = st.slider("🔒 Confiança mínima", 0.0, 1.0, 0.45, 0.05)

    st.divider()
    if st.button("🔄 Atualizar dados"):
        st.cache_data.clear()
        st.rerun()

    st.caption(f"Banco: `{DB_PATH}`")

# ── Carregamento e filtragem ──────────────────────────────────────────────────
df_raw = load_data(days_back)
df = df_raw[
    df_raw["class_name"].isin(selected_classes) &
    (df_raw["confidence"] >= min_conf)
].copy()

if df.empty:
    st.warning("Nenhum registro encontrado com os filtros selecionados.")
    st.stop()

# ── KPIs ──────────────────────────────────────────────────────────────────────
st.subheader("📊 Indicadores Gerais")
col1, col2, col3, col4 = st.columns(4)

df["hour"] = df["timestamp"].dt.hour
peak_hour = df["hour"].value_counts().idxmax()
top_class = df["class_name"].value_counts().idxmax()
avg_conf = df["confidence"].mean()

col1.metric("Total de Detecções", f"{len(df):,}")
col2.metric("Horário de Pico", f"{peak_hour:02d}h – {peak_hour+1:02d}h")
col3.metric("Classe Dominante", top_class.capitalize())
col4.metric("Confiança Média", f"{avg_conf:.1%}")

st.divider()

# ── Gráficos ──────────────────────────────────────────────────────────────────
col_a, col_b = st.columns([2, 1])

with col_a:
    st.subheader("📈 Volume de Detecções por Hora")
    df_hourly = (
        df.groupby([df["timestamp"].dt.floor("H"), "class_name"])
        .size()
        .reset_index(name="count")
    )
    df_hourly.rename(columns={"timestamp": "hora"}, inplace=True)
    fig_line = px.line(
        df_hourly,
        x="hora", y="count", color="class_name",
        labels={"hora": "Hora", "count": "Detecções", "class_name": "Classe"},
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_line.update_layout(legend_title="Classe", hovermode="x unified")
    st.plotly_chart(fig_line, use_container_width=True)

with col_b:
    st.subheader("🍩 Distribuição por Classe")
    class_counts = df["class_name"].value_counts().reset_index()
    class_counts.columns = ["Classe", "Total"]
    fig_pie = px.pie(
        class_counts, values="Total", names="Classe",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)

# ── Heatmap por hora do dia ───────────────────────────────────────────────────
st.subheader("🌡️ Mapa de Calor — Detecções por Hora do Dia")
df["weekday"] = df["timestamp"].dt.day_name()
heat = df.groupby(["weekday", "hour"]).size().reset_index(name="count")
day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
heat["weekday"] = pd.Categorical(heat["weekday"], categories=day_order, ordered=True)
heat = heat.sort_values("weekday")

fig_heat = px.density_heatmap(
    heat, x="hour", y="weekday", z="count",
    color_continuous_scale="Viridis",
    labels={"hour": "Hora do dia", "weekday": "Dia da semana", "count": "Detecções"},
)
st.plotly_chart(fig_heat, use_container_width=True)

# ── Tabela de últimos registros ───────────────────────────────────────────────
st.subheader("🗒️ Últimos 100 Registros")
latest = df.sort_values("timestamp", ascending=False).head(100).copy()
latest["timestamp"] = latest["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
latest["confidence"] = latest["confidence"].map("{:.1%}".format)
latest.rename(columns={
    "timestamp": "Data/Hora",
    "class_name": "Classe",
    "confidence": "Confiança",
}).reset_index(drop=True)
st.dataframe(latest, use_container_width=True, hide_index=True)
