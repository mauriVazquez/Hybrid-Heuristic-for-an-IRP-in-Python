<?php

namespace App\Filament\Resources;

use App\Filament\Resources\ClienteResource\Pages;
use App\Filament\Resources\ClienteResource\RelationManagers;
use App\Models\Cliente;
use App\Models\Departamento;
use App\Models\Localidad;
use App\Models\Zona;
use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\SoftDeletingScope;
use Filament\Forms\Get;
use Filament\Forms\Set;
class ClienteResource extends Resource
{
    protected static ?string $model = Cliente::class;
    protected static ?string $pluralModelLabel = 'Clientes';
    protected static ?string $navigationIcon = 'heroicon-o-rectangle-stack';
    protected static ?string $navigationGroup = 'Entidades';


 

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Select::make('zona_id')->label('Zona')
                    ->options(Zona::all()->pluck('nombre', 'id'))
                    ->required(),
                Forms\Components\TextInput::make('nombre')
                    ->required()
                    ->maxLength(255),
                Forms\Components\Fieldset::make('Ubicación')
                ->schema([
                    Forms\Components\Select::make('departamento')
                        ->options(Departamento::all()->pluck('nombre', 'id'))
                        ->native(false)
                        ->afterStateUpdated(fn (Set $set, ?string $state) => $set('localidad', ''))
                        ->live(),
                    Forms\Components\Select::make('localidad')
                        ->options(fn (Get  $get) => Localidad::where('departamento_id',$get('departamento'))->pluck('nombre', 'id'))
                        ->required()
                        ->native(false),
                    Forms\Components\TextInput::make('direccion')->label('Dirección')
                        ->required()
                        ->maxLength(255)
                        ->columnSpan(2),
                    Forms\Components\Fieldset::make('Coordenadas')
                        ->schema([
                        Forms\Components\TextInput::make('coord_x')->label('Longitud')
                            ->required()
                            ->maxLength(255),
                        Forms\Components\TextInput::make('coord_y')->label('Latitud')
                            ->required()
                            ->maxLength(255),
                        ])
                ]),


                Forms\Components\TextInput::make('costo_almacenamiento')->label('Costo de almacenamiento')
                    ->required()
                    ->maxLength(255),
                Forms\Components\TextInput::make('nivel_almacenamiento')->label('Nivel actual')
                    ->required()
                    ->maxLength(255),
                Forms\Components\TextInput::make('nivel_maximo')->label('Nivel máximo')
                    ->required()
                    ->maxLength(255),
                Forms\Components\TextInput::make('nivel_minimo')->label('Nivel mínimo')
                    ->required()
                    ->maxLength(255),
                Forms\Components\TextInput::make('nivel_demanda')->label('Nivel de demanda')
                    ->required()
                    ->maxLength(255),
            ])->columns(1);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('nombre'),
                Tables\Columns\TextColumn::make('localidad.nombre'),
                Tables\Columns\TextColumn::make('direccion'),
            ])
            ->filters([
               //Filtros
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
            'index' => Pages\ListClientes::route('/'),
            'create' => Pages\CreateCliente::route('/create'),
            'edit' => Pages\EditCliente::route('/{record}/edit'),
        ];
    }
}
