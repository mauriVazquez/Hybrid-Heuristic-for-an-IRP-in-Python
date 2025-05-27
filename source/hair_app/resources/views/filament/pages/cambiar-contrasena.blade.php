<x-filament::page>
    <div class="w-6/12 max-w-2xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-400 dark:border-gray-700">
        <form wire:submit.prevent="cambiarContrasena">
            <div class="space-y-4">
                <label class="block text-gray-900 dark:text-gray-200 font-medium">Nueva contraseña</label>
                <x-filament::input
                    type="password"
                    wire:model="new_password"
                    required
                    class="w-full p-3 border border-gray-800 dark:border-gray-500 rounded-md bg-gray-50 text-gray-900 dark:bg-gray-700 dark:text-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />

                <label class="block text-gray-900 dark:text-gray-200 font-medium">Confirmar nueva contraseña</label>
                <x-filament::input
                    type="password"
                    wire:model="new_password_confirmation"
                    required
                    class="w-full p-3 border border-gray-800 dark:border-gray-500 rounded-md bg-gray-50 text-gray-900 dark:bg-gray-700 dark:text-white shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
                <!-- Mensajes de error de validación -->
                <div class="text-red-600 dark:text-red-500 text-sm font-medium">
                    @error('new_password') {{ $message }} @enderror
                    @error('new_password_confirmation') {{ $message }} @enderror
                </div>

                <x-filament::button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg dark:bg-blue-500 dark:hover:bg-blue-600 transition-all duration-300">
                    Cambiar Contraseña
                </x-filament::button>
            </div>
        </form>
    </div>
</x-filament::page>