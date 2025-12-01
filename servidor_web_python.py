from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import subprocess
import sys
import json
import os

app = Flask(__name__)
CORS(app)

# Sign language recognizer (lazy loading)
sign_recognizer = None

def get_sign_recognizer():
    """Inicializar el reconocedor de señas solo cuando se necesita"""
    global sign_recognizer
    if sign_recognizer is None:
        try:
            # Verificar que existen los modelos
            if not (os.path.exists('model.joblib') or os.path.exists('model.p')):
                print("⚠️  Advertencia: No se encontró modelo de señas estático")
                return None
            
            from lenguaje_senas_service import SignLanguageRecognizer
            sign_recognizer = SignLanguageRecognizer()
            print("✅ Reconocedor de señas inicializado")
        except Exception as e:
            print(f"❌ Error inicializando reconocedor de señas: {e}")
            return None
    return sign_recognizer

def ejecutar_script_python(script, argumentos=""):
    """Ejecuta los scripts Python según el comando recibido"""
    try:
        print(f"🧠 Ejecutando script: {script}")
        print(f"📦 Argumentos recibidos: {argumentos}")

        if script == "voz_a_texto":
            print("🎤 Ejecutando reconocimiento de voz...")
            resultado = subprocess.run(
                [sys.executable, "voz_a_texto.py"],
                capture_output=True, text=True, timeout=30
            )
            output = resultado.stdout.strip()
            print(f"📨 Output voz_a_texto: {output}")
            
            if output.startswith("RESULTADO:"):
                return output.replace("RESULTADO:", "").strip()
            return output if output else "🎤 Voz a texto completado"

        elif script == "texto_a_voz":
            print(f"🔊 Ejecutando texto a voz: '{argumentos}'")
            resultado = subprocess.run(
                [sys.executable, "texto_a_voz.py", argumentos],
                capture_output=True, text=True, timeout=30
            )
            output = resultado.stdout.strip()
            print(f"📨 Output texto_a_voz: {output}")
            return f"🔊 Texto convertido a voz: {argumentos}"

        elif script == "voz_traductor":
            try:
                datos = json.loads(argumentos)
                texto = datos.get('texto', '')
                idioma = datos.get('idioma', 'en')
                
                print(f"🎯 Traduciendo voz: '{texto}' a {idioma}")
                
                resultado = subprocess.run(
                    [sys.executable, "voz_traductor.py", idioma, texto],
                    capture_output=True, text=True, timeout=30
                )
                
                output = resultado.stdout.strip()
                error_output = resultado.stderr.strip()
                
                print(f"📨 Stdout voz_traductor: {output}")
                if error_output:
                    print(f"📨 Stderr voz_traductor: {error_output}")
                
                if output.startswith("RESULTADO:"):
                    return output.replace("RESULTADO:", "").strip()
                elif output.startswith("ERROR:"):
                    return output.replace("ERROR:", "").strip()
                elif output:
                    return output
                else:
                    return "🌐 Traducción de voz completada"
                    
            except subprocess.TimeoutExpired:
                return "❌ Error: Timeout en traducción de voz"
            except json.JSONDecodeError as e:
                return f"❌ Error: Formato JSON inválido - {str(e)}"
            except Exception as e:
                return f"❌ Error ejecutando traductor voz: {str(e)}"

        elif script == "texto_traducido":
            try:
                datos = json.loads(argumentos)
                texto = datos.get('texto', '')
                idioma = datos.get('idioma', 'en')
                
                print(f"🎯 Traduciendo texto: '{texto}' a {idioma}")
                
                resultado = subprocess.run(
                    [sys.executable, "texto_traducido_a_voz.py", idioma, texto],
                    capture_output=True, text=True, timeout=30
                )
                
                output = resultado.stdout.strip()
                error_output = resultado.stderr.strip()
                
                print(f"📨 Stdout texto_traducido: {output}")
                if error_output:
                    print(f"📨 Stderr texto_traducido: {error_output}")
                
                if output.startswith("RESULTADO:"):
                    return output.replace("RESULTADO:", "").strip()
                elif output.startswith("ERROR:"):
                    return output.replace("ERROR:", "").strip()
                elif output:
                    return output
                else:
                    return "📘 Traducción de texto completada"
                    
            except subprocess.TimeoutExpired:
                return "❌ Error: Timeout en traducción de texto"
            except json.JSONDecodeError as e:
                return f"❌ Error: Formato JSON inválido - {str(e)}"
            except Exception as e:
                return f"❌ Error ejecutando traductor texto: {str(e)}"

        else:
            return f"⚠️ Script no reconocido: {script}"

    except Exception as e:
        return f"❌ Error ejecutando script: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/voz_a_texto')
def voz_a_texto():
    return render_template('voz_a_texto.html')

@app.route('/texto_a_voz')
def texto_a_voz():
    return render_template('texto_a_voz.html')

@app.route('/voz_traductor')
def voz_traductor():
    return render_template('voz_traductor.html')

@app.route('/texto_traducido')
def texto_traducido():
    return render_template('texto_traducido.html')

@app.route('/lenguaje_senas')
def lenguaje_senas():
    return render_template('lenguaje_senas.html')

@app.route('/control_carro')
def control_carro():
    return render_template('control_carro.html')

@app.route('/ejecutar_voz_a_texto')
def ejecutar_voz_a_texto():
    respuesta = ejecutar_script_python("voz_a_texto")
    return respuesta

@app.route('/ejecutar_texto_a_voz', methods=['POST'])
def ejecutar_texto_a_voz():
    datos = request.get_json()
    texto = datos.get('texto', '')
    respuesta = ejecutar_script_python("texto_a_voz", texto)
    return respuesta

@app.route('/ejecutar_traductor_voz', methods=['POST'])
def ejecutar_traductor_voz():
    datos = request.get_json()
    argumentos_json = json.dumps(datos)
    respuesta = ejecutar_script_python("voz_traductor", argumentos_json)
    return respuesta

@app.route('/ejecutar_traductor_texto', methods=['POST'])
def ejecutar_traductor_texto():
    datos = request.get_json()
    argumentos_json = json.dumps(datos)
    respuesta = ejecutar_script_python("texto_traducido", argumentos_json)
    return respuesta

@app.route('/obtener_texto_senas')
def obtener_texto_senas():
    """Endpoint para obtener el texto reconocido de señas"""
    recognizer = get_sign_recognizer()
    if recognizer is None:
        return jsonify({
            'text': 'Error: Modelos no disponibles',
            'mode': 'error',
            'confidence': 0
        })
    
    try:
        return jsonify({
            'text': recognizer.get_text(),
            'mode': recognizer.active_mode,
            'confidence': 0
        })
    except Exception as e:
        return jsonify({
            'text': f'Error: {str(e)}',
            'mode': 'error',
            'confidence': 0
        })

@app.route('/procesar_frame_senas', methods=['POST'])
def procesar_frame_senas():
    """Endpoint para procesar frames de video en tiempo real"""
    recognizer = get_sign_recognizer()
    if recognizer is None:
        return jsonify({
            'text': 'Error: Modelos no disponibles',
            'mode': 'error',
            'confidence': 0
        })
    
    try:
        import cv2
        import numpy as np
        import base64
        
        # Get frame from request
        data = request.get_json()
        frame_data = data.get('frame', '')
        
        # Decode base64 image
        if frame_data.startswith('data:image'):
            frame_data = frame_data.split(',')[1]
        
        img_bytes = base64.b64decode(frame_data)
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # Process frame
        result = recognizer.process_frame(frame)
        
        return jsonify({
            'text': result['text'],
            'mode': result['mode'],
            'confidence': result['confidence']
        })
        
    except Exception as e:
        print(f"❌ Error procesando frame: {e}")
        return jsonify({
            'text': recognizer.get_text() if recognizer else '',
            'mode': 'error',
            'confidence': 0,
            'error': str(e)
        })

@app.route('/limpiar_texto_senas', methods=['POST'])
def limpiar_texto_senas():
    """Endpoint para limpiar el texto de señas"""
    recognizer = get_sign_recognizer()
    if recognizer:
        recognizer.reset()
        return jsonify({'status': 'ok', 'message': 'Texto limpiado'})
    return jsonify({'status': 'error', 'message': 'Reconocedor no disponible'})

# ============ CONTROL DEL CARRO ============
@app.route('/control_carro', methods=['POST'])
def enviar_control_carro():
    """Endpoint para enviar comandos de control al carro"""
    try:
        datos = request.get_json()
        direccion = datos.get('direccion', '')
        velocidad = datos.get('velocidad', 50)
        
        print(f"🚗 Control Carro: {direccion} @ {velocidad}%")
        
        # Aquí iría la lógica para enviar al ESP32 vía serial
        # Por ejemplo: serial.write(f"MOVE:{direccion}:{velocidad}\n".encode())
        
        return jsonify({
            'status': 'ok',
            'mensaje': f'Comando enviado: {direccion}',
            'direccion': direccion,
            'velocidad': velocidad
        })
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)})

@app.route('/modo_autonomo', methods=['POST'])
def modo_autonomo():
    """Activar/desactivar modo autónomo"""
    try:
        datos = request.get_json()
        activado = datos.get('activado', False)
        
        print(f"🤖 Modo autónomo: {'ACTIVADO' if activado else 'DESACTIVADO'}")
        
        # Aquí iría la lógica para activar modo autónomo en el ESP32
        
        return jsonify({
            'status': 'ok',
            'modo_autonomo': activado
        })
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)})

@app.route('/emergencia', methods=['POST'])
def emergencia():
    """Parada de emergencia"""
    try:
        print("🚨 PARADA DE EMERGENCIA ACTIVADA")
        
        # Aquí iría la lógica para detener el carro inmediatamente
        
        return jsonify({
            'status': 'ok',
            'mensaje': 'Parada de emergencia activada'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)})

@app.route('/actualizar_velocidad', methods=['POST'])
def actualizar_velocidad():
    """Actualizar velocidad del carro"""
    try:
        datos = request.get_json()
        velocidad = datos.get('velocidad', 50)
        
        print(f"⚡ Velocidad actualizada: {velocidad}%")
        
        return jsonify({
            'status': 'ok',
            'velocidad': velocidad
        })
    except Exception as e:
        return jsonify({'status': 'error', 'mensaje': str(e)})

@app.route('/estado_carro')
def estado_carro():
    """Obtener estado del carro (batería, señal, etc.)"""
    import random
    
    # En producción, esto vendría del ESP32
    return jsonify({
        'bateria': random.randint(70, 95),
        'senal': random.choice(['Excelente', 'Buena', 'Regular']),
        'temperatura': random.randint(20, 35),
        'estado': 'activo'
    })

if __name__ == '__main__':
    import os
    
    print("🚀 Iniciando servidor web Look-y...")
    
    # Detectar si tenemos pyOpenSSL/cryptography para SSL
    ssl_available = False
    try:
        import OpenSSL
        import cryptography
        ssl_available = True
    except ImportError:
        pass
    
    # Intentar usar SSL si está disponible
    if ssl_available:
        try:
            print("🔒 Iniciando con HTTPS...")
            print("🌐 Servidor corriendo en: https://localhost:5000")
            print("📱 Desde tu teléfono: https://[IP_DE_TU_PC]:5000")
            print("💡 Acepta el certificado autofirmado cuando lo pida\n")
            app.run(host='0.0.0.0', port=5000, ssl_context='adhoc', debug=True)
        except Exception as e:
            print(f"⚠️  No se pudo iniciar HTTPS: {e}")
            print("🌐 Iniciando con HTTP normal...\n")
            print("🌐 Servidor corriendo en: http://localhost:5000")
            print("📱 Desde tu teléfono: http://[IP_DE_TU_PC]:5000")
            print("⚠️  Para permisos de cámara/micrófono usa localhost\n")
            app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("🌐 Servidor corriendo en: http://localhost:5000")
        print("📱 Desde tu teléfono: http://[IP_DE_TU_PC]:5000")
        print("💡 Para HTTPS instala: pip install pyopenssl cryptography")
        print("⚠️  Para permisos de cámara/micrófono usa localhost\n")
        app.run(host='0.0.0.0', port=5000, debug=True)