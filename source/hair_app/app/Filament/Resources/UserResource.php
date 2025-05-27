<?php

namespace App\Filament\Resources;

use App\Models\User;
use Filament\Forms;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Forms\Components\TextInput;
use Filament\Forms\Components\Select;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Actions\EditAction;
use Filament\Tables\Actions\DeleteAction;
use Filament\Forms\Components\CheckboxList;
use Spatie\Permission\Models\Role;
use Spatie\Permission\Models\Permission;
use App\Filament\Resources\UserResource\Pages;

class UserResource extends Resource
{
    protected static ?string $model = User::class;
    protected static ?string $navigationIcon = 'heroicon-o-user';

    public static function form(Forms\Form $form): Forms\Form
    {
        return $form
            ->schema([
                TextInput::make('name')
                    ->required()
                    ->maxLength(255)
                    ->disabled(fn ($record) => !auth()->user()?->can('update', $record)),
                TextInput::make('email')
                    ->email()
                    ->unique(User::class, 'email', ignoreRecord: true)
                    ->required()
                    ->disabled(fn ($record) => !auth()->user()?->can('update', $record)),
                TextInput::make('password')
                    ->password()
                    ->dehydrateStateUsing(fn ($state) => bcrypt($state))
                    ->required()
                    ->maxLength(255)
                    ->disabled(fn ($record) => !auth()->user()?->can('update', $record) && !auth()->user()?->can('updatePassword', $record)),
                Select::make('roles')
                    ->multiple()
                    ->relationship('roles', 'name')
                    ->preload()
                    ->required()
                    ->disabled(fn ($record) => !auth()->user()?->can('update', $record)),
                CheckboxList::make('permissions')
                    ->relationship('permissions', 'name')
                    ->columns(2)
                    ->required()
                    ->disabled(fn ($record) => !auth()->user()?->can('update', $record)),
            ]);
    }

    public static function table(Tables\Table $table): Tables\Table
    {
        return $table
            ->columns([
                TextColumn::make('name')->sortable()->searchable(),
                TextColumn::make('email')->sortable()->searchable(),
                TextColumn::make('roles.name')->label('Roles')->badge(),
            ])
            ->actions([
                EditAction::make()->authorize(fn ($record) => auth()->user()?->can('update', $record) || auth()->user()?->can('updatePassword', $record)),
                DeleteAction::make()->authorize(fn ($record) => auth()->user()?->can('delete', $record)),
            ]);
    }

    public static function getRelations(): array
    {
        return [];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListUsers::route('/'),
            'create' => Pages\CreateUser::route('/create'),
            'edit' => Pages\EditUser::route('/{record}/edit'),
        ];
    }
}
