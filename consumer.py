from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, from_unixtime
from pyspark.sql.types import (StructType, StringType, FloatType,
                               DoubleType, IntegerType)
import joblib
import csv, os
from crypto import symbols
from alert_sender import load_subscribers, send_email_alert

# ---------- TRYB TESTOWY ----------
TEST_MODE = False  # False w środowisku produkcyjnym

# ---------- Załadowanie skalera i model Isolation Forest ----------
scaler = joblib.load("standard_scaler.pkl")
model  = joblib.load("isolation_forest_model.pkl")

print(f"Model loaded: {model}")  # Dodaj na początku skryptu

symbol_mapping = {symbol: idx for idx, symbol in enumerate(symbols)}

spark = SparkSession.builder \
    .appName("CryptoAnomalyIForest") \
    .master("local[*]") \
    .getOrCreate()

schema = (StructType()
          .add("symbol",  StringType())
          .add("price",   FloatType())
          .add("volume",  FloatType())
          .add("priceChangePercent", FloatType())
          .add("weightedAvgPrice",  FloatType())
          .add("count",   IntegerType())
          .add("timestamp", DoubleType()))   

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "crypto_prices") \
    .load()


json_df = (df.selectExpr("CAST(value AS STRING)")
             .select(from_json(col("value"), schema).alias("d"))
             .select("d.*")
             .withColumn("event_time",
                         from_unixtime("timestamp").cast("timestamp")))

# ---------- log anomalii do CSV ----------
def log_anomaly(row):
    file = "anomalies.csv"
    try:
        print(f"Próbuję zapisać anomalię do pliku: {file}")
        print(f"Obecny katalog roboczy: {os.getcwd()}")
        
        write_head = not os.path.exists(file)
        with open(file, "a", newline="") as f:
            writer = csv.writer(f)
            if write_head:
                writer.writerow(["timestamp", "symbol", "price", "volume"])
            writer.writerow([row.timestamp, row.symbol, row.price, row.volume])
            f.flush()
            os.fsync(f.fileno())
        print(f"✅ Zapisano anomalię do {file}")
    except Exception as e:
        print(f"❌ Błąd zapisu: {e}")
        import traceback
        traceback.print_exc()

def detect_and_alert(row):
    try:
        print(f"\n--- Przetwarzanie rekordu: {row.symbol} ---")
        
        if TEST_MODE and row.symbol == "BTCUSDT":
            print("🧪 Tryb testowy aktywny: wymuszona anomalia dla BTCUSDT")
            log_anomaly(row)
            try:
                subs = load_subscribers()
                if subs:
                    body = (f"🚨 Anomalia wykryta przez Isolation Forest\n"
                            f"Symbol: {row.symbol}\n"
                            f"Cena: {row.price}\n"
                            f"Volume: {row.volume}")
                    send_email_alert("Alert krypto", body, subs)
                    print("📧 Alert email wysłany.")
            except Exception as e:
                print(f"Błąd wysyłania alertu: {e}")
            return
            
        sid = symbol_mapping.get(row.symbol, -1)
        if sid is None:
            print(f"⚠️ Nieznany symbol: {row.symbol}")
            return
        
        x_raw = [[
            row.price,
            row.volume,
            row.priceChangePercent,
            row.weightedAvgPrice,
            row.count,
            sid
        ]]

        print(f"Dane wejściowe: {x_raw}")
        
        x = scaler.transform(x_raw)
        prediction = model.predict(x)[0]
        
        if prediction == -1:
            log_anomaly(row)
            try:
                subs = load_subscribers()
                if subs:
                    body = (f"🚨 Anomalia wykryta przez Isolation Forest\n"
                            f"Symbol: {row.symbol}\n"
                            f"Cena: {row.price}\n"
                            f"Volume: {row.volume}")
                    send_email_alert("Alert krypto", body, subs)
                    print("📧 Alert email wysłany.")
            except Exception as e:
                print(f"Błąd wysyłania alertu: {e}")
    except Exception as e:
        print(f"BŁĄD: {str(e)}")
        import traceback
        traceback.print_exc()

# ---------- uruchamiamy stream ----------
print("Uruchamiam stream detekcji anomalii...")
(json_df.writeStream
        .foreach(detect_and_alert)
        .outputMode("append")
        .trigger(processingTime='30 seconds')
        .start()
        .awaitTermination())