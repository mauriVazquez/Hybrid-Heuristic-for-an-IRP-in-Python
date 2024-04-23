<x-filament-panels::page>
    <div>
        <form wire:submit="submit">
            {{ $this->form }}

            <button type="submit">
                Generar
            </button>
        </form>

        <x-filament-actions::modals />
    </div>
</x-filament-panels::page>