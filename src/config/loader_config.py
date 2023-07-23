import os
import json

def load_config():
    # Obtiene la ruta absoluta del archivo config.json en la carpeta raíz del proyecto
    root_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(root_path, "config.json")

    # Verifica si el archivo config.json existe antes de intentar cargarlo
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"El archivo {config_path} no fue encontrado.")

    # Lee los valores del archivo de configuración.
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    return config