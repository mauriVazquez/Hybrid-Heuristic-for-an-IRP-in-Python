<?php

namespace App\Filament\Pages;

use Filament\Pages\Page;
use Illuminate\Support\Facades\Hash;
use Filament\Notifications\Notification;


class CambiarContrasena extends Page
{
    protected static ?string $navigationIcon = 'heroicon-o-key';
    protected static ?string $navigationGroup = 'Cuenta';
    protected static ?string $title = 'Cambiar Contraseña';
    protected static string $view = 'filament.pages.cambiar-contrasena';

    public ?string $new_password = '';
    public ?string $new_password_confirmation = '';

    public function cambiarContrasena()
    {
        $this->validate([
            'new_password' => 'required|min:8|confirmed',
        ], [
            'new_password.required' => 'La nueva contraseña es obligatoria.',
            'new_password.min' => 'La nueva contraseña debe tener al menos 8 caracteres.',
            'new_password.confirmed' => 'La confirmación de la contraseña no coincide.',
        ]);

        auth()->user()->update([
            'password' => Hash::make($this->new_password),
        ]);

        session()->flash('success', 'Contraseña actualizada correctamente.');
        $this->reset('new_password', 'new_password_confirmation');
        Notification::make()
            ->title('Contraseña actualizada')
            ->body('Tu contraseña ha sido cambiada exitosamente.')
            ->success()
            ->persistent()
            ->send(auth()->user());
    }

    public static function shouldRegisterNavigation(): bool
    {
        return auth()->user()?->hasRole('conductor');
    }
}
