"""
producer.py
------------
• pobiera dane 24‑h z Binance REST co 30 s
• dorzuca dodatkowe pola (priceChangePercent, weightedAvgPrice, count)
• wysyła rekord jako JSON do tematu Kafka `crypto_prices`
• zapisuje każdy rekord do market_prices.csv (lokalny log do wykresu)
"""

import json, os, csv, time, requests
from kafka import KafkaProducer
from datetime import datetime
from crypto import symbols  

# ------- konfiguracja -------
KAFKA_BROKER = "kafka:9092"           # nazwa usługi w docker‑compose
TOPIC        = "crypto_prices"
FETCH_EVERY  = 30                     # sekund
CSV_FILE     = "market_prices.csv"
TEST_MODE    = False                  # zmień na True dla testów
# -----------------------------

producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_binance_data(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    response = requests.get(url, timeout=10)
    j = response.json()
    data = {
        "symbol": symbol,
        "price": float(j["lastPrice"]),
        "volume": float(j["volume"]),
        "priceChangePercent": float(j["priceChangePercent"]),
        "weightedAvgPrice":   float(j["weightedAvgPrice"]),
        "count": int(j["count"]),
        "timestamp": time.time(),
        "iso_time": datetime.utcnow().isoformat(timespec="seconds")+"Z",
    }

    # ---------- TESTOWA ANOMALIA ----------
    if TEST_MODE and symbol == "BTCUSDT":
        # 🧪 Zmodyfikuj wszystkie dane jako anomalia
        data["price"] = 99.99   # każda waluta inny skok
        data["volume"] = 0.0001
        data["priceChangePercent"] = 123.45
        data["weightedAvgPrice"] = 88888.88
        data["count"] = 1
        data["comment"] = "SIMULATED_ANOMALY"
    # --------------------------------------
    return data

def log_csv(rec):
    write_header = not os.path.exists(CSV_FILE)
    fields = [
        "timestamp", "symbol", "price", "volume",
        "priceChangePercent", "weightedAvgPrice", "count"
    ]
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if write_header:
            writer.writeheader()
        writer.writerow({k: rec.get(k, "") for k in fields})


while True:
    for symbol in symbols:
        try:
            msg = fetch_binance_data(symbol)
            producer.send(TOPIC, msg)
            log_csv(msg)
            print(f"[Kafka] Wysłano: {msg}")
        except Exception as e:
            print(f"Błąd pobierania danych dla {symbol}: {e}")
    time.sleep(30)
