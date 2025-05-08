# train_isolation_forest.py
from __future__ import annotations
import concurrent.futures as cf
import logging
import time
from pathlib import Path
from typing import Dict, List

import joblib
import pandas as pd
import requests
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from crypto import symbols   # lista 10 symboli

# ---------- konfiguracja ----------
API_URL = "https://api.binance.com/api/v3/ticker/24hr?symbol={}"
SAMPLES_PER_SYMBOL = 100          # zmień na 10–20 dla szybkiego demo
REQUEST_DELAY = 0.5               # s – przestrzegamy limitów Binance
CONTAMINATION = 0.005             # 0.5 % uznajemy za anomalie
N_ESTIMATORS = 200
RAND_STATE = 42
MODEL_PATH = Path("isolation_forest_model.pkl")
SCALER_PATH = Path("standard_scaler.pkl")
RAW_DATA_PATH = Path("training_raw.csv")
# ----------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

def fetch_one(symbol: str) -> List[Dict]:
    """Pobiera SAMPLES_PER_SYMBOL rekordów dla jednego symbolu."""
    rows: List[Dict] = []
    for _ in range(SAMPLES_PER_SYMBOL):
        try:
            r = requests.get(API_URL.format(symbol), timeout=10)
            j = r.json()
            rows.append(
                {
                    "symbol": symbol,
                    "price": float(j["lastPrice"]),
                    "volume": float(j["volume"]),
                    "priceChangePercent": float(j["priceChangePercent"]),
                    "weightedAvgPrice": float(j["weightedAvgPrice"]),
                    "count": int(j["count"]),
                }
            )
        except Exception as exc:
            logging.warning("Błąd API %s: %s", symbol, exc)
        time.sleep(REQUEST_DELAY)
    return rows

def collect_data() -> pd.DataFrame:
    logging.info("⏳ Pobieranie danych z Binance …")
    with cf.ThreadPoolExecutor(max_workers=len(symbols)) as pool:
        results = pool.map(fetch_one, symbols)

    data = [row for batch in results for row in batch]
    df = pd.DataFrame(data)
    df["symbol_id"] = df["symbol"].astype("category").cat.codes
    logging.info("✅ Zebrano %d wierszy", len(df))
    df.to_csv(RAW_DATA_PATH, index=False)
    return df

def train_model(df: pd.DataFrame):
    features = ["price", "volume", "priceChangePercent",
                "weightedAvgPrice", "count", "symbol_id"]

    X = df[features].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=N_ESTIMATORS,
        contamination=CONTAMINATION,
        n_jobs=-1,
        random_state=RAND_STATE,
    )
    logging.info("🚀 Trening Isolation Forest …")
    model.fit(X_scaled)
    logging.info("✅ Trening zakończony")

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    logging.info("💾 Zapisano model → %s", MODEL_PATH)
    logging.info("💾 Zapisano scaler → %s", SCALER_PATH)

if __name__ == "__main__":
    df_train = collect_data()
    train_model(df_train)
