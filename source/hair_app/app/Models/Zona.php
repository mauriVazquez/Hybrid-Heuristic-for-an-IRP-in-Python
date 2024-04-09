<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Zona extends Model
{
    use HasFactory, HasUuids;
    protected $table = 'zonas';

    public function clientes()
    {
        return $this->hasMany(Cliente::class);
    }
    public function proveedores()
    {
        return $this->hasMany(Proveedor::class);
    }
    public function vehiculos()
    {
        return $this->hasMany(Vehiculo::class);
    }
    public function formulariosEjecucion()
    {
        return $this->hasMany(FormularioEjecucion::class);
    }
}
