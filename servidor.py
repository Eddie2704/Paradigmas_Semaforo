from flask import Flask, request
from flask_cors import CORS 
import threading

app = Flask(__name__)
CORS(app) 

ultimo_evento = None
lock = threading.Lock()

@app.route("/evento", methods=["POST"])
def evento():
    global ultimo_evento
    
    
    dato = request.data.decode("utf-8")
    
    with lock:
        ultimo_evento = dato
        
    print(f"--- Evento recibido en Flask: {dato} ---")
    return "OK", 200 


def iniciar():
    hilo = threading.Thread(
        target=lambda: app.run(
            host="0.0.0.0",
            port=5000,
            debug=False,
            use_reloader=False
        ),
        daemon=True
    )
    hilo.start()


def leer():
    global ultimo_evento
    with lock:
        dato = ultimo_evento
        ultimo_evento = None
    return dato