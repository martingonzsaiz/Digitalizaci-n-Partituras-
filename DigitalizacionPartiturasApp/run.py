# Importación del objeto app desde el módulo app
from app import app

# Comprobación de la ejecución del archivo
if __name__ == '__main__':
    # Inicialización del servidor de Flask con host='0.0.0.0' (para que sea accesible con cualquier IP)
    # con el puerto 5000 y habilitando el modo de depuración para detectar los errores
    app.run(host='0.0.0.0', port=5000, debug=True)
