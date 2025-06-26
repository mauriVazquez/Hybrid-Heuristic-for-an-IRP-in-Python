<?php

namespace App\Filament\Pages;

use Filament\Pages\Dashboard as BaseDashboard;

class Dashboard extends BaseDashboard
{
    protected static string $routePath = '/dashboard';
    
    protected static ?string $title = 'Dashboard Principal';
    
    protected static ?string $navigationLabel = 'Dashboard';
    
    protected static ?string $navigationIcon = 'heroicon-o-chart-bar';

    public static function shouldRegisterNavigation(): bool
    {
        return auth()->user()?->hasRole('admin');
    }
    
    // protected static ?int $navigationSort = 1;    
    public function getWidgets(): array
    {
        return [
            \App\Filament\Widgets\EstadisticasGenerales::class,
            \App\Filament\Widgets\GraficoCostos::class,
            \App\Filament\Widgets\GraficoRutas::class,
        ];
    }

    public function getColumns(): int | array
    {
        return [
            'sm' => 1,
            'md' => 2,
            'lg' => 3,
        ];
    }
}
