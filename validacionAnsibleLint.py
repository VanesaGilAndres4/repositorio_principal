import subprocess
import json
import os

def ejecutar_ansible_lint(ruta_repositorio):
    """
    Ejecuta ansible-lint en la ruta especificada y devuelve la salida JSON.
    """
    # Usamos -f json para obtener una salida estructurada que es fácil de parsear.
    # El comando se ejecuta en el directorio del repositorio.
    comando = ["ansible-lint", "-f", "json", "."]
    
    try:
        # Ejecutamos el comando y capturamos la salida y los errores
        resultado = subprocess.run(
            comando,
            cwd=ruta_repositorio,
            capture_output=True,
            text=True,
            check=False # No lanzar excepción si el linting falla (código de retorno != 0)
        )
        
        # ansible-lint escribe los resultados en stdout, incluso si son errores.
        output = resultado.stdout
        # Los errores de ejecución (como comando no encontrado) irían a stderr.
        if resultado.stderr:
            print(f"Errores de ejecución (stderr): {resultado.stderr}")
            
        return output

    except FileNotFoundError:
        print("Error: 'ansible-lint' no se encontró. Asegúrate de que esté instalado y en tu PATH.")
        return None
    except Exception as e:
        print(f"Ocurrió un error inesperado al ejecutar ansible-lint: {e}")
        return None

def parsear_errores(output_json):
    """
    Parsea la salida JSON de ansible-lint y extrae los errores.
    """
    if not output_json:
        return []

    try:
        # La salida es una lista de objetos JSON, donde cada objeto es un error o advertencia.
        datos = json.loads(output_json)
        # Puedes filtrar solo los errores si es necesario. La salida JSON incluye todos los resultados.
        return datos

    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        print(f"Salida cruda que causó el error: {output_json[:500]}...") # Imprimir parte de la salida para depurar
        return []

def mostrar_errores(lista_errores):
    """
    Imprime los errores de manera legible.
    """
    if not lista_errores:
        print("¡No se encontraron errores de ansible-lint!")
        return

    print(f"Se encontraron {len(lista_errores)} problemas:")
    for i, error in enumerate(lista_errores, 1):
        # La estructura JSON puede variar ligeramente, pero estos campos son comunes
        print(f"--- Problema {i} ---")
        print(f"Archivo: {error.get('filename', 'N/A')}")
        print(f"Línea: {error.get('linenumber', 'N/A')}")
        print(f"Regla: {error.get('rule_id', 'N/A')} ({error.get('rule_description', 'N/A')})")
        print(f"Severidad: {error.get('severity', 'N/A')}")
        print(f"Descripción: {error.get('message', 'N/A')}")
        print("-" * 20)

if __name__ == "__main__":
    #Ruta del repositorio
    REPO_PATH = "." 
    
    # Ejecutar y capturar salida
    salida_raw = ejecutar_ansible_lint(REPO_PATH)
    
    if salida_raw:
        # Parsear la salida JSON
        errores = parsear_errores(salida_raw)
        
        # Mostrar los resultados
        mostrar_errores(errores)
