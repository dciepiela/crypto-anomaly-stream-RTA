🧠 Crypto Anomaly Detector – Isolation Forest + Kafka + Streamlit

System do wykrywania anomalii w danych rynkowych kryptowalut w czasie rzeczywistym, z wykorzystaniem:

🌐 danych z Binance API

📊 wykresów na Streamlit

🛰 Apache Kafka do przesyłania danych

⚡ Apache Spark do strumieniowego przetwarzania

🌲 Isolation Forest do detekcji anomalii

📬 alertów e-mail dla subskrybentów


📌 Funkcje

✅ Pobieranie danych dla 10 popularnych kryptowalut co 30 sekund

✅ Detekcja anomalii w cenie, wolumenie i zmienności

✅ Dashboard z wykresami anomalii i danych cenowych

✅ Obsługa subskrypcji e-mailowych (alerty)

✅ System oparty o Dockera i Kafka Streaming (Spark Structured Streaming)

🧪 Technologie
 - Dane źródłowe	Binance API (REST)
 - Strumień danych	Apache Kafka + Zookeeper
 - Przetwarzanie	Apache Spark (Structured Streaming)
 - Wykrywanie anomalii	Isolation Forest (scikit-learn)
 - Wizualizacja	Streamlit + Plotly
 - Alerty	SMTP e-mail
 - Opakowanie	Docker + docker-compose

📈 Monitorowane symbole
  - BTCUSDT (Bitcoin)
  - ETHUSDT (Ethereum)
  - BNBUSDT (Binance Coin)
  - DOGEUSDT (Dogecoin)
  - XRPUSDT (Ripple)
  - SHIBUSDT (Shiba Inu)
  - ADAUSDT (Cardano)
  - ARBUSDT (Arbitrum)
  - MATICUSDT (Polygon)
  - SOLUSDT (Solana)


🚀 Uruchomienie
1. Wytrenuj model offline:
pip install -r requirements.txt
python train_isolation_forest.py

Tworzy pliki:
- isolation_forest_model.pkl
- standard_scaler.pkl

2. Utwórz plik .env z hasłem aplikacji Gmail (do alertów mailowych):
   Utwórz plik .env w katalogu głównym i wklej:
   - EMAIL_ADDRESS=twoj_email@gmail.com
   - EMAIL_APP_PASSWORD=haslo_aplikacji
   
   🔐 Uwaga: Hasło aplikacji uzyskasz z: https://myaccount.google.com/apppasswords
   Wymagana jest włączona weryfikacja dwuetapowa.
3. Zbuduj i uruchom kontenery:
   - docker-compose build
   - docker-compose up

4. Otwórz dashboard w przeglądarce:
   👉 http://localhost:8502
