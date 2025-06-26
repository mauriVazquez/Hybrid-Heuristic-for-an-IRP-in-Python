<?php

namespace App\Filament\Widgets;

use Filament\Widgets\Widget;

class InfoSistema extends Widget
{
    protected static string $view = 'filament.widgets.info-sistema';
    
    protected static ?int $sort = 6;
    
    protected int | string | array $columnSpan = 'full';

    protected function getViewData(): array
    {
        return [
            'version_algoritmo' => '2.1.4',
            'ultimo_mantenimiento' => '2024-06-20',
            'proxima_actualizacion' => '2024-07-15',
            'estado_servidor' => 'Online',
            'memoria_uso' => '67%',
            'cpu_uso' => '42%',
            'algoritmos_disponibles' => [
                'Simulated Annealing',
                'Búsqueda Tabú',
                'Algoritmo Híbrido',
                'Optimización por Colonia de Hormigas'
            ],
            'funcionalidades' => [
                'Optimización de rutas en tiempo real',
                'Análisis predictivo de demanda',
                'Gestión automática de inventarios',
                'Reportes avanzados de rendimiento',
                'Integración con sistemas GPS'
            ]
        ];
    }
}
