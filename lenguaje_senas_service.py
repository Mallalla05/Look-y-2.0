"""
Servicio optimizado de reconocimiento de señas
Modo ESTÁTICO + DINÁMICO con alta estabilidad
"""

import cv2
import mediapipe as mp
import numpy as np
import pickle
import joblib
import os
import sys
import warnings
import time

from collections import deque, Counter

warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


class SignLanguageRecognizer:
    def __init__(self):
        print("🔧 Inicializando reconocedor optimizado...")

        # ===============================
        #  Carga de modelos
        # ===============================
        self.static_model = None
        self.dynamic_model = None
        self.dynamic_classes = None

        self._load_static()
        self._load_dynamic()

        if not self.static_model and not self.dynamic_model:
            raise Exception("No se encontraron modelos")

        # ===============================
        #   Mediapipe — Más precisión
        # ===============================
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.75,  # ↑ antes 0.5
            min_tracking_confidence=0.75    # ↑ antes 0.5
        )

        # ===============================
        # Variables internas
        # ===============================
        self.previous_landmarks = None
        self.motion_scores = deque(maxlen=15)
        self.MOTION_THRESHOLD = 0.045   # ↑ más robusto

        # Static mode
        self.prediction_buffer = deque(maxlen=12)  # ↑ más estable
        self.last_letter = None
        self.letter_hold_start = 0
        self.HOLD_TIME = 0.50  # ↓ más rápido

        # Result text
        self.spelled_text = ""

        # Dynamic mode
        self.sequence_buffer = deque(maxlen=30)
        self.last_word = None
        self.last_word_time = 0
        self.WORD_COOLDOWN = 1.5  # ↑ evitar spam
        self.DYNAMIC_CONFIDENCE = 0.80  # ↑ más seguro

        # Mode
        self.active_mode = "static"

        print("✅ Modelo listo")

    # ====================================
    #        CARGA MODELOS
    # ====================================

    def _load_static(self):
        try:
            file = "model.joblib" if os.path.exists("model.joblib") else "model.p"

            if os.path.exists(file):
                if file.endswith(".joblib"):
                    data = joblib.load(file)
                    self.static_model = data["model"]
                else:
                    with open(file, "rb") as f:
                        data = pickle.load(f)
                        self.static_model = data["model"]

                print("✅ Modelo estático cargado")
        except:
            print("⚠️ No se pudo cargar modelo estático")

    def _load_dynamic(self):
        try:
            import tensorflow as tf

            if os.path.exists("sequence_model.h5") and os.path.exists("label_encoder.npy"):
                self.dynamic_model = tf.keras.models.load_model("sequence_model.h5")
                self.dynamic_classes = np.load("label_encoder.npy", allow_pickle=True)
                print("✅ Modelo dinámico cargado")
        except:
            print("⚠️ No se pudo cargar modelo dinámico")

    # ====================================
    #        PROCESAR FRAME
    # ====================================

    def process_frame(self, frame):
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frameRGB)

        detected = results.multi_hand_landmarks is not None

        # ====================================
        #      DETECCIÓN DE MOVIMIENTO
        # ====================================
        if detected:
            hand = results.multi_hand_landmarks[0]
            now_landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand.landmark])

            if self.previous_landmarks is not None:
                dist = np.mean(np.sqrt(np.sum((now_landmarks - self.previous_landmarks)**2, axis=1)))
                self.motion_scores.append(dist)

            self.previous_landmarks = now_landmarks
        else:
            self.motion_scores.clear()

        # ======================
        #   Elegir modo
        # ======================
        if len(self.motion_scores) >= 5:
            avg = np.mean(self.motion_scores)

            if avg > self.MOTION_THRESHOLD and self.dynamic_model:
                if self.active_mode != "dynamic":
                    self.active_mode = "dynamic"
                    self.prediction_buffer.clear()
            else:
                if self.active_mode != "static":
                    self.active_mode = "static"
                    self.sequence_buffer.clear()

        # ======================
        #   MODO ESTÁTICO
        # ======================
        confidence = 0

        if detected and self.active_mode == "static" and self.static_model:
            hand = results.multi_hand_landmarks[0]

            lm = np.array([[lm.x, lm.y] for lm in hand.landmark])
            lm -= lm[0]
            maxv = np.max(np.abs(lm))
            if maxv != 0:
                lm /= maxv
            lm = lm.flatten()

            if lm.shape == (42,):
                pred = self.static_model.predict([lm])[0]
                proba = self.static_model.predict_proba([lm])[0]
                confidence = np.max(proba)

                if confidence >= 0.50:  # ↑ antes 0.25
                    self.prediction_buffer.append(pred)

                # === smoothing ===
                if len(self.prediction_buffer) >= 8:
                    most = Counter(self.prediction_buffer).most_common(1)[0]
                    letter = most[0]

                    now = time.time()
                    if letter == self.last_letter:
                        if now - self.letter_hold_start >= self.HOLD_TIME:
                            if not self.spelled_text.endswith(letter):
                                self.spelled_text += letter
                                self.last_letter = None
                    else:
                        self.last_letter = letter
                        self.letter_hold_start = now

        # ======================
        #   MODO DINÁMICO
        # ======================
        elif detected and self.active_mode == "dynamic" and self.dynamic_model:

            # Extraer features del frame
            hand = results.multi_hand_landmarks[0]
            lm = np.array([[lm.x, lm.y, lm.z] for lm in hand.landmark])
            lm -= lm[0]
            maxv = np.max(np.abs(lm))
            if maxv != 0:
                lm /= maxv
            lm = lm.flatten().tolist()

            if len(lm) < 126:
                lm += [0] * (126 - len(lm))

            self.sequence_buffer.append(lm[:126])

            # Solo predecir con ventana completa
            if len(self.sequence_buffer) == 30:
                now = time.time()
                if now - self.last_word_time > self.WORD_COOLDOWN:
                    seq = np.array([list(self.sequence_buffer)])
                    preds = self.dynamic_model.predict(seq, verbose=0)[0]
                    idx = np.argmax(preds)
                    confidence = preds[idx]

                    if confidence >= self.DYNAMIC_CONFIDENCE:
                        word = self.dynamic_classes[idx]

                        if not self.spelled_text.endswith(word):
                            if self.spelled_text and not self.spelled_text.endswith(" "):
                                self.spelled_text += " "
                            self.spelled_text += word

                        self.last_word = word
                        self.last_word_time = now

        return {
            "text": self.spelled_text,
            "mode": self.active_mode,
            "confidence": round(float(confidence) * 100, 2)
        }

    # ======================
    def reset(self):
        self.spelled_text = ""
        self.prediction_buffer.clear()
        self.sequence_buffer.clear()
        self.last_letter = None
        self.last_word = None
