<?php

namespace App\Filament\Widgets;

use Filament\Widgets\StatsOverviewWidget as BaseWidget;
use Filament\Widgets\StatsOverviewWidget\Stat;

class EstadisticasGenerales extends BaseWidget
{
    protected static ?int $sort = 1;
    
    protected static ?string $pollingInterval = '15s';

    protected function getStats(): array
    {
        return [
            Stat::make('Total Clientes', $this->getTotalClientes())
                ->description('Clientes registrados')
                ->descriptionIcon('heroicon-m-users')
                ->color('success')
                ->chart([7, 2, 10, 3, 15, 4, 17]),
            
            Stat::make('Rutas Optimizadas', $this->getRutasOptimizadas())
                ->description('Rutas generadas este mes')
                ->descriptionIcon('heroicon-m-map')
                ->color('info')
                ->chart([15, 4, 10, 2, 12, 4, 22]),
            
            Stat::make('Costo Promedio', '$' . number_format($this->getCostoPromedio(), 2))
                ->description('Por ruta optimizada')
                ->descriptionIcon('heroicon-m-currency-dollar')
                ->color('warning')
                ->chart([3, 8, 5, 10, 6, 12, 4]),
            
            Stat::make('Ahorro Total', '$' . number_format($this->getAhorroTotal(), 2))
                ->description('Respecto a rutas tradicionales')
                ->descriptionIcon('heroicon-m-arrow-trending-down')
                ->color('success')
                ->chart([2, 4, 6, 8, 10, 12, 14]),
        ];
    }

    private function getTotalClientes(): int
    {
        // Data mock - en producción esto vendría de la base de datos
        return 89;
    }

    private function getRutasOptimizadas(): int
    {
        // Data mock
        return 156;
    }

    private function getCostoPromedio(): float
    {
        // Data mock
        return 2845.67;
    }

    private function getAhorroTotal(): float
    {
        // Data mock
        return 15420.30;
    }
}
