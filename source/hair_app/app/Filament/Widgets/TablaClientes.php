<?php

namespace App\Filament\Widgets;

use Filament\Tables;
use Filament\Tables\Table;
use Filament\Widgets\TableWidget as BaseWidget;

class TablaClientes extends BaseWidget
{
    protected static ?string $heading = 'Clientes Recientes';
    
    protected static ?int $sort = 3;
    
    protected int | string | array $columnSpan = 'full';

    protected function getTableData(): array
    {
        return [
            [
                'id' => 1,
                'nombre' => 'Supermercado Central',
                'ciudad' => 'Buenos Aires',
                'demanda' => 150,
                'ultima_visita' => '2024-06-20',
                'estado' => 'Activo',
                'costo_entrega' => 125.50,
            ],
            [
                'id' => 2,
                'nombre' => 'Almacén Don Pedro',
                'ciudad' => 'Córdoba',
                'demanda' => 89,
                'ultima_visita' => '2024-06-18',
                'estado' => 'Activo',
                'costo_entrega' => 98.75,
            ],
            [
                'id' => 3,
                'nombre' => 'Tienda La Esquina',
                'ciudad' => 'Rosario',
                'demanda' => 67,
                'ultima_visita' => '2024-06-15',
                'estado' => 'Pendiente',
                'costo_entrega' => 87.30,
            ],
            [
                'id' => 4,
                'nombre' => 'Mercado San Martín',
                'ciudad' => 'Mendoza',
                'demanda' => 203,
                'ultima_visita' => '2024-06-12',
                'estado' => 'Activo',
                'costo_entrega' => 156.90,
            ],
            [
                'id' => 5,
                'nombre' => 'Distribuidora Norte',
                'ciudad' => 'Salta',
                'demanda' => 134,
                'ultima_visita' => '2024-06-10',
                'estado' => 'Inactivo',
                'costo_entrega' => 112.45,
            ],
        ];
    }

    public function table(Table $table): Table
    {
        return $table
            // ->data($this->getTableData())
            ->columns([
                Tables\Columns\TextColumn::make('nombre')
                    ->label('Cliente')
                    ->searchable()
                    ->sortable(),
                Tables\Columns\TextColumn::make('ciudad')
                    ->label('Ciudad')
                    ->searchable(),
                Tables\Columns\TextColumn::make('demanda')
                    ->label('Demanda')
                    ->numeric()
                    ->sortable(),
                Tables\Columns\TextColumn::make('ultima_visita')
                    ->label('Última Visita')
                    ->date()
                    ->sortable(),
                Tables\Columns\BadgeColumn::make('estado')
                    ->label('Estado')
                    ->colors([
                        'success' => 'Activo',
                        'warning' => 'Pendiente',
                        'danger' => 'Inactivo',
                    ]),
                Tables\Columns\TextColumn::make('costo_entrega')
                    ->label('Costo Entrega')
                    ->money('USD')
                    ->sortable(),
            ])
            ->defaultSort('ultima_visita', 'desc')
            ->paginated([5, 10]);
    }
}
