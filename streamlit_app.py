import streamlit as st
import pandas as pd
import os
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
from crypto import symbols

SUBSCRIBERS_FILE = "subscribers.txt"
ANOMALIES_FILE = "anomalies.csv"
MARKET_FILE = "market_prices.csv"

st.set_page_config(page_title="Panel wykrywania anomalii kryptowalut", layout="wide")
st.title("📊 Detektor anomalii kryptowalut")
st_autorefresh(interval=30 * 1000, limit=None, key="auto_refresh")

# ---------------- SUBSKRYPCJE EMAIL -------------
email = st.text_input("Twój email")
action = st.radio("Wybierz:", ["Zapisz się", "Wypisz się"])

def load_emails():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    with open(SUBSCRIBERS_FILE, "r") as f:
        return [line.strip() for line in f.readlines()]

def save_emails(emails):
    with open(SUBSCRIBERS_FILE, "w") as f:
        f.writelines([e + "\n" for e in emails])

if st.button("Zatwierdź"):
    emails = load_emails()
    if action == "Zapisz się":
        if email and email not in emails:
            emails.append(email)
            save_emails(emails)
            st.success("Zapisano.")
        else:
            st.info("Już zapisany lub brak e‑maila.")
    else:  # wypis
        if email in emails:
            emails.remove(email)
            save_emails(emails)
            st.success("Wypisano.")
        else:
            st.warning("Nie znaleziono podanego e‑maila.")

# ---------------- WYBÓR SYMBOLU ----------------
selected_symbol = st.selectbox("Wybierz kryptowalutę:", symbols)

# 🚨 ANOMALIE
st.markdown("---")
st.subheader("🚨 Wykryte anomalie (Isolation Forest)")
if os.path.exists(ANOMALIES_FILE) and os.path.getsize(ANOMALIES_FILE) > 0:
    df = pd.read_csv(ANOMALIES_FILE)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

    st.markdown(f"🔢 **Łącznie wykrytych anomalii:** {len(df)}")

    # Statystyki per symbol - tabela
    st.subheader("📊 Anomalie per symbol")
    anomaly_stats = df.groupby("symbol").size().reset_index(name="liczba_anomalii")
    st.dataframe(anomaly_stats.sort_values("liczba_anomalii", ascending=False))

    # Filtruj po symbolu i sortuj
    df_sym = df[df["symbol"] == selected_symbol].sort_values("timestamp", ascending=False)

    st.markdown("### 📋 Ostatnie anomalie – stronicowanie")

    # Parametry stronicowania
    rows_per_page = 8
    total_rows = len(df_sym)
    total_pages = max(1, (total_rows - 1) // rows_per_page + 1)

    page = st.number_input("Wybierz stronę:", min_value=1, max_value=total_pages, value=1, step=1)

    start_idx = (page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page

    # Wyświetl stronę
    st.dataframe(df_sym.iloc[start_idx:end_idx], height=300)
    st.caption(f"Strona {page} z {total_pages} ({total_rows} rekordów)")

    # Wykres
    fig_ano = px.line(df_sym, x="timestamp", y="price",
                      title=f"Cena {selected_symbol} z anomaliami")
    fig_ano.add_scatter(x=df_sym["timestamp"],
                        y=df_sym["price"],
                        mode="markers",
                        marker=dict(color="red", size=10),
                        name="Anomalia")
    st.plotly_chart(fig_ano, use_container_width=True)
else:
    st.info(f"Brak danych o anomaliach (plik {ANOMALIES_FILE} pusty lub nieistnieje).")
    st.write(f"Status pliku: {'Istnieje' if os.path.exists(ANOMALIES_FILE) else 'Nie istnieje'}")
    if os.path.exists(ANOMALIES_FILE):
        st.write(f"Rozmiar pliku: {os.path.getsize(ANOMALIES_FILE)} bajtów")

# ---------------- CIĄGŁA CENA -------------------
st.markdown("---")
st.subheader("📈 Wykres ceny (ciągłej)")

if os.path.exists(MARKET_FILE) and os.path.getsize(MARKET_FILE) > 0:
    df_mkt = pd.read_csv(MARKET_FILE, on_bad_lines="skip") 
    df_mkt["timestamp"] = pd.to_datetime(df_mkt["timestamp"], unit="s")
    df_mkt_sym = df_mkt[df_mkt["symbol"] == selected_symbol].sort_values("timestamp")

    fig_price = px.line(df_mkt_sym, x="timestamp", y="price",
                        title=f"Cena {selected_symbol} – dane ciągłe")
    st.plotly_chart(fig_price, use_container_width=True)
else:
    st.info("Brak market_prices.csv lub plik pusty.")

# ---------------- LISTA SUBSKRYBENTÓW -----------
st.markdown("---")
st.write("📋 Subskrybenci:")
st.dataframe(pd.DataFrame(load_emails(), columns=["Email"]))