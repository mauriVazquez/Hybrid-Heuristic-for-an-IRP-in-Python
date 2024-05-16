<?php

namespace App\Filament\Resources;

use App\enums\EstadosRecorrido;
use App\Filament\Resources\RecorridoResource\Pages;
use App\Filament\Resources\RecorridoResource\RelationManagers;
use App\Models\Recorrido;
use App\Services\HairService;
use Filament\Actions\Action;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Notifications\Notification;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\SoftDeletingScope;

class RecorridoResource extends Resource
{
    protected static ?string $model = Recorrido::class;

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
                Tables\Columns\TextColumn::make('id'),
                Tables\Columns\TextColumn::make('proveedor.nombre'),
                Tables\Columns\TextColumn::make('clientes_count')->label('Cant. clientes')->counts('clientes'),
                Tables\Columns\TextColumn::make('estado')
                    ->label('Estado')
                    ->badge()
                    ->color(fn ($state): string => match ($state) {
                        EstadosRecorrido::Pendiente => 'gray',
                        EstadosRecorrido::Procesando => 'warning',
                        EstadosRecorrido::Resuelto => 'success',
                        EstadosRecorrido::Rechazado => 'danger',
                    }),
            ])
            ->filters([
                //
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
                Tables\Actions\Action::make('Ejecutar')->action(function (Recorrido $record) {

                    $hairService = new HairService;
                    $response = $hairService->enviarSolicitudEjecucion($record->id, $record->proveedor, $record->clientes->pluck('id'), $record->vehiculo, $record->horizon_length);

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
            'index' => Pages\ListRecorridos::route('/'),
            'create' => Pages\CreateRecorrido::route('/nuevo-recorrido'),
            // 'edit' => Pages\EditRecorrido::route('/{record}/edit'),
        ];
    }
}
