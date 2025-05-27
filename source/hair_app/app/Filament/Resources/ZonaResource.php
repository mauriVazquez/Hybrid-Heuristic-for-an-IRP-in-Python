<?php

namespace App\Filament\Resources;

use App\Filament\Resources\ZonaResource\Pages;
use App\Filament\Resources\ZonaResource\RelationManagers;
use App\Models\Zona;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\SoftDeletingScope;

class ZonaResource extends Resource
{
    protected static ?string $model = Zona::class;
    protected static ?string $pluralModelLabel = 'Zonas';
    protected static ?string $navigationIcon = 'heroicon-s-map';
    // protected static ?string $navigationGroup = 'Entidades';
    // protected static ?int $navigationSort = 0;

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\TextInput::make('nombre')->required(),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('nombre')->label('Descripción'),
                Tables\Columns\TextColumn::make('clientes_count')->label('Clientes')->counts('clientes'),
                Tables\Columns\TextColumn::make('proveedores_count')->label('Proveedores')->counts('proveedores'),
                Tables\Columns\TextColumn::make('vehiculos_count')->label('Vehiculos')->counts('vehiculos'),
            ])
            ->filters([
                //
            ])
            ->actions([
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
            'index' => Pages\ListZonas::route('/'),
            'create' => Pages\CreateZona::route('/create'),
            // 'edit' => Pages\EditZona::route('/{record}/edit'),
        ];
    }
}
