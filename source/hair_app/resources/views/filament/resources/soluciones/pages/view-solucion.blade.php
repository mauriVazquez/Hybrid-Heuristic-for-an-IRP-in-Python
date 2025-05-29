<x-filament-panels::page>
    <div class="flex flex-col gap-4">
        {{-- Filtro fijo --}}
        <select
            class="rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white text-sm px-2 py-1"
            wire:change="$set('rutaId', $event.target.value)">
            @foreach ($rutas as $ruta)
            <option value="{{ $ruta['id'] }}" {{ $rutaId == $ruta['id'] ? 'selected' : '' }}>
                Ruta {{ $ruta['orden'] }}
            </option>
            @endforeach
        </select>



        {{-- Layout dividido: tabla + canvas --}}
        <div class="flex flex-col lg:flex-row gap-4">
            <div class="w-full lg:w-3/5">
                {{ $this->table }}
            </div>
            <div class="w-full lg:w-2/5">
                @push('scripts')
                <script src="https://d3js.org/d3.v7.min.js"></script>
                @endpush

                <livewire:vehicle-route
                    :routeData="$this->currentRouteData['puntos']"
                    :key="'route-' . $this->rutaId . $canvasRefreshKey" />

            </div>
        </div>
    </div>
</x-filament-panels::page>