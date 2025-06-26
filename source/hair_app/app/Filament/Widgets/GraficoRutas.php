<?php

namespace App\Filament\Widgets;

use Filament\Widgets\ChartWidget;

class GraficoRutas extends ChartWidget
{
    protected static ?string $heading = 'Rutas por Mes';
    
    protected static ?int $sort = 2;
    
    protected static ?string $pollingInterval = '30s';

    protected function getData(): array
    {
        return [
            'datasets' => [
                [
                    'label' => 'Rutas Optimizadas',
                    'data' => $this->getRutasData(),
                    'backgroundColor' => '#36A2EB',
                    'borderColor' => '#36A2EB',
                ],
                [
                    'label' => 'Rutas Tradicionales',
                    'data' => $this->getRutasTradicionalesData(),
                    'backgroundColor' => '#FF6384',
                    'borderColor' => '#FF6384',
                ],
            ],
            'labels' => ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
        ];
    }

    protected function getType(): string
    {
        return 'line';
    }

    private function getRutasData(): array
    {
        // Data mock - rutas optimizadas por mes
        return [45, 52, 48, 61, 55, 67, 73, 69, 76, 82, 78, 85];
    }

    private function getRutasTradicionalesData(): array
    {
        // Data mock - rutas tradicionales por mes
        return [32, 38, 35, 42, 39, 45, 48, 44, 51, 56, 53, 58];
    }

    protected function getOptions(): array
    {
        return [
            'plugins' => [
                'legend' => [
                    'display' => true,
                ],
            ],
            'scales' => [
                'y' => [
                    'beginAtZero' => true,
                ],
            ],
        ];
    }
}
