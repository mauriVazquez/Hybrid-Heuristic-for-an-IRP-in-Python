<?php

namespace App\Filament\Resources;

use App\Filament\Resources\SolucionResource\Pages;
use App\Models\Solucion;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;

class SolucionResource extends Resource
{
    protected static ?string $model = Solucion::class;
    protected static ?string $pluralModelLabel = 'Soluciones';
    protected static ?string $navigationIcon = 'heroicon-o-rectangle-stack';
   
    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                //
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                //
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
