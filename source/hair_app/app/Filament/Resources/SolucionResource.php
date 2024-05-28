<?php

namespace App\Filament\Resources;

use App\enums\EstadosRecorrido;
use App\Filament\Resources\SolucionResource\Pages;
use App\Models\Proveedor;
use App\Models\Solucion;
use App\Models\Vehiculo;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Filament\Forms;
class SolucionResource extends Resource
{
    protected static ?string $model = Solucion::class;
    protected static ?string $pluralModelLabel = 'Soluciones';
    protected static ?string $navigationIcon = 'heroicon-o-rectangle-stack';
   
    public static function form(Form $form): Form
    {
        return $form
            ->schema([                
                Forms\Components\TextInput::make('politica_reabastecimiento'),
                Forms\Components\TextInput::make('estado'),
                Forms\Components\TextInput::make('costo'),
                Forms\Components\Select::make('vehiculo_id')->label('Vehículo')
                    ->options(Vehiculo::all()->pluck('patente', 'id'))
                    ->required(),
                Forms\Components\Select::make('proveedor_id')->label('Proveedor')
                    ->options(Proveedor::all()->pluck('nombre', 'id'))
                    ->required(),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('id'),
                Tables\Columns\TextColumn::make('estado'),
                Tables\Columns\TextColumn::make('proveedor.nombre'),
                Tables\Columns\TextColumn::make('created_at')->label('Fecha de creación')->dateTime('d/m/Y H:m:s'),
                // Tables\Columns\TextColumn::make('clientes_count')->label('Cant. clientes')->counts('clientes'),
            ])
            ->filters([
                //
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
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
            'index' => Pages\ListSolucions::route('/'),
            'create' => Pages\CreateSolucion::route('/create'),
            'edit' => Pages\EditSolucion::route('/{record}/edit'),
        ];
    }


}
