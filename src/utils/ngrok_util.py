import subprocess

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

        if command == buttons['VPN_DOWN']:
            self.command = 'sudo service ngrok start'
        elif command == buttons['VPN_UP']:
            self.command = 'sudo service ngrok stop'
        elif command == buttons['VPN_STATUS']:
            self.command = 'sudo service ngrok status'

        try:
            if self.logger:
                self.logger.info(f"Ejecutando comando: {self.command}")
                result = self.command
                #result = subprocess.check_output(EXECUTE, shell=True, stderr=subprocess.STDOUT)
                #return result.decode('utf-8').strip()
            return result
        except subprocess.CalledProcessError as e:
            return f"Error al ejecutar el comando: {e.output.decode('utf-8').strip()}"
         
    @keyboard_function
    def tunnel_detect_change_addres(self, command):
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return result.decode('utf-8').strip()
        except subprocess.CalledProcessError as e:
            return f"Error al ejecutar el comando: {e.output.decode('utf-8').strip()}"
