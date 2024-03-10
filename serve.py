from http.server import BaseHTTPRequestHandler, HTTPServer
from entidades_manager import EntidadesManager 
import json
from main import execute
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        EntidadesManager.restart()
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        #Se inicializa al proveedor
        proveedor = data['proveedor']
        EntidadesManager.crear_proveedor(proveedor['id'], proveedor['coord_x'], proveedor['coord_y'],proveedor['costo_almacenamiento'], proveedor['nivel_almacenamiento'],  proveedor['nivel_produccion'],)

        #Se inicializan los clientes
        for cliente in data['clientes']['data']:
            EntidadesManager.crear_cliente(cliente['id'], cliente['coord_x'], cliente['coord_y'], cliente['costo_almacenamiento'], cliente['nivel_almacenamiento'], cliente['nivel_maximo'], cliente['nivel_minimo'], cliente['nivel_demanda'], proveedor['coord_x'], proveedor['coord_y'])
        
        #Se inicializa el vehículo
        vehiculo = data['vehiculo']
        EntidadesManager.crear_vehiculo(vehiculo['id'], vehiculo['capacidad'])
        
        #Se inicializan los parámetros [Importante que vaya último]
        EntidadesManager.crear_parametros(data['horizon_length'])
       
        soluciones = execute()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = json.dumps({"data": soluciones, "status":200})
        print(soluciones)
        self.wfile.write(response.encode('utf-8'))

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8001):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Servidor iniciado en el puerto {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()