// Look-y Cart - Arduino Final (Modo Automático Mejorado)
// IMPORTANTE: Desconecta Pin 0 antes de programar, luego reconéctalo

#define IN1 8
#define IN2 9
#define IN3 10
#define IN4 11
#define ENA 5
#define ENB 6
#define TRIG 12
#define ECHO 13

const float DISTANCIA_OBSTACULO = 15.0;
const float DISTANCIA_SEGURO = 10.0;
const float DISTANCIA_PELIGRO = 6.0;
const unsigned long TIEMPO_AVANCE = 3000;
const unsigned long TIEMPO_GIRO = 400;

unsigned long tiempoAvance = 0;
unsigned long ultimaDeteccion = 0;
bool modoAutonomo = false;
bool obstaculoDetectado = false;
int velocidadActual = 120;

void setup() {
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT); pinMode(ENB, OUTPUT);
  pinMode(TRIG, OUTPUT); pinMode(ECHO, INPUT);
  
  Serial.begin(9600);
  detener();
  
  delay(1000);
  Serial.println("READY");
  Serial.println("LOOK-Y - MODO SEGURO ACTIVADO");
  
  tiempoAvance = millis();
}

void loop() {
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();
    
    if (comando.length() > 0) {
      procesarComando(comando);
    }
  }
  
  if (modoAutonomo) {
    funcionAutonoma();
  }
  
  delay(10);
}

void procesarComando(String comando) {
  if (comando.startsWith("CMD:")) {
    comando = comando.substring(4);
    
    int separador = comando.indexOf(':');
    if (separador > 0) {
      String direccion = comando.substring(0, separador);
      int velocidad = comando.substring(separador + 1).toInt();
      
      velocidadActual = map(velocidad, 0, 100, 0, 255);
      
      if (direccion == "ADELANTE") {
        avanzar(velocidadActual);
        Serial.println("OK:ADELANTE");
      }
      else if (direccion == "ATRAS") {
        retroceder(velocidadActual);
        Serial.println("OK:ATRAS");
      }
      else if (direccion == "IZQUIERDA") {
        girarIzquierda(velocidadActual);
        Serial.println("OK:IZQUIERDA");
      }
      else if (direccion == "DERECHA") {
        girarDerecha(velocidadActual);
        Serial.println("OK:DERECHA");
      }
      else if (direccion == "DETENER" || direccion == "STOP") {
        detener();
        Serial.println("OK:STOP");
      }
    }
  }
  else if (comando.startsWith("MODE:AUTO:")) {
    if (comando.endsWith("ON")) {
      modoAutonomo = true;
      tiempoAvance = millis();
      obstaculoDetectado = false;
      Serial.println("AUTO:ON");
    } else {
      modoAutonomo = false;
      detener();
      Serial.println("AUTO:OFF");
    }
  }
}

void funcionAutonoma() {
  float distancia = medirDistancia();
  
  // Verificación múltiple para mayor precisión
  for(int i = 0; i < 2; i++) {
    float distVerificacion = medirDistancia();
    if(distVerificacion < distancia) {
      distancia = distVerificacion;
    }
    delay(10);
  }
  
  Serial.print("📏 ");
  if (distancia < 50) {
    Serial.print(distancia, 1);
    Serial.println(" cm");
  } else {
    Serial.println("Libre");
  }
  
  // PELIGRO INMEDIATO - Retroceso de emergencia
  if (distancia < DISTANCIA_PELIGRO && distancia > 2.0) {
    Serial.println("⚠️ PELIGRO! Retroceso EMERGENCIA");
    retrocederRapido();
    delay(600);
    girarIzquierda(150);  // INVERTIDO: era Derecha
    delay(800);
    detener();
    tiempoAvance = millis();
    obstaculoDetectado = true;
    return;
  }
  
  // OBSTÁCULO CERCA - Evitar
  if (distancia < DISTANCIA_SEGURO && distancia > 2.0) {
    Serial.println("⚠️ Obstáculo CERCA - Evitando...");
    detener();
    delay(200);
    girarIzquierda(150);  // INVERTIDO: era Derecha
    delay(600);
    detener();
    tiempoAvance = millis();
    obstaculoDetectado = true;
    return;
  }
  
  // OBSTÁCULO DETECTADO - Buscar mejor camino
  if (distancia < DISTANCIA_OBSTACULO && distancia > 2.0) {
    if (!obstaculoDetectado) {
      Serial.println("🔍 Obstáculo detectado - Buscando camino...");
      detener();
      delay(300);
      buscarMejorCamino();
      obstaculoDetectado = true;
    }
    return;
  }
  
  // Camino libre
  obstaculoDetectado = false;
  
  // Cambio de dirección programado
  if (millis() - tiempoAvance > TIEMPO_AVANCE) {
    Serial.println("🔄 Cambio de dirección programado");
    detener();
    delay(200);
    girarIzquierda(150);  // INVERTIDO: era Derecha
    delay(TIEMPO_GIRO);
    detener();
    delay(200);
    tiempoAvance = millis();
  } else {
    avanzarSuave();
  }
}

void buscarMejorCamino() {
  Serial.println("🔍 Evaluando caminos...");
  
  // Mirar a la IZQUIERDA (INVERTIDO: era derecha)
  girarIzquierda(150);
  delay(400);
  detener();
  delay(300);
  float distIzquierda = medirDistanciaRapido();
  Serial.print("⬅️ Izquierda: "); Serial.print(distIzquierda); Serial.println("cm");
  
  // Mirar a la DERECHA (INVERTIDO: era izquierda)
  girarDerecha(150);
  delay(800);
  detener();
  delay(300);
  float distDerecha = medirDistanciaRapido();
  Serial.print("➡️ Derecha: "); Serial.print(distDerecha); Serial.println("cm");
  
  // Volver al centro
  girarIzquierda(150);
  delay(400);
  detener();
  delay(300);
  
  float margenSeguridad = 5.0;
  
  bool izquierdaBuena = (distIzquierda - distDerecha) > margenSeguridad;
  bool derechaBuena = (distDerecha - distIzquierda) > margenSeguridad;
  
  if (izquierdaBuena && distIzquierda > 20) {
    Serial.println("✅ Girando IZQUIERDA");
    girarIzquierda(150);
    delay(600);
  } else if (derechaBuena && distDerecha > 20) {
    Serial.println("✅ Girando DERECHA");
    girarDerecha(150);
    delay(600);
  } else {
    Serial.println("🔙 Retrocediendo y giro aleatorio");
    retroceder(180);
    delay(800);
    if(random(2) == 0) {
      girarIzquierda(150);
    } else {
      girarDerecha(150);
    }
    delay(1000);
  }
  
  detener();
  delay(400);
  tiempoAvance = millis();
}

void avanzarSuave() {
  digitalWrite(IN1, HIGH);  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);  digitalWrite(IN4, LOW);
  analogWrite(ENA, 120); analogWrite(ENB, 120);
}

void avanzar(int velocidad) {
  digitalWrite(IN1, HIGH);  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);  digitalWrite(IN4, LOW);
  analogWrite(ENA, velocidad);
  analogWrite(ENB, velocidad);
}

void retroceder(int velocidad) {
  digitalWrite(IN1, LOW);   digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);   digitalWrite(IN4, HIGH);
  analogWrite(ENA, velocidad);
  analogWrite(ENB, velocidad);
}

void retrocederRapido() {
  digitalWrite(IN1, LOW);   digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);   digitalWrite(IN4, HIGH);
  analogWrite(ENA, 200); analogWrite(ENB, 200);
}

// INVERTIDAS: Derecha <-> Izquierda
void girarDerecha(int velocidad) {
  digitalWrite(IN1, LOW);   digitalWrite(IN2, HIGH);  // INVERTIDO
  digitalWrite(IN3, HIGH);  digitalWrite(IN4, LOW);   // INVERTIDO
  analogWrite(ENA, velocidad);
  analogWrite(ENB, velocidad);
}

void girarIzquierda(int velocidad) {
  digitalWrite(IN1, HIGH);  digitalWrite(IN2, LOW);   // INVERTIDO
  digitalWrite(IN3, LOW);   digitalWrite(IN4, HIGH);  // INVERTIDO
  analogWrite(ENA, velocidad);
  analogWrite(ENB, velocidad);
}

void detener() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  analogWrite(ENA, 0); analogWrite(ENB, 0);
}

float medirDistancia() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  
  long duracion = pulseIn(ECHO, HIGH, 20000);
  if (duracion == 0) return 100.0;
  
  float distancia = duracion * 0.034 / 2;
  return (distancia < 2.0 || distancia > 400.0) ? 100.0 : distancia;
}

float medirDistanciaRapido() {
  return medirDistancia();
}