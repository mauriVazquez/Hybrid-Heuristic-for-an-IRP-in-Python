<?php

namespace App\Filament\Resources;

use App\Filament\Resources\SolucionResource\Pages;
use App\Models\Proveedor;
use App\Models\Solucion;
use App\Models\Vehiculo;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Filament\Forms;
use Illuminate\Database\Eloquent\Builder;

class SolucionResource extends Resource
{
    protected static ?string $model = Solucion::class;
    protected static ?string $pluralModelLabel = 'Soluciones';
    protected static ?string $navigationIcon = 'heroicon-o-rectangle-stack';
   
    public static function getSlug(): string
    {
        return 'soluciones'; // Cambia la URL del recurso de 'users' a 'usuarios'.
    }

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
                //
                Tables\Columns\TextColumn::make('plantilla_id')->label('Plantilla'),
                Tables\Columns\SelectColumn::make('conductor_id')->label('Conductor')->options(function(){
                    return \App\Models\User::all()->pluck('name', 'id');
                })->afterStateUpdated(function($record, $column,){
                    $record->conductor?->assignRole('conductor');
                })->hidden(fn() => !auth()->user()->hasRole('admin')),
                Tables\Columns\TextColumn::make('costo')->label('Costo'),
                Tables\Columns\TextColumn::make('created_at')->label('fecha')->since(),
            ])
            ->filters([
                //
            ])
            ->actions([
                // Tables\Actions\EditAction::make(),
                Tables\Actions\ViewAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                ]),
            ])
            ->modifyQueryUsing(function (Builder $query) {
                if (auth()->user()->hasRole('conductor')) {
                    $query->where('conductor_id', auth()->id());
                }
            });
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
            'view' => Pages\ViewSolucion::route('/{record}'),
        ];
    }

    
}
