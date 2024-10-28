<?php

namespace App\enums;

use Filament\Support\Contracts\HasLabel;

enum EstadosEnum: int implements HasLabel
{
    case Pendiente = 1;
    case Procesando = 2;
    case Resuelto = 3;
    case Rechazado = 4;

    public function getLabel(): ?string
    {
        return $this->name;
    }
}
