#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "INFINITUM1773";
const char* password = "kd7c9PnD9c";
const char* mqtt_server = "192.168.1.84";
const int mqtt_port = 1883;

String clientId = "LookyCart_";

const char* topic_control = "looky/control";
const char* topic_status = "looky/status";
const char* topic_autonomo = "looky/autonomo";
const char* topic_emergencia = "looky/emergencia";

HardwareSerial ArduinoSerial(2);

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastReconnectAttempt = 0;
unsigned long tiempoUltimoComando = 0;
unsigned long lastStatusPrint = 0;
const unsigned long TIMEOUT_AUTONOMO = 3000;
bool modoAutonomo = false;

void setup() {
  Serial.begin(115200);
  ArduinoSerial.begin(9600, SERIAL_8N1, 16, 17);
  delay(2000);
  
  Serial.println("\n🚀 Look-y Cart ESP32");
  
  uint64_t chipid = ESP.getEfuseMac();
  clientId += String((uint32_t)(chipid >> 32), HEX);
  
  Serial.print("ID: ");
  Serial.println(clientId);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  Serial.print("WiFi...");
  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos < 30) {
    delay(500);
    Serial.print(".");
    intentos++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println(" ✓");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
    
    client.setServer(mqtt_server, mqtt_port);
    client.setCallback(callback);
    
    reconnect();
  } else {
    Serial.println(" ✗");
  }
  
  Serial.println("Sistema listo\n");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.reconnect();
    delay(5000);
    return;
  }
  
  if (!client.connected()) {
    if (millis() - lastReconnectAttempt > 5000) {
      lastReconnectAttempt = millis();
      reconnect();
    }
  } else {
    client.loop();
  }
  
  if (millis() - lastStatusPrint > 10000) {
    lastStatusPrint = millis();
    Serial.print("WiFi:");
    Serial.print(WiFi.status() == WL_CONNECTED ? "OK" : "X");
    Serial.print(" MQTT:");
    Serial.println(client.connected() ? "OK" : "X");
  }
  
  if (!modoAutonomo && tiempoUltimoComando > 0) {
    if (millis() - tiempoUltimoComando > TIMEOUT_AUTONOMO) {
      activarModoAutonomo();
    }
  }
  
  if (ArduinoSerial.available() > 0) {
    String respuesta = ArduinoSerial.readStringUntil('\n');
    respuesta.trim();
    
    if (respuesta.length() > 0) {
      Serial.print("🤖 ");
      Serial.println(respuesta);
      
      if (client.connected()) {
        client.publish(topic_status, respuesta.c_str());
      }
    }
  }
  
  delay(10);
}

void callback(char* topic, byte* payload, unsigned int length) {
  String mensaje = "";
  for (int i = 0; i < length; i++) {
    mensaje += (char)payload[i];
  }
  mensaje.trim();
  
  Serial.print("📨 [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(mensaje);
  
  if (String(topic) == topic_control) {
    procesarComandoControl(mensaje);
  }
  else if (String(topic) == topic_autonomo) {
    if (mensaje == "ON" || mensaje == "1") {
      activarModoAutonomo();
    } else {
      desactivarModoAutonomo();
    }
  }
  else if (String(topic) == topic_emergencia) {
    Serial.println("🚨 EMERGENCIA");
    ArduinoSerial.println("CMD:DETENER:0");
    desactivarModoAutonomo();
  }
}

void procesarComandoControl(String comando) {
  tiempoUltimoComando = millis();
  
  if (modoAutonomo) {
    desactivarModoAutonomo();
  }
  
  int separador = comando.indexOf(':');
  if (separador > 0) {
    String direccion = comando.substring(0, separador);
    int velocidad = comando.substring(separador + 1).toInt();
    velocidad = constrain(velocidad, 0, 100);
    
    String comandoArduino = "CMD:" + direccion + ":" + String(velocidad);
    
    Serial.print("→ ");
    Serial.println(comandoArduino);
    
    ArduinoSerial.println(comandoArduino);
  }
}

void activarModoAutonomo() {
  if (!modoAutonomo) {
    modoAutonomo = true;
    Serial.println("🤖 AUTO ON");
    ArduinoSerial.println("MODE:AUTO:ON");
    
    if (client.connected()) {
      client.publish(topic_status, "AUTO_ON");
      client.publish(topic_autonomo, "ON");
    }
  }
}

void desactivarModoAutonomo() {
  if (modoAutonomo) {
    modoAutonomo = false;
    Serial.println("👤 MANUAL");
    ArduinoSerial.println("MODE:AUTO:OFF");
    
    if (client.connected()) {
      client.publish(topic_status, "AUTO_OFF");
      client.publish(topic_autonomo, "OFF");
    }
  }
}

boolean reconnect() {
  Serial.print("MQTT...");
  
  if (client.connect(clientId.c_str(), NULL, NULL, topic_status, 0, true, "OFFLINE")) {
    Serial.println(" ✓");
    
    client.subscribe(topic_control);
    client.subscribe(topic_autonomo);
    client.subscribe(topic_emergencia);
    
    client.publish(topic_status, "ONLINE", true);
    
    return true;
  } else {
    Serial.print(" ✗ ");
    Serial.println(client.state());
    return false;
  }
}