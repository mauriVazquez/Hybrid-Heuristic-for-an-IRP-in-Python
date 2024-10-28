<?php

namespace App\Filament\Resources\RecorridoResource\Pages;

use App\enums\EstadosEnum;
use App\Filament\Resources\RecorridoResource;
use Filament\Actions;
use Filament\Resources\Pages\CreateRecord;

class CreateRecorrido extends CreateRecord
{
    protected static string $resource = RecorridoResource::class;

    protected function mutateFormDataBeforeCreate(array $data): array
    {
        $data['estado'] = EstadosEnum::Pendiente;
        return $data;
    }
}
