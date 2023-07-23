import subprocess
import requests
import re
import os

# Anotación de tipo para marcar las funciones que deben estar disponibles en el teclado
def keyboard_function(func):
    func.keyboard = True
    return func
    
class NgrokExecutor:
    def __init__(self):
        # Inicializa una variable para almacenar la instancia de logging
        self.logger = None
        
    # Método setter para establecer la instancia de logging
    def set_logger(self, logger):
        self.logger = logger
        
    # Obtiene las funciones marcadas con la anotación @keyboard_function
    def get_available_functions(self):
        keyboard_functions = [
            func_name for func_name, func in NgrokExecutor.__dict__.items() 
            if callable(func) and hasattr(func, 'keyboard') and func.keyboard
        ]
        return keyboard_functions
    
    @keyboard_function
    def tunnel_command(self, command , buttons):
        self.command = ''

        if command == buttons['VPN_UP']:
            self.command = 'sudo service ngrok start'
        elif command == buttons['VPN_DOWN']:
            self.command = 'sudo service ngrok stop'
        elif command == buttons['VPN_STATUS']:
            self.command = 'sudo service ngrok status'

        try:
            if self.logger:
                self.logger.info(f"Ejecutando comando: {self.command}")
                #result = self.command
                result = subprocess.check_output(self.command, shell=True, stderr=subprocess.STDOUT)

                return result.decode('utf-8').strip()
            return result
        except subprocess.CalledProcessError as e:
            return f"Error al ejecutar el comando: {e.output.decode('utf-8').strip()}"
         
    @keyboard_function
    def tunnel_detect_change_addres(self    ):
            ngrok_api_url = "http://rokubi.lan:4040/api/tunnels"

            try:
                response = requests.get(ngrok_api_url,timeout=10)
                response.raise_for_status()

                data = response.json()
                tunnels = data.get("tunnels", [])

                for tunnel in tunnels:
                    if tunnel.get("name") == "vpn":
                        public_url = tunnel.get("public_url")
                        if public_url:
                            # Eliminar el prefijo "tcp://" y separar address y port
                            address, port = public_url.replace("tcp://", "").split(":")

                            # Leer el archivo vpn.ovpn y obtener address2 y port2
                            address2, port2 = self.get_remote_from_ovpn_file()

                            # Comparar los valores address y port con address2 y port2
                            print(address, port, address2, port2)
                            if address != address2 or port != port2:
                                self.update_ovpn_file(address, port)
                                print("si hay cambios")
                                return address, port, address2, port2
                            else:
                                print("No hay cambios")
                                return address, port, address2, port2

                return "No se encontró el valor de 'public_url' para el túnel 'vpn'."
            except requests.exceptions.RequestException as e:
                return f"Error al hacer la petición HTTP: {e}"
            except (KeyError, ValueError) as e:
                return f"Error al procesar la respuesta JSON: {e}"

    def get_remote_from_ovpn_file(self):
        # Ruta del archivo vpn.ovpn
        ovpn_file_path = "/home/pi/ovpns/rafa.ovpn"

        if not os.path.isfile(ovpn_file_path):
            return None, None

        try:
            with open(ovpn_file_path, "r") as ovpn_file:
                for line in ovpn_file:
                    if line.strip().startswith("remote"):
                        print(line)
                        # Utilizar expresiones regulares para extraer address2 y port2
                        match = re.search(r"remote\s+(\S+)\s+(\d+)", line.strip())
                        if match:
                            address2, port2 = match.groups()
                            return address2, port2
                        break

            return None, None  # Si no se encontró la línea "remote" o no tiene suficientes valores
        except FileNotFoundError:
            return None, None  # Si no se encuentra el archivo vpn.ovpn
        except Exception as e:
            return None, None  # En caso de error al leer el archivo o procesar los valores
    
    def update_ovpn_file(self, address, port):
        # Ruta del archivo vpn.ovpn
        ovpn_file_path = "/home/pi/ovpns/vpn.ovpn"

        try:
            with open(ovpn_file_path, "r") as ovpn_file:
                lines = ovpn_file.readlines()

            with open(ovpn_file_path, "w") as ovpn_file:
                for line in lines:
                    if line.strip().startswith("remote"):
                        # Actualizar la línea "remote" con los nuevos valores de address y port
                        ovpn_file.write(f"remote {address} {port}\n")
                    else:
                        ovpn_file.write(line)

        except Exception as e:
            pass  # En caso de error al actualizar el archivo, simplemente omitir el cambio
