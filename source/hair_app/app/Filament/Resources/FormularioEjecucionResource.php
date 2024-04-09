<?php

namespace App\Filament\Resources;

use App\Filament\Resources\FormularioEjecucionResource\Pages;
use App\Models\FormularioEjecucion;
use App\Models\Proveedor;
use App\Models\Vehiculo;
use App\Models\Zona;

use Filament\Forms;
use Filament\Forms\Form;
use Filament\Forms\Get;
use Filament\Forms\Set;

use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;

class FormularioEjecucionResource extends Resource
{
    protected static ?string $model = FormularioEjecucion::class;
    protected static ?string $pluralModelLabel = 'formularios de ejecución';
    protected static ?string $navigationIcon = 'heroicon-o-rectangle-stack';
    protected static ?string $navigationParentItem = 'Soluciones';



    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Select::make('zona_id')
                    ->label('Zona')
                    ->options(Zona::all()->pluck('nombre', 'id'))
                    ->searchable()
                    ->live()
                    ->afterStateUpdated(function (Set $set) {
                            $set('proveedor_id', null);
                            $set('clientes', null);
                            $set('vehiculo_id', null);
                    })
                    ->required(),
                Forms\Components\TextInput::make('horizon_length')
                    ->label('Horizonte de tiempo')
                    ->numeric()
                    ->integer()
                    ->default(3)
                    ->required(),
                Forms\Components\Section::make()
                    ->schema([
                        Forms\Components\Select::make('vehiculo_id')
                            ->label('Vehículo')
                            ->options(Vehiculo::all()->pluck('patente','id'))
                            ->searchable()
                            ->required(),
                        Forms\Components\Select::make('proveedor_id')
                            ->label('Proveedor')
                            ->options(Proveedor::all()->pluck('nombre','id'))
                            ->searchable()
                            ->required(),
                        Forms\Components\Select::make('clientes')
                            ->label('Clientes')
                            ->relationship('clientes', 'nombre')
                            ->multiple()
                            ->required(),
                    ])
                    ->columns(1)
                    ->visible(fn (Get $get): bool => $get('zona_id') ? true : false),
                
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('zona.nombre')->label('Zona'),
                Tables\Columns\TextColumn::make('clientes_count')->label('Clientes')->counts('clientes'),
                // Tables\Columns\TextColumn::make('proveedores_count')->label('Proveedores')->counts('proveedores'),
                Tables\Columns\TextColumn::make('proveedor.nombre')->label('Proveedor'),
                Tables\Columns\TextColumn::make('vehiculo.capacidad')->label('Capacidad vehículo')
                ->description(fn (FormularioEjecucion $record): string => "Patente: ".$record->vehiculo->patente),
                Tables\Columns\TextColumn::make('updated_at')->date('d/m/Y H:i')->label('Última edición'),
            ])
            ->filters([
                //
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
                Tables\Actions\ViewAction::make(),
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
            'index' => Pages\ListFormularioEjecucions::route('/'),
            'create' => Pages\CreateFormularioEjecucion::route('/create'),
            'edit' => Pages\EditFormularioEjecucion::route('/{record}/edit'),
            'view' => Pages\ViewFormularioEjecucion::route('/hair/{record}'),
        ];
    }
}
