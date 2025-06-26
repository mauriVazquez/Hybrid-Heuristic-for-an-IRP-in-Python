<?php

namespace App\Filament\Widgets;

use Filament\Widgets\ChartWidget;

class GraficoCostos extends ChartWidget
{
    protected static ?string $heading = 'Distribución de Costos';
    
    protected static ?int $sort = 4;

    protected function getData(): array
    {
        return [
            'datasets' => [
                [
                    'label' => 'Costos por Categoría',
                    'data' => $this->getCostosData(),
                    'backgroundColor' => [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF',
                        '#FF9F40',
                    ],
                ],
            ],
            'labels' => $this->getCategoriasLabels(),
        ];
    }

    protected function getType(): string
    {
        return 'doughnut';
    }

    private function getCostosData(): array
    {
        // Data mock - distribución de costos
        return [35, 25, 20, 12, 5, 3];
    }

    private function getCategoriasLabels(): array
    {
        return [
            'Combustible',
            'Mantenimiento',
            'Salarios',
            'Seguros',
            'Peajes',
            'Otros'
        ];
    }

    protected function getOptions(): array
    {
        return [
            'plugins' => [
                'legend' => [
                    'display' => true,
                    'position' => 'bottom',
                ],
            ],
            'maintainAspectRatio' => false,
        ];
    }
}
