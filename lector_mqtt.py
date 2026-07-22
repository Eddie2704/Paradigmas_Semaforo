# lector_mqtt.py
import paho.mqtt.client as mqtt
import threading

# Configuración idéntica al código de la ESP32 en Wokwi
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "unah/semaforo/eventos"

ultimo_evento = None
lock = threading.Lock()

def al_recibir_mensaje(client, userdata, msg):
    global ultimo_evento
    dato = msg.payload.decode("utf-8")
    with lock:
        ultimo_evento = dato
    print(f"--- Evento recibido vía MQTT: {dato} ---")

def iniciar():
    # Usamos la versión de API más reciente y recomendada por Paho MQTT
    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    cliente.on_message = al_recibir_mensaje
    
    try:
        cliente.connect(MQTT_BROKER, MQTT_PORT, 60)
        cliente.subscribe(MQTT_TOPIC)
        # Inicia el bucle de escucha de red en un hilo separado
        cliente.loop_start()
        print("[SISTEMA] Escucha MQTT activada y conectada al Broker.")
    except Exception as e:
        print(f"[ERROR MQTT] No se pudo conectar al Broker: {e}")

def leer():
    global ultimo_evento
    with lock:
        dato = ultimo_evento
        ultimo_evento = None
    return dato