import streamlit as st
import pandas as pd

st.set_page_config(page_title="Player Cards", layout="wide")

st.title("🏒 Player Card App")

uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    df = df.replace("-", 0)
   df = df.replace("-", 0)

for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.fillna(0)

    if "Time on ice" in df.columns:
        df["TOI_min"] = pd.to_timedelta(df["Time on ice"]).dt.total_seconds() / 60

    def per60(col):
        return df[col] / df["TOI_min"] * 60

    for col in ["Shots", "Points", "xG (Expected goals)", "Blocked shots"]:
        if col in df.columns:
            df[col + "_per60"] = per60(col)

    if "Team xG when on ice" in df.columns and "Opponent's xG when on ice" in df.columns:
        df["xG impact"] = df["Team xG when on ice"] - df["Opponent's xG when on ice"]

    def pct(series):
        return series.rank(pct=True)

    for col in df.select_dtypes(include="number").columns:
        df[col + "_pct"] = pct(df[col])

    def avg(cols):
        cols = [c for c in cols if c in df.columns]
        return df[cols].mean(axis=1)

    df["Offence"] = avg(["Points_per60_pct", "Shots_per60_pct", "xG (Expected goals)_per60_pct"])
    df["Transition"] = avg(["xG impact_pct", "CORSI for, %_pct"])
    df["Defence"] = avg(["Blocked shots_per60_pct"])

    df["Total"] = 0.4*df["Offence"] + 0.4*df["Transition"] + 0.2*df["Defence"]

    player = st.selectbox("Select Player", df["Player"])

    p = df[df["Player"] == player].iloc[0]

    st.subheader(player)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Offence", f"{p['Offence']*100:.1f}%")
    col2.metric("Transition", f"{p['Transition']*100:.1f}%")
    col3.metric("Defence", f"{p['Defence']*100:.1f}%")
    col4.metric("TOTAL", f"{p['Total']*100:.1f}%")

    st.dataframe(df)
