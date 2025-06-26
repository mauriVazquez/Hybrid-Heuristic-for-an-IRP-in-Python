<?php

namespace App\Filament\Widgets;

use Filament\Widgets\ChartWidget;

class RendimientoAlgoritmo extends ChartWidget
{
    protected static ?string $heading = 'Rendimiento del Algoritmo Híbrido';
    
    protected static ?int $sort = 5;
    
    protected static ?string $pollingInterval = '60s';

    protected function getData(): array
    {
        return [
            'datasets' => [
                [
                    'label' => 'Tiempo de Ejecución (segundos)',
                    'data' => $this->getTiemposEjecucion(),
                    'backgroundColor' => 'rgba(75, 192, 192, 0.2)',
                    'borderColor' => 'rgba(75, 192, 192, 1)',
                    'yAxisID' => 'y',
                ],
                [
                    'label' => 'Iteraciones',
                    'data' => $this->getIteraciones(),
                    'backgroundColor' => 'rgba(255, 99, 132, 0.2)',
                    'borderColor' => 'rgba(255, 99, 132, 1)',
                    'yAxisID' => 'y1',
                ],
            ],
            'labels' => ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
        ];
    }

    protected function getType(): string
    {
        return 'line';
    }

    private function getTiemposEjecucion(): array
    {
        // Data mock - tiempos de ejecución promedio por mes
        return [45, 42, 38, 41, 39, 37];
    }

    private function getIteraciones(): array
    {
        // Data mock - número promedio de iteraciones por mes
        return [1200, 1150, 1080, 1190, 1140, 1100];
    }

    protected function getOptions(): array
    {
        return [
            'responsive' => true,
            'interaction' => [
                'mode' => 'index',
                'intersect' => false,
            ],
            'scales' => [
                'x' => [
                    'display' => true,
                    'title' => [
                        'display' => true,
                        'text' => 'Mes'
                    ]
                ],
                'y' => [
                    'type' => 'linear',
                    'display' => true,
                    'position' => 'left',
                    'title' => [
                        'display' => true,
                        'text' => 'Tiempo (segundos)'
                    ]
                ],
                'y1' => [
                    'type' => 'linear',
                    'display' => true,
                    'position' => 'right',
                    'title' => [
                        'display' => true,
                        'text' => 'Iteraciones'
                    ],
                    'grid' => [
                        'drawOnChartArea' => false,
                    ],
                ],
            ],
        ];
    }
}
