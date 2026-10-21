import streamlit as st
import pandas as pd
import firebase_admin
import plotly.express as px
from firebase_config import firebase_app
from data import load_data
from images import MCLAREN_CAR, LANDO_NORRIS, OSCAR_PIASTRI, F1_RACE


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="McLaren F1  DashBoard",
    page_icon="🏎️",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        135deg,
        #080808 0%,
        #111111 55%,
        #1d1d1d 100%
    );
    background-attachment: fixed;
}

.header {
    background: #101010;
    padding: 35px;
    text-align: center;
    border-bottom: 5px solid #ff8700;
    margin-bottom: 25px;
    border-radius: 0 0 15px 15px;
}

.header h1 {
    color: #ff8700;
    margin: 0;
    font-size: 42px;
}

.header p {
    color: white;
    margin-top: 10px;
    font-size: 17px;
}

.section {
    background: #171717;
    padding: 25px;
    border-radius: 15px;
    margin-top: 25px;
    margin-bottom: 25px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
}

.driver-card {
    background: white;
    border-radius: 15px;
    overflow: hidden;
    border-top: 5px solid #ff8700;
    box-shadow: 0 4px 15px rgba(0,0,0,0.10);
}

.driver-info {
    padding: 20px;
}

.driver-name {
    font-size: 25px;
    font-weight: bold;
}

.driver-number {
    color: #ff8700;
    font-weight: bold;
}

/* KPI CARDS */
.kpi-card {
    position: relative;
    min-height: 112px;
    padding: 18px 20px;
    border-radius: 16px;
    background: linear-gradient(145deg, #1c1c1c 0%, #101010 100%);
    border: 1px solid #303030;
    border-top: 4px solid #ff8700;
    box-shadow: 0 8px 22px rgba(0,0,0,0.35);
    overflow: hidden;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.kpi-card:hover {
    transform: translateY(-3px);
    border-color: #ff8700;
}

.kpi-card::after {
    content: "";
    position: absolute;
    width: 90px;
    height: 90px;
    right: -35px;
    bottom: -45px;
    border-radius: 50%;
    background: rgba(255,135,0,0.10);
}

.kpi-icon {
    font-size: 23px;
    margin-bottom: 7px;
}

.kpi-title {
    color: #a9a9a9;
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.7px;
}

.kpi-value {
    color: #ffffff;
    font-size: 30px;
    font-weight: 800;
    line-height: 1.15;
    margin-top: 4px;
}

.kpi-accent {
    color: #ff8700;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD DATA
# ============================================================

try:
    df = load_data()
except Exception as e:
    st.error(f"Unable to load data: {e}")
    st.stop()


# Make sure required columns exist
required_columns = [
    "Season",
    "Round",
    "Date",
    "GrandPrix",
    "Driver",
    "Race_Pos",
    "Points",
    "Finish_Position",
    "Podium",
    "Win",
    "Cumulative_Points"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "Missing columns in mclaren_race_data.csv: "
        + ", ".join(missing_columns)
    )
    st.stop()


# Numeric conversion
for column in [
    "Season",
    "Round",
    "Race_Pos",
    "Points",
    "Finish_Position",
    "Cumulative_Points"
]:
    df[column] = pd.to_numeric(df[column], errors="coerce")


# Date conversion
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="header">
    <h1>🏎️ McLaren F1 DashBoard</h1>
    <p>Formula 1 Race Performance Dashboard | 2020–2025</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# HERO IMAGE
# ============================================================

if MCLAREN_CAR:
    st.image(
        MCLAREN_CAR,
        caption="McLaren Formula 1",
        use_container_width=True
    )
else:
    st.warning("McLaren car image not found.")


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.title("🏎️ Dashboard Filters")
st.sidebar.markdown("---")

seasons = sorted(df["Season"].dropna().unique())

selected_seasons = st.sidebar.multiselect(
    "Season",
    seasons,
    default=seasons
)

drivers = sorted(df["Driver"].dropna().unique())

selected_drivers = st.sidebar.multiselect(
    "Driver",
    drivers,
    default=drivers
)

races = sorted(df["GrandPrix"].dropna().unique())

selected_races = st.sidebar.multiselect(
    "Grand Prix",
    races,
    default=races
)


# ============================================================
# FILTER DATA
# ============================================================

filtered = df.copy()

if selected_seasons:
    filtered = filtered[
        filtered["Season"].isin(selected_seasons)
    ]

if selected_drivers:
    filtered = filtered[
        filtered["Driver"].isin(selected_drivers)
    ]

if selected_races:
    filtered = filtered[
        filtered["GrandPrix"].isin(selected_races)
    ]

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_races = filtered["GrandPrix"].nunique()

total_points = filtered["Points"].sum()

wins = int(
    filtered["Win"]
    .fillna(False)
    .astype(bool)
    .sum()
)

podiums = int(
    filtered["Podium"]
    .fillna(False)
    .astype(bool)
    .sum()
)

avg_finish = filtered["Finish_Position"].mean()

avg_race_position = filtered["Race_Pos"].mean()


# ============================================================
# KPI CARDS
# ============================================================

st.markdown("### 📊 Performance Overview")

# Custom KPI cards for a clean McLaren/F1 dark theme
kpis = [
    ("🏁", "Races", f"{total_races}"),
    ("🏆", "Points", f"{total_points:.0f}"),
    ("🥇", "Wins", f"{wins}"),
    ("🥉", "Podiums", f"{podiums}"),
    ("📊", "Avg Finish", f"{avg_finish:.2f}"),
    ("🏎️", "Avg Race Pos", f"{avg_race_position:.2f}"),
]

kpi_cols = st.columns(6)

for col, (icon, title, value) in zip(kpi_cols, kpis):
    with col:
        st.markdown(
            f"""
            <div class=\"kpi-card\">
                <div class=\"kpi-icon\">{icon}</div>
                <div class=\"kpi-title\">{title}</div>
                <div class=\"kpi-value\">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# DRIVER ANALYSIS
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)

st.subheader("👨‍🚀 Driver Performance")

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# LANDO
# ------------------------------------------------------------

with col1:

    if LANDO_NORRIS:
        st.image(
            LANDO_NORRIS,
            caption="Lando Norris",
            use_container_width=True
        )

    lando = filtered[
        filtered["Driver"] == "Lando Norris"
    ]

    if not lando.empty:

        st.markdown(
            """
            <div class="driver-info">
                <div class="driver-name">Lando Norris</div>
                <div class="driver-number">CAR #04</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)

        with c1:
            st.metric(
                "Points",
                f"{lando['Points'].sum():.0f}"
            )

        with c2:
            st.metric(
                "Wins",
                f"{lando['Win'].fillna(False).astype(bool).sum()}"
            )

        st.write(
            f"📊 Average Finish: "
            f"**{lando['Finish_Position'].mean():.2f}**"
        )

        st.write(
            f"🏁 Average Race Position: "
            f"**{lando['Race_Pos'].mean():.2f}**"
        )

        st.write(
            f"🥉 Podiums: "
            f"**{lando['Podium'].fillna(False).astype(bool).sum()}**"
        )

    else:
        st.info("Lando Norris is not included in the current filters.")


# ------------------------------------------------------------
# OSCAR
# ------------------------------------------------------------

with col2:

    if OSCAR_PIASTRI:
        st.image(
            OSCAR_PIASTRI,
            caption="Oscar Piastri",
            use_container_width=True
        )

    oscar = filtered[
        filtered["Driver"] == "Oscar Piastri"
    ]

    if not oscar.empty:

        st.markdown(
            """
            <div class="driver-info">
                <div class="driver-name">Oscar Piastri</div>
                <div class="driver-number">CAR #81</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)

        with c1:
            st.metric(
                "Points",
                f"{oscar['Points'].sum():.0f}"
            )

        with c2:
            st.metric(
                "Wins",
                f"{oscar['Win'].fillna(False).astype(bool).sum()}"
            )

        st.write(
            f"📊 Average Finish: "
            f"**{oscar['Finish_Position'].mean():.2f}**"
        )

        st.write(
            f"🏁 Average Race Position: "
            f"**{oscar['Race_Pos'].mean():.2f}**"
        )

        st.write(
            f"🥉 Podiums: "
            f"**{oscar['Podium'].fillna(False).astype(bool).sum()}**"
        )

    else:
        st.info("Oscar Piastri is not included in the current filters.")

st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# POINTS BY DRIVER
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)

st.subheader("🏆 Points by Driver")

points = (
    filtered
    .groupby("Driver", as_index=False)["Points"]
    .sum()
    .sort_values("Points", ascending=False)
)

fig = px.bar(
    points,
    x="Driver",
    y="Points",
    text="Points",
    title="Total Championship Points"
)

fig.update_traces(
    marker_color="#ff8700",
    textposition="outside"
)

fig.update_layout(
    template="plotly_white",
    height=450,
    xaxis_title="Driver",
    yaxis_title="Points"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# CHAMPIONSHIP POINTS PROGRESSION
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)

st.subheader("📈 Championship Points Progression")

trend = filtered.sort_values(
    ["Driver", "Season", "Round"]
).copy()

trend["Cumulative_Filtered_Points"] = (
    trend.groupby("Driver")["Points"].cumsum()
)

trend["Race_Number"] = (
    trend.groupby("Driver").cumcount() + 1
)

fig = px.line(
    trend,
    x="Race_Number",
    y="Cumulative_Filtered_Points",
    color="Driver",
    markers=True,
    hover_data=[
        "Season",
        "Round",
        "GrandPrix",
        "Points"
    ],
    title="Cumulative Points Across Selected Races"
)

fig.update_layout(
    template="plotly_white",
    height=450,
    xaxis_title="Race Number",
    yaxis_title="Cumulative Points"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# RACE POSITION ANALYSIS
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)

st.subheader("🏁 Race Position Analysis")

fig = px.scatter(
    filtered,
    x="Race_Pos",
    y="Finish_Position",
    color="Driver",
    size="Points",
    hover_name="GrandPrix",
    hover_data=[
        "Season",
        "Round",
        "Points"
    ],
    title="Race Position vs Finish Position"
)

fig.update_xaxes(
    autorange="reversed",
    title="Race Position"
)

fig.update_yaxes(
    autorange="reversed",
    title="Finish Position"
)

fig.update_layout(
    template="plotly_white",
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# SEASON ANALYSIS
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)

st.subheader("📅 Season Performance")

season_points = (
    filtered
    .groupby(["Season", "Driver"], as_index=False)["Points"]
    .sum()
)

fig = px.bar(
    season_points,
    x="Season",
    y="Points",
    color="Driver",
    barmode="group",
    text="Points",
    title="Points by Season and Driver"
)

fig.update_layout(
    template="plotly_white",
    height=500,
    xaxis_title="Season",
    yaxis_title="Points"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# PODIUM & WIN ANALYSIS
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)

st.subheader("🥇 Wins and Podiums by Driver")

achievement = (
    filtered
    .groupby("Driver")
    .agg(
        Wins=("Win", lambda x: x.fillna(False).astype(bool).sum()),
        Podiums=("Podium", lambda x: x.fillna(False).astype(bool).sum())
    )
    .reset_index()
)

achievement_long = achievement.melt(
    id_vars="Driver",
    value_vars=["Wins", "Podiums"],
    var_name="Achievement",
    value_name="Count"
)

fig = px.bar(
    achievement_long,
    x="Driver",
    y="Count",
    color="Achievement",
    barmode="group",
    text="Count",
    title="Wins and Podiums"
)

fig.update_layout(
    template="plotly_white",
    height=450,
    yaxis_title="Count"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# RACE-BY-RACE PERFORMANCE
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)

st.subheader("🏎️ Race-by-Race Performance")

race_summary = filtered[
    [
        "Season",
        "Round",
        "GrandPrix",
        "Driver",
        "Race_Pos",
        "Finish_Position",
        "Points",
        "Podium",
        "Win"
    ]
].sort_values(
    ["Season", "Round", "Driver"]
)

st.dataframe(
    race_summary,
    use_container_width=True,
    hide_index=True
)

st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# COMPLETE DATASET
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)

st.subheader("📋 Complete Dataset")

st.dataframe(
    filtered.sort_values(
        ["Season", "Round", "Driver"]
    ),
    use_container_width=True,
    hide_index=True
)

csv = filtered.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Data",
    data=csv,
    file_name="mclaren_filtered_data.csv",
    mime="text/csv"
)

st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# RACE PHOTO
# ============================================================

if F1_RACE:

    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.subheader("🏁 McLaren Race")

    st.image(
        F1_RACE,
        use_container_width=True
    )

    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div style="
    text-align:center;
    color:#777;
    padding:30px;
">
    <b>McLaren F1 DashBoard</b>
    <br>
    Python • Pandas • Plotly • Streamlit • Numpy • SQLPostgre
</div>
""", unsafe_allow_html=True)
