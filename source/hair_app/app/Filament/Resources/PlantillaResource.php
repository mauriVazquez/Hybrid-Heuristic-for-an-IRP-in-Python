<?php

namespace App\Filament\Resources;

use App\enums\EstadosEnum;
use App\Filament\Resources\PlantillaResource\Pages;
use App\Models\Cliente;
use App\Models\Proveedor;
use App\Models\Plantilla;
use App\Models\Vehiculo;
use App\Models\Zona;
use App\Services\HairService;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Forms\Get;
use Filament\Notifications\Notification;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;

class PlantillaResource extends Resource
{
    protected static ?string $model = Plantilla::class;

    protected static ?string $navigationIcon = 'heroicon-o-rectangle-stack';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Select::make('zona_id')
                    ->label('Zona')
                    ->options(fn() => Zona::all()->pluck('nombre', 'id'))
                    ->searchable()
                    ->live(),
                Forms\Components\TextInput::make('horizonte_tiempo')
                    ->label('Horizonte de tiempo')
                    ->numeric()
                    ->integer()
                    ->default(3)
                    ->required(),
                Forms\Components\Section::make()
                    ->schema([
                        Forms\Components\Select::make('vehiculo_id')
                            ->label('Vehículo')
                            ->options(fn() => Vehiculo::all()->pluck('patente', 'id'))
                            ->searchable()
                            ->required(),
                        Forms\Components\Select::make('proveedor_id')
                            ->label('Proveedor')
                            ->options(fn() => Proveedor::all()->pluck('nombre', 'id'))
                            ->searchable()
                            ->required(),
                        Forms\Components\Select::make('clientes')
                            ->label('Clientes')
                            ->options(function (Get $get) {
                                $zona_id = $get('zona_id');
                                $clientes = $get('clientes');
                                if (!$zona_id)
                                    return Cliente::all()->pluck('nombre', 'id');

                                return Cliente::where('zona_id', $zona_id)->when(
                                    !empty($clientes),
                                    function ($query) use ($clientes) {
                                        $query->orWhereIn('id', $clientes);
                                    }
                                )->get()->pluck('nombre', 'id');
                            })
                            ->relationship('clientes', 'nombre')
                            ->multiple()
                            ->required(),
                    ])
                    ->columns(1),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                //
                // Tables\Columns\TextColumn::make('id'),
                Tables\Columns\TextColumn::make('zona.nombre'),
                Tables\Columns\TextColumn::make('proveedor.nombre'),
                Tables\Columns\TextColumn::make('horizonte_tiempo'),
                Tables\Columns\TextColumn::make('clientes_count')->label('Cant. clientes')->counts('clientes'),
                Tables\Columns\TextColumn::make('estado')
                    ->label('Estado')
                    ->badge()
                    ->color(fn($state): string => match ($state) {
                        EstadosEnum::Pendiente => 'gray',
                        EstadosEnum::Procesando => 'warning',
                        EstadosEnum::Resuelto => 'success',
                        EstadosEnum::Rechazado => 'danger',
                    }),
            ])
            ->filters([
                //
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
                Tables\Actions\Action::make('Ejecutar')->action(function (Plantilla $record) {       
                    info("enviar");
                    $hairService = new HairService;
                    $response = $hairService->enviarSolicitudEjecucion($record->id, $record->proveedor, $record->clientes->pluck('id'), $record->vehiculo, $record->horizonte_tiempo);
                    Notification::make('Solicitud Enviada')
                        ->title('Solicitud enviada')
                        ->body("Se está procesando la ruta")
                        ->success()
                        ->broadcast(auth()->user());
                }),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                ]),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListPlantillas::route('/'),
            'create' => Pages\CreatePlantilla::route('/nuevo-plantilla'),
            'edit' => Pages\EditPlantilla::route('/{record}/edit'),
        ];
    }
}
