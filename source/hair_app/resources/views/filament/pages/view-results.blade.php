<x-filament::page>
        <h1 class="text-3xl text-center text-primary-600 dark:text-primary-400">Resultados HAIR</h1>
        <x-filament::section
                collapsible
                collapsed
        >
                <x-slot name="heading">
                        Datos de ejecución
                
                </x-slot>
                <h1 class="text-2xl text-center text-primary-600 dark:text-primary-400">{{strtoupper($this->record->zona->nombre)}}</h1>
                <h2 class="text-xl text-center">{{strtoupper($this->record->horizon_length)}} UNIDADES DE TIEMPO</h2>
        
                <h2 class="text-xl pt-3 text-primary-600 dark:text-primary-400">Proveedor</h2>
                {{$this->record->proveedor->nombre}}

                <h2 class="text-xl pt-3 text-primary-600 dark:text-primary-400">Clientes</h2>
                <ul>@foreach($this->record->clientes as $cliente)
                        <li>{{$cliente->nombre}}</li>
                @endforeach</ul>

                <h2 class="text-xl pt-3 text-primary-600 dark:text-primary-400">Vehiculo</h2>
                <b>Modelo:</b> {{$this->record->vehiculo->marca . " ". $this->record->vehiculo->nombre_modelo}}<br>
                <b>Dominio:</b> {{$this->record->vehiculo->patente}}<br>
                <b>Capacidad:</b> {{$this->record->vehiculo->capacidad}}<br>
        </x-filament::section>


        <x-filament::section>
                <x-slot name="heading">Resultados</x-slot>
                @if($this->attributes['soluciones'])
                <div class="fi-ta-ctn divide-y divide-gray-200 overflow-hidden rounded-xl bg-white shadow-sm ring-1 ring-gray-950/5 dark:divide-white/10 dark:bg-gray-900 dark:ring-white/10">
                <table class="fi-ta-table w-full table-auto divide-y divide-gray-200 text-start dark:divide-white/5">
                        <thead class="divide-y divide-gray-200 dark:divide-white/5">
                                <tr class="bg-gray-50 dark:bg-white/5">
                                        <th class="fi-ta-cell p-0 w-1">Iteracion</th>
                                        <th class="fi-ta-cell p-0 w-1">Etiqueta</th>
                                        <th class="fi-ta-cell p-0 w-1">Costo</th>
                                </tr>
                        </thead>     
                        <tbody class="divide-y divide-gray-200 whitespace-nowrap dark:divide-white/5">
                        @foreach($this->attributes['soluciones'] as $solucion)
                        <tr class="fi-ta-row hover:bg-gray-50 dark:hover:bg-white/5">
                                <td class="fi-ta-cell p-0 w-1 text-center">{{$solucion->iteration}}</td>
                                <td class="fi-ta-cell p-0 w-1 text-center">{{$solucion->tag}}</td>
                                <td class="fi-ta-cell p-0 w-1 text-center">{{$solucion->costo}}</td>
                        </tr>
                        @endforeach
                        </tbody>          
                </table>
                </div>
                @else
                <h1 class="text-2xl text-center text-primary-600 dark:text-primary-400">Error en la llamada al servicio</h1>
                @endif
        </x-filament::section>
</x-filament::page>