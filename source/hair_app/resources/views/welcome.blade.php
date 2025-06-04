<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HAIR APP - Optimización de Rutas para Centros de Distribución</title>
    <meta name="description" content="Plataforma integral para centros de distribución que optimiza rutas de reparto, gestiona clientes, vehículos y zonas de manera eficiente.">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-lg fixed w-full z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <div class="flex-shrink-0 flex items-center">
                        <i class="fas fa-route text-amber-600 text-2xl mr-2"></i>
                        <span class="font-bold text-xl text-gray-900">HAIR APP</span>
                    </div>
                </div>
                <div class="hidden md:flex items-center space-x-8">
                    <a href="#features" class="text-gray-700 hover:text-amber-600 transition duration-300">Características</a>
                    <a href="#how-it-works" class="text-gray-700 hover:text-amber-600 transition duration-300">Cómo Funciona</a>
                    <a href="#benefits" class="text-gray-700 hover:text-amber-600 transition duration-300">Beneficios</a>
                    <a href="/admin" class="bg-amber-600 text-white px-4 py-2 rounded-lg hover:bg-amber-700 transition duration-300">Ingresar</a>
                </div>
                <div class="md:hidden flex items-center">
                    <button class="text-gray-700 hover:text-amber-600">
                        <i class="fas fa-bars text-xl"></i>
                    </button>
                </div>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="bg-gradient-to-br from-amber-500 to-amber-700 text-white pt-20">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <div>
                    <h1 class="text-4xl md:text-6xl font-bold mb-6 leading-tight">
                        Optimiza tus <span class="text-white">Rutas de Reparto</span> de Manera Inteligente
                    </h1>
                    <p class="text-xl mb-8 text-blue-100">
                        Plataforma integral para centros de distribución que revoluciona la gestión logística con optimización automática de rutas, control de vehículos y gestión eficiente de clientes.
                    </p>
                    <div class="flex flex-col sm:flex-row gap-4">
                        <button class="bg-white text-amber-700 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition duration-300 transform hover:scale-105">
                            Solicitar Demo
                        </button>
                        <button class="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white hover:text-amber-700 transition duration-300">
                            Ver Características
                        </button>
                    </div>
                </div>
                <div class="relative">
                    <div class="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
                        <div class="grid grid-cols-2 gap-4 mb-6">
                            <div class="bg-green-400/20 rounded-lg p-4 text-center">
                                <i class="fas fa-truck text-2xl mb-2"></i>
                                <div class="text-sm">Vehículos Activos</div>
                                <div class="text-2xl font-bold">247</div>
                            </div>
                            <div class="bg-yellow-400/20 rounded-lg p-4 text-center">
                                <i class="fas fa-map-marker-alt text-2xl mb-2"></i>
                                <div class="text-sm">Entregas Hoy</div>
                                <div class="text-2xl font-bold">1,834</div>
                            </div>
                        </div>
                        <div class="bg-amber-400/20 rounded-lg p-4">
                            <div class="flex items-center justify-between mb-2">
                                <span class="text-sm">Eficiencia de Rutas</span>
                                <span class="text-sm font-bold">94%</span>
                            </div>
                            <div class="w-full bg-white/20 rounded-full h-2">
                                <div class="bg-green-400 h-2 rounded-full" style="width: 94%"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-20 bg-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-16">
                <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                    Características Principales
                </h2>
                <p class="text-xl text-gray-600 max-w-3xl mx-auto">
                    Una solución completa que integra todas las herramientas necesarias para optimizar tu operación logística
                </p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <div class="bg-gray-50 rounded-xl p-8 hover:shadow-lg transition duration-300">
                    <div class="bg-amber-100 w-16 h-16 rounded-lg flex items-center justify-center mb-6">
                        <i class="fas fa-clipboard-list text-amber-600 text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold mb-4 text-gray-900">Planillas de Viajes</h3>
                    <p class="text-gray-600">
                        Crea y gestiona planillas de viajes de manera intuitiva. Organiza tus entregas con información detallada de cada ruta.
                    </p>
                </div>

                <div class="bg-gray-50 rounded-xl p-8 hover:shadow-lg transition duration-300">
                    <div class="bg-green-100 w-16 h-16 rounded-lg flex items-center justify-center mb-6">
                        <i class="fas fa-users text-green-600 text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold mb-4 text-gray-900">Gestión de Clientes</h3>
                    <p class="text-gray-600">
                        Administra tu base de clientes con información completa, historial de entregas y preferencias de servicio.
                    </p>
                </div>

                <div class="bg-gray-50 rounded-xl p-8 hover:shadow-lg transition duration-300">
                    <div class="bg-purple-100 w-16 h-16 rounded-lg flex items-center justify-center mb-6">
                        <i class="fas fa-truck text-purple-600 text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold mb-4 text-gray-900">Control de Vehículos</h3>
                    <p class="text-gray-600">
                        Registra y monitorea tu flota vehicular con información técnica, capacidades y estado operativo.
                    </p>
                </div>

                <div class="bg-gray-50 rounded-xl p-8 hover:shadow-lg transition duration-300">
                    <div class="bg-orange-100 w-16 h-16 rounded-lg flex items-center justify-center mb-6">
                        <i class="fas fa-map text-orange-600 text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold mb-4 text-gray-900">Zonificación</h3>
                    <p class="text-gray-600">
                        Define y administra zonas de reparto para optimizar la distribución geográfica de tus entregas.
                    </p>
                </div>

                <div class="bg-gray-50 rounded-xl p-8 hover:shadow-lg transition duration-300">
                    <div class="bg-red-100 w-16 h-16 rounded-lg flex items-center justify-center mb-6">
                        <i class="fas fa-route text-red-600 text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold mb-4 text-gray-900">Optimización de Rutas</h3>
                    <p class="text-gray-600">
                        Algoritmo inteligente que calcula las rutas más eficientes considerando tráfico, distancias y restricciones.
                    </p>
                </div>

                <div class="bg-gray-50 rounded-xl p-8 hover:shadow-lg transition duration-300">
                    <div class="bg-teal-100 w-16 h-16 rounded-lg flex items-center justify-center mb-6">
                        <i class="fas fa-chart-line text-teal-600 text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold mb-4 text-gray-900">Reportes y Analytics</h3>
                    <p class="text-gray-600">
                        Obtén insights valiosos con reportes detallados sobre eficiencia, costos y rendimiento operativo.
                    </p>
                </div>
            </div>
        </div>
    </section>

    <!-- How It Works Section -->
    <section id="how-it-works" class="py-20 bg-gray-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-16">
                <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                    ¿Cómo Funciona?
                </h2>
                <p class="text-xl text-gray-600">
                    Proceso simple y eficiente en 4 pasos
                </p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                <div class="text-center">
                    <div class="bg-amber-600 text-white w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl font-bold">
                        1
                    </div>
                    <h3 class="text-xl font-semibold mb-4 text-gray-900">Configuración Inicial</h3>
                    <p class="text-gray-600">
                        Carga tus clientes, vehículos y define las zonas de reparto en el sistema.
                    </p>
                </div>

                <div class="text-center">
                    <div class="bg-green-600 text-white w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl font-bold">
                        2
                    </div>
                    <h3 class="text-xl font-semibold mb-4 text-gray-900">Crear Planilla</h3>
                    <p class="text-gray-600">
                        Genera planillas de viaje con los pedidos y entregas programadas para cada día.
                    </p>
                </div>

                <div class="text-center">
                    <div class="bg-purple-600 text-white w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl font-bold">
                        3
                    </div>
                    <h3 class="text-xl font-semibold mb-4 text-gray-900">Optimización</h3>
                    <p class="text-gray-600">
                        El sistema calcula automáticamente las rutas más eficientes para cada vehículo.
                    </p>
                </div>

                <div class="text-center">
                    <div class="bg-orange-600 text-white w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl font-bold">
                        4
                    </div>
                    <h3 class="text-xl font-semibold mb-4 text-gray-900">Ejecución</h3>
                    <p class="text-gray-600">
                        Los repartidores reciben las rutas optimizadas y ejecutan las entregas eficientemente.
                    </p>
                </div>
            </div>
        </div>
    </section>

    <!-- Benefits Section -->
    <section id="benefits" class="py-20 bg-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
                <div>
                    <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-8">
                        Beneficios para tu Operación
                    </h2>
                    
                    <div class="space-y-6">
                        <div class="flex items-start">
                            <div class="bg-green-100 rounded-lg p-3 mr-4">
                                <i class="fas fa-dollar-sign text-green-600 text-xl"></i>
                            </div>
                            <div>
                                <h3 class="text-xl font-semibold mb-2 text-gray-900">Reducción de Costos</h3>
                                <p class="text-gray-600">Hasta 30% menos en costos de combustible y mantenimiento vehicular.</p>
                            </div>
                        </div>

                        <div class="flex items-start">
                            <div class="bg-blue-100 rounded-lg p-3 mr-4">
                                <i class="fas fa-clock text-amber-600 text-xl"></i>
                            </div>
                            <div>
                                <h3 class="text-xl font-semibold mb-2 text-gray-900">Ahorro de Tiempo</h3>
                                <p class="text-gray-600">Optimización que reduce tiempos de entrega en promedio 25%.</p>
                            </div>
                        </div>

                        <div class="flex items-start">
                            <div class="bg-purple-100 rounded-lg p-3 mr-4">
                                <i class="fas fa-smile text-purple-600 text-xl"></i>
                            </div>
                            <div>
                                <h3 class="text-xl font-semibold mb-2 text-gray-900">Satisfacción del Cliente</h3>
                                <p class="text-gray-600">Entregas más puntuales y predecibles mejoran la experiencia del cliente.</p>
                            </div>
                        </div>

                        <div class="flex items-start">
                            <div class="bg-orange-100 rounded-lg p-3 mr-4">
                                <i class="fas fa-chart-bar text-orange-600 text-xl"></i>
                            </div>
                            <div>
                                <h3 class="text-xl font-semibold mb-2 text-gray-900">Mayor Productividad</h3>
                                <p class="text-gray-600">Incremento del 40% en entregas completadas por vehículo por día.</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl p-8">
                    <div class="text-center mb-8">
                        <h3 class="text-2xl font-bold text-gray-900 mb-4">Resultados Comprobados</h3>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-6">
                        <div class="text-center bg-white rounded-lg p-6 shadow-sm">
                            <div class="text-3xl font-bold text-blue-600 mb-2">30%</div>
                            <div class="text-sm text-gray-600">Reducción de Costos</div>
                        </div>
                        <div class="text-center bg-white rounded-lg p-6 shadow-sm">
                            <div class="text-3xl font-bold text-green-600 mb-2">25%</div>
                            <div class="text-sm text-gray-600">Menos Tiempo</div>
                        </div>
                        <div class="text-center bg-white rounded-lg p-6 shadow-sm">
                            <div class="text-3xl font-bold text-purple-600 mb-2">40%</div>
                            <div class="text-sm text-gray-600">Más Entregas</div>
                        </div>
                        <div class="text-center bg-white rounded-lg p-6 shadow-sm">
                            <div class="text-3xl font-bold text-orange-600 mb-2">95%</div>
                            <div class="text-sm text-gray-600">Satisfacción</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Target Users Section -->
    <section class="py-20 bg-gray-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center mb-16">
                <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                    Diseñado para Profesionales de la Logística
                </h2>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div class="bg-white rounded-xl p-8 text-center shadow-lg hover:shadow-xl transition duration-300">
                    <div class="bg-amber-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
                        <i class="fas fa-warehouse text-amber-600 text-3xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold mb-4 text-gray-900">Centros de Distribución</h3>
                    <p class="text-gray-600 mb-6">
                        Optimiza la gestión completa de tu centro de distribución con herramientas especializadas para coordinadores y supervisores.
                    </p>
                    <ul class="text-left text-sm text-gray-600 space-y-2">
                        <li class="flex items-center"><i class="fas fa-check text-green-500 mr-2"></i> Control total de inventario</li>
                        <li class="flex items-center"><i class="fas fa-check text-green-500 mr-2"></i> Planificación de rutas</li>
                        <li class="flex items-center"><i class="fas fa-check text-green-500 mr-2"></i> Reportes ejecutivos</li>
                    </ul>
                </div>

                <div class="bg-white rounded-xl p-8 text-center shadow-lg hover:shadow-xl transition duration-300">
                    <div class="bg-green-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
                        <i class="fas fa-shipping-fast text-green-600 text-3xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold mb-4 text-gray-900">Repartidores</h3>
                    <p class="text-gray-600 mb-6">
                        Interfaz móvil intuitiva que guía a los repartidores por las rutas más eficientes con información en tiempo real.
                    </p>
                    <ul class="text-left text-sm text-gray-600 space-y-2">
                        <li class="flex items-center"><i class="fas fa-check text-green-500 mr-2"></i> Navegación optimizada</li>
                        <li class="flex items-center"><i class="fas fa-check text-green-500 mr-2"></i> Confirmación de entregas</li>
                        <li class="flex items-center"><i class="fas fa-check text-green-500 mr-2"></i> Comunicación directa</li>
                    </ul>
                </div>

                <div class="bg-white rounded-xl p-8 text-center shadow-lg hover:shadow-xl transition duration-300">
                    <div class="bg-purple-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6">
                        <i class="fas fa-handshake text-purple-600 text-3xl"></i>
                    </div>
                    <h3 class="text-xl font-semibold mb-4 text-gray-900">Proveedores</h3>
                    <p class="text-gray-600 mb-6">
                        Portal especializado para proveedores que facilita la coordinación de entregas y el seguimiento de pedidos.
                    </p>
                    <ul class="text-left text-sm text-gray-600 space-y-2">
                        <li class="flex items-center"><i class="fas fa-check text-green-500 mr-2"></i> Programación de entregas</li>
                        <li class="flex items-center"><i class="fas fa-check text-green-500 mr-2"></i> Seguimiento en tiempo real</li>
                        <li class="flex items-center"><i class="fas fa-check text-green-500 mr-2"></i> Historial de transacciones</li>
                    </ul>
                </div>
            </div>
        </div>
    </section>

    <!-- CTA Section -->
    <section class="py-20 bg-gradient-to-r from-amber-500 to-orange-600 text-white">
        <div class="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
            <h2 class="text-3xl md:text-4xl font-bold mb-6">
                ¿Listo para Optimizar tu Operación Logística?
            </h2>
            <p class="text-xl mb-8 text-amber-100">
                Únete a cientos de empresas que ya están ahorrando tiempo y dinero con HAIR APP
            </p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
                <button class="bg-white text-amber-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition duration-300 transform hover:scale-105">
                    Solicitar Demo Gratuita
                </button>
                <button class="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white hover:text-amber-600 transition duration-300">
                    Hablar con un Experto
                </button>
            </div>
        </div>
    </section>

    <!-- Contact Section -->
    <section id="contact" class="py-20 bg-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-16">
                <div>
                    <h2 class="text-3xl font-bold text-gray-900 mb-6">Contáctanos</h2>
                    <p class="text-xl text-gray-600 mb-8">
                        Estamos aquí para ayudarte a optimizar tu operación logística. Contáctanos para una consulta personalizada.
                    </p>
                    
                    <div class="space-y-6">
                        <div class="flex items-center">
                            <div class="bg-blue-100 rounded-lg p-3 mr-4">
                                <i class="fas fa-phone text-blue-600"></i>
                            </div>
                            <div>
                                <div class="font-semibold text-gray-900">Teléfono</div>
                                <div class="text-gray-600">+1 (555) 123-4567</div>
                            </div>
                        </div>
                        
                        <div class="flex items-center">
                            <div class="bg-green-100 rounded-lg p-3 mr-4">
                                <i class="fas fa-envelope text-green-600"></i>
                            </div>
                            <div>
                                <div class="font-semibold text-gray-900">Email</div>
                                <div class="text-gray-600">contacto@HAIR APP.com</div>
                            </div>
                        </div>
                        
                        <div class="flex items-center">
                            <div class="bg-purple-100 rounded-lg p-3 mr-4">
                                <i class="fas fa-map-marker-alt text-purple-600"></i>
                            </div>
                            <div>
                                <div class="font-semibold text-gray-900">Oficina</div>
                                <div class="text-gray-600">Av. Principal 123, Ciudad</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="bg-gray-50 rounded-xl p-8">
                    <form class="space-y-6">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Nombre Completo</label>
                            <input type="text" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                            <input type="email" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Empresa</label>
                            <input type="text" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Tipo de Usuario</label>
                            <select class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent">
                                <option>Centro de Distribución</option>
                                <option>Repartidor</option>
                                <option>Proveedor</option>
                                <option>Otro</option>
                            </select>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Mensaje</label>
                            <textarea rows="4" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"></textarea>
                        </div>
                        
                        <button type="submit" class="w-full bg-amber-600 text-white py-3 rounded-lg font-semibold hover:bg-amber-700 transition duration-300">
                            Enviar Mensaje
                        </button>
                    </form>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-12">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
                <div>
                    <div class="flex items-center mb-4">
                        <i class="fas fa-route text-amber-400 text-2xl mr-2"></i>
                        <span class="font-bold text-xl">HAIR APP</span>
                    </div>
                    <p class="text-gray-400 mb-4">
                        Optimizando la logística del futuro con tecnología inteligente.
                    </p>
                    <div class="flex space-x-4">
                        <a href="#" class="text-gray-400 hover:text-white transition duration-300">
                            <i class="fab fa-facebook text-xl"></i>
                        </a>
                        <a href="#" class="text-gray-400 hover:text-white transition duration-300">
                            <i class="fab fa-twitter text-xl"></i>
                        </a>
                        <a href="#" class="text-gray-400 hover:text-white transition duration-300">
                            <i class="fab fa-linkedin text-xl"></i>
                        </a>
                    </div>
                </div>
                
                <div>
                    <h3 class="font-semibold mb-4">Producto</h3>
                    <ul class="space-y-2 text-gray-400">
                        <li><a href="#" class="hover:text-white transition duration-300">Características</a></li>
                        <li><a href="#" class="hover:text-white transition duration-300">Precios</a></li>
                        <li><a href="#" class="hover:text-white transition duration-300">Demo</a></li>
                        <li><a href="#" class="hover:text-white transition duration-300">API</a></li>
                    </ul>
                </div>
                
                <div>
                    <h3 class="font-semibold mb-4">Soporte</h3>
                    <ul class="space-y-2 text-gray-400">
                        <li><a href="#" class="hover:text-white transition duration-300">Documentación</a></li>
                        <li><a href="#" class="hover:text-white transition duration-300">Centro de Ayuda</a></li>
                        <li><a href="#" class="hover:text-white transition duration-300">Contacto</a></li>
                        <li><a href="#" class="hover:text-white transition duration-300">Estado del Sistema</a></li>
                    </ul>
                </div>
                
                <div>
                    <h3 class="font-semibold mb-4">Empresa</h3>
                    <ul class="space-y-2 text-gray-400">
                        <li><a href="#" class="hover:text-white transition duration-300">Acerca de</a></li>
                        <li><a href="#" class="hover:text-white transition duration-300">Blog</a></li>
                        <li><a href="#" class="hover:text-white transition duration-300">Carreras</a></li>
                        <li><a href="#" class="hover:text-white transition duration-300">Privacidad</a></li>
                    </ul>
                </div>
            </div>
            
            <div class="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
                <p>&copy; 2024 HAIR APP. Todos los derechos reservados.</p>
            </div>
        </div>
    </footer>

    <script>
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Mobile menu toggle
        const mobileMenuButton = document.querySelector('.md\\:hidden button');
        const mobileMenu = document.createElement('div');
        mobileMenu.className = 'md:hidden bg-white shadow-lg absolute top-16 left-0 right-0 z-40 hidden';
        mobileMenu.innerHTML = `
            <div class="px-4 py-2 space-y-2">
                <a href="#features" class="block py-2 text-gray-700 hover:text-amber-600">Características</a>
                <a href="#how-it-works" class="block py-2 text-gray-700 hover:text-amber-600">Cómo Funciona</a>
                <a href="#benefits" class="block py-2 text-gray-700 hover:text-amber-600">Beneficios</a>
                <a href="#contact" class="block py-2 bg-amber-600 text-white px-4 rounded-lg text-center">Contacto</a>
            </div>
        `;
        
        document.querySelector('nav').appendChild(mobileMenu);
        
        mobileMenuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    </script>
</body>
</html>
