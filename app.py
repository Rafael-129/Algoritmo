from flask import Flask, render_template, request, redirect, url_for

class Nodo:
    def __init__(self, data):
        self.data = data
        self.next = None

class ListaEnlazada:
    def __init__(self):
        self.head = None

    def agregar_nodo(self, data):
        nuevo_nodo = Nodo(data)
        if not self.head:
            self.head = nuevo_nodo
        else:
            actual = self.head
            while actual.next:
                actual = actual.next
            actual.next = nuevo_nodo

    def buscar(self, criterio):
        actual = self.head
        while actual:
            if actual.data['nombre'] == criterio:
                return actual.data
            actual = actual.next
        return None

    def mostrar_todos(self):
        actual = self.head
        resultado = []
        while actual:
            resultado.append(actual.data)
            actual = actual.next
        return resultado

class Cola:
    def __init__(self):
        self.front = None
        self.rear = None

    def encolar(self, pedido):
        nuevo_nodo = Nodo(pedido)
        if not self.front:
            self.front = self.rear = nuevo_nodo
        else:
            self.rear.next = nuevo_nodo
            self.rear = nuevo_nodo

    def mostrar_pedidos(self):
        actual = self.front
        resultado = []
        while actual:
            resultado.append(actual.data)
            actual = actual.next
        return resultado

class Pila:
    def __init__(self):
        self.top = None

    def apilar(self, data):
        nuevo_nodo = Nodo(data)
        nuevo_nodo.next = self.top
        self.top = nuevo_nodo

    def mostrar_historial(self):
        actual = self.top
        resultado = []
        while actual:
            resultado.append(actual.data)
            actual = actual.next
        return resultado

class MaquinaExpendedora:
    def __init__(self):
        self.inventario = ListaEnlazada()
        self.pedidos = Cola()
        self.historial = Pila()

    def agregar_producto(self, nombre, precio, cantidad):
        producto = {'nombre': nombre, 'precio': float(precio), 'cantidad': int(cantidad)}
        self.inventario.agregar_nodo(producto)

    def ver_inventario(self):
        return self.inventario.mostrar_todos()

    def realizar_pedido(self, nombre_producto):
        producto = self.inventario.buscar(nombre_producto)
        if producto and producto['cantidad'] > 0:
            producto['cantidad'] -= 1
            pedido = {'producto': nombre_producto, 'cantidad': 1, 'total': producto['precio']}
            self.pedidos.encolar(pedido)
            self.historial.apilar(pedido)
            return f"Pedido de {nombre_producto} realizado con éxito."
        else:
            return "Producto no disponible."
        
    def calcular_ganancias_totales(self):
        total_ganado = 0
        for pedido in self.historial.mostrar_historial():
            total_ganado += pedido['total']
        return total_ganado
    
    def reabastecer_producto(self, nombre_producto, cantidad):
        producto = self.inventario.buscar(nombre_producto)
        if producto:
            producto['cantidad'] += cantidad
            return f"Producto {nombre_producto} reabastecido."
        else:
            return "Producto no encontrado."

    def ver_pedidos(self):
        return self.pedidos.mostrar_pedidos()

    def ver_historial(self):
        return self.historial.mostrar_historial()


app = Flask(__name__)

# Inventario de productos
inventario = [
    {'nombre': 'A1', 'precio': 1.5, 'cantidad': 10},
    {'nombre': 'A2', 'precio': 1.2, 'cantidad': 8},
    {'nombre': 'A3', 'precio': 0.9, 'cantidad': 15},
    {'nombre': 'B1', 'precio': 0.9, 'cantidad': 15},
    {'nombre': 'B2', 'precio': 0.9, 'cantidad': 15},
    {'nombre': 'B3', 'precio': 0.9, 'cantidad': 15},
    {'nombre': 'C1', 'precio': 0.9, 'cantidad': 15},
    {'nombre': 'C2', 'precio': 0.9, 'cantidad': 15},
    {'nombre': 'C3', 'precio': 0.9, 'cantidad': 15}
]

# Historial de pedidos
historial = []
total_acumulado = 0

@app.route('/', methods=['GET', 'POST'])
def home():
    global total_acumulado
    mensaje = 'Seleccione su Producto'
    total_venta = 0  # Total de la venta actual
    
    if request.method == 'POST':
        producto_nombre = request.form['producto']
        producto = next((p for p in inventario if p['nombre'] == producto_nombre), None)
        
        if producto and producto['cantidad'] > 0:
            producto['cantidad'] -= 1
            total_venta = producto['precio']  # Total solo para esta venta
            total_acumulado += total_venta  # Acumulamos solo si es exitoso
            mensaje = f"Pedido de {producto_nombre} realizado con éxito. Total venta: ${total_venta:.2f}. "
            
            # Agregar el pedido al historial
            historial.append({'producto': producto_nombre, 'total': total_venta})
        else:
            mensaje = "Producto no disponible o fuera de stock."
    
    return render_template('index.html', inventario=inventario, mensaje=mensaje, total_acumulado=total_acumulado)

@app.route('/historial')
def ver_historial():
    # Calcular el total ganado en el historial
    total_ganado = sum(pedido['total'] for pedido in historial)
    return render_template('historial.html', historial=historial, total_ganado=total_ganado)

@app.route('/reabastecer', methods=['GET', 'POST'])
def reabastecer():
    if request.method == 'POST':
        nombre_producto = request.form['nombre']
        cantidad = int(request.form['cantidad'])
        
        # Buscar el producto por nombre
        producto = next((p for p in inventario if p['nombre'].lower() == nombre_producto.lower()), None)
        
        if producto:
            producto['cantidad'] += cantidad
            mensaje = f"Producto {nombre_producto} reabastecido exitosamente. Nueva cantidad: {producto['cantidad']}"
        else:
            mensaje = f"El producto {nombre_producto} no existe."
        
        return render_template('reabastecer.html', mensaje=mensaje)
    
    return render_template('reabastecer.html', mensaje=None)


@app.route('/cancelar', methods=['POST'])
def cancelar():
    global total_acumulado

    if historial:
        # Eliminar el último pedido del historial
        ultimo_pedido = historial.pop()
        total_acumulado -= ultimo_pedido['total']  # Restar del total acumulado

        # Revertir el stock del producto
        producto = next((p for p in inventario if p['nombre'] == ultimo_pedido['producto']), None)
        if producto:
            producto['cantidad'] += 1

        mensaje = f"Pedido de {ultimo_pedido['producto']} cancelado exitosamente."
    else:
        mensaje = "No hay pedidos para cancelar."

    return render_template('index.html', inventario=inventario, mensaje=mensaje, total_acumulado=total_acumulado)



if __name__ == '__main__':
    app.run(debug=True)