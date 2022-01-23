# Server
cd C:\Users\Nhay103\Documents\GitHub\STSV\server
conda activate rectinet
python server.py

# Client
cd C:\Users\Nhay103\Documents\GitHub\STSV\client
conda activate rectinet
streamlit run app.py <ngrok>

# Ngrok
ngrok tcp 8251