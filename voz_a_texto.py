import speech_recognition as sr
import sys
import os
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def reconocer_voz():
    """Reconoce voz usando Google Speech Recognition"""
    recognizer = sr.Recognizer()
    
    try:
        # Configurar micrófono
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)
            
            # Escuchar audio
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
            
        # Reconocer usando Google
        texto = recognizer.recognize_google(audio, language="es-ES")
        return texto
        
    except sr.WaitTimeoutError:
        return "ERROR: Tiempo de espera agotado. No se detecto voz."
    except sr.UnknownValueError:
        return "ERROR: No se pudo entender el audio."
    except sr.RequestError as e:
        return f"ERROR: Error en el servicio: {e}"
    except Exception as e:
        return f"ERROR: Error inesperado: {e}"

def main():
    # Modo automático (desde servidor)
    if len(sys.argv) > 1:
        print("Modo automatico activado")
        resultado = reconocer_voz()
        print(f"RESULTADO:{resultado}")
        return
    
    # Modo interactivo
    print("Reconocimiento de Voz")
    print("Di 'salir' para terminar\n")
    
    while True:
        input("Presiona Enter para empezar a grabar...")
        
        texto = reconocer_voz()
        
        if texto and "salir" in texto.lower():
            print("Saliendo del programa...")
            break

if __name__ == "__main__":
    main()