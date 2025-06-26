<x-filament-widgets::widget>
    <x-filament::section>
        <x-slot name="heading">
            Información del Sistema
        </x-slot>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Información General -->
            <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
                <div class="px-4 py-5 sm:p-6">
                    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Estado del Sistema</h3>
                    <dl class="space-y-3">
                        <div class="flex justify-between">
                            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Versión del Algoritmo:</dt>
                            <dd class="text-sm text-gray-900 dark:text-white font-semibold">{{ $version_algoritmo }}</dd>
                        </div>
                        <div class="flex justify-between">
                            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Estado del Servidor:</dt>
                            <dd class="text-sm">
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                    {{ $estado_servidor }}
                                </span>
                            </dd>
                        </div>
                        <div class="flex justify-between">
                            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Uso de Memoria:</dt>
                            <dd class="text-sm text-gray-900 dark:text-white">{{ $memoria_uso }}</dd>
                        </div>
                        <div class="flex justify-between">
                            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Uso de CPU:</dt>
                            <dd class="text-sm text-gray-900 dark:text-white">{{ $cpu_uso }}</dd>
                        </div>
                        <div class="flex justify-between">
                            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Último Mantenimiento:</dt>
                            <dd class="text-sm text-gray-900 dark:text-white">{{ $ultimo_mantenimiento }}</dd>
                        </div>
                        <div class="flex justify-between">
                            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">Próxima Actualización:</dt>
                            <dd class="text-sm text-gray-900 dark:text-white">{{ $proxima_actualizacion }}</dd>
                        </div>
                    </dl>
                </div>
            </div>

            <!-- Algoritmos y Funcionalidades -->
            <div class="space-y-6">
                <!-- Algoritmos Disponibles -->
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
                    <div class="px-4 py-5 sm:p-6">
                        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Algoritmos Disponibles</h3>
                        <ul class="space-y-2">
                            @foreach($algoritmos_disponibles as $algoritmo)
                                <li class="flex items-center">
                                    <svg class="h-4 w-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                                    </svg>
                                    <span class="text-sm text-gray-900 dark:text-white">{{ $algoritmo }}</span>
                                </li>
                            @endforeach
                        </ul>
                    </div>
                </div>

                <!-- Funcionalidades -->
                <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
                    <div class="px-4 py-5 sm:p-6">
                        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">Funcionalidades Principales</h3>
                        <ul class="space-y-2">
                            @foreach($funcionalidades as $funcionalidad)
                                <li class="flex items-center">
                                    <svg class="h-4 w-4 text-blue-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                                    </svg>
                                    <span class="text-sm text-gray-900 dark:text-white">{{ $funcionalidad }}</span>
                                </li>
                            @endforeach
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </x-filament::section>
</x-filament-widgets::widget>
