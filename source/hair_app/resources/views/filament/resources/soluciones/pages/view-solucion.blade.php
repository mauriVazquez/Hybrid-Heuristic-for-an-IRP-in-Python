<x-filament-panels::page>

    <!-- {{$record->rutas}} -->
    <div class="flex justify-beetwen">
        <div>Seleccionar ruta:</div> 
        @foreach($record->rutas as $ruta)
            <button wire:click="setCurrentRouteData({{$ruta}})" class="fi-btn relative grid-flow-col items-center justify-center font-semibold outline-none transition duration-75 focus-visible:ring-2 rounded-lg  fi-btn-color-gray fi-color-gray fi-size-md fi-btn-size-md gap-1.5 px-3 py-2 text-sm inline-grid shadow-sm bg-white text-gray-950 hover:bg-gray-50 dark:bg-white/5 dark:text-white dark:hover:bg-white/10 ring-1 ring-gray-950/10 dark:ring-white/20 fi-ac-action fi-ac-btn-action">
                Ruta {{$loop->index + 1}}
            </button>
        @endforeach
    </div>
    @push('scripts')
    <script src="https://d3js.org/d3.v7.min.js"></script>
    @endpush
    <livewire:vehicle-route :routeData="$currentRouteData" :key="time()" />
    <div>
        {{
            $this->table
        }}
    </div>
</x-filament-panels::page>