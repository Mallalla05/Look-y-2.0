import speech_recognition as sr
from googletrans import Translator
import pyttsx3
import sys
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def reconocer_voz():
    """Reconoce voz del usuario"""
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("Escuchando... Habla ahora")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
            
        texto = recognizer.recognize_google(audio, language="es-ES")
        print(f"Dijiste: {texto}")
        return texto
        
    except sr.WaitTimeoutError:
        return "ERROR: Tiempo de espera agotado"
    except sr.UnknownValueError:
        return "ERROR: No se pudo entender el audio"
    except Exception as e:
        return f"ERROR: {str(e)}"

def traducir_y_hablar(texto, idioma_destino):
    try:
        # Traducir texto
        traductor = Translator()
        traduccion = traductor.translate(texto, dest=idioma_destino)
        texto_traducido = traduccion.text
        
        print(f"Traduccion ({idioma_destino}): {texto_traducido}")

        # Convertir a voz
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        engine.setProperty('volume', 0.8)
        engine.say(texto_traducido)
        engine.runAndWait()
        
        return texto_traducido
        
    except Exception as e:
        return f"ERROR: Error en traduccion: {str(e)}"

def modo_automatico(idioma_destino, texto):
    """Modo para cuando se llama desde el servidor"""
    if texto and texto.strip():
        resultado = traducir_y_hablar(texto.strip(), idioma_destino)
        print(f"RESULTADO:{resultado}")
    else:
        print("ERROR: No se recibio texto para traducir")

def main():
    # Verificar si se pasan argumentos (modo automático)
    if len(sys.argv) > 2:
        idioma_destino = sys.argv[1]
        texto = sys.argv[2]
        modo_automatico(idioma_destino, texto)
        return
    
    # Modo interactivo (original)
    recognizer = sr.Recognizer()
    
    try:
        mic = sr.Microphone()
        print("Ajustando al ruido ambiental...")
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Microfono listo")
    except Exception as e:
        print(f"Error con el microfono: {e}")
        return

    idioma_destino = input("Ingresa el codigo del idioma destino (ej. en, fr, de, ja, it): ").strip()

    print("\nHabla algo (di 'salir' para terminar):")
    while True:
        try:
            texto = reconocer_voz()
            
            if "salir" in texto.lower():
                print("Saliendo del programa...")
                break
                
            if not texto.startswith("ERROR:"):
                traducir_y_hablar(texto, idioma_destino)

        except KeyboardInterrupt:
            print("\nPrograma interrumpido manualmente.")
            break

if __name__ == "__main__":
    main()