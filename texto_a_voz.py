import pyttsx3
import sys
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def hablar(texto):
    try:
        engine = pyttsx3.init()
        
        # Configurar propiedades de voz
        engine.setProperty('rate', 170)    # Velocidad
        engine.setProperty('volume', 0.8)  # Volumen
        
        # Buscar voces en español
        voces = engine.getProperty('voices')
        voz_espanol = None
        
        for voz in voces:
            if 'spanish' in voz.name.lower() or 'espanol' in voz.name.lower():
                voz_espanol = voz.id
                break
            elif 'microsoft david' in voz.name.lower() or 'microsoft zira' in voz.name.lower():
                voz_espanol = voz.id
        
        if voz_espanol:
            engine.setProperty('voice', voz_espanol)
        
        print(f"Convirtiendo a voz: '{texto}'")
        engine.say(texto)
        engine.runAndWait()
        return f"Texto convertido a voz exitosamente: {texto}"
        
    except Exception as e:
        return f"ERROR: Error en texto a voz: {str(e)}"

def main():
    # Verificar argumentos
    if len(sys.argv) > 1:
        # Modo automático desde servidor
        texto = sys.argv[1]
    else:
        # Modo interactivo
        texto = input("Escribe el texto a convertir a voz: ")
        if texto.lower() == 'salir':
            print("Programa terminado.")
            return
    
    resultado = hablar(texto)
    print(resultado)

if __name__ == "__main__":
    main()