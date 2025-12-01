from googletrans import Translator
import pyttsx3
import sys
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def traducir_texto(texto, idioma_destino):
    try:
        traductor = Translator()
        traduccion = traductor.translate(texto, dest=idioma_destino)
        return traduccion.text
    except Exception as e:
        return f"ERROR: Error en traduccion: {str(e)}"

def hablar_texto(texto):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 170)
        engine.setProperty('volume', 0.8)
        engine.say(texto)
        engine.runAndWait()
        return True
    except Exception as e:
        print(f"Error en texto a voz: {e}")
        return False

def modo_automatico(idioma_destino, texto):
    """Modo para cuando se llama desde el servidor"""
    if texto and texto.strip():
        traduccion = traducir_texto(texto.strip(), idioma_destino)
        
        if not traduccion.startswith("ERROR:"):
            if hablar_texto(traduccion):
                print(f"RESULTADO:{traduccion}")
            else:
                print("ERROR: No se pudo convertir a voz")
        else:
            print(f"ERROR:{traduccion}")
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
    print("Traductor de texto a voz")
    print("Ejemplo de idiomas: en (ingles), fr (frances), de (aleman), ja (japones), it (italiano)")
    print("Escribe 'salir' para terminar.\n")

    idioma_destino = input("Ingresa el codigo del idioma destino: ").strip()

    while True:
        texto = input("\nEscribe el texto a traducir: ")
        if texto.lower() == "salir":
            print("Programa terminado.")
            break

        traduccion = traducir_texto(texto, idioma_destino)
        print(f"Traduccion ({idioma_destino}): {traduccion}")

        if not traduccion.startswith("ERROR:"):
            hablar_texto(traduccion)

if __name__ == "__main__":
    main()