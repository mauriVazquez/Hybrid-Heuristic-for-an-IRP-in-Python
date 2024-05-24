<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Solucion extends Model
{
    use HasFactory, HasUuids;
    protected $table = 'soluciones';

    protected $fillable = [
        'costo',
        'estado',
        'politica_reabastecimiento',
        'vehiculo_id',
        'proveedor_id',
        'recorrido_id',
    ];

    public function vehiculo()
    {
        return $this->belongsTo(Vehiculo::class);
    }

    public function rutas()
    {
        return $this->hasMany(Ruta::class);
    }

    public function proveedor()
    {
        return $this->belongsTo(Proveedor::class);
    }

    public function recorrido()
    {
        return $this->belongsTo(Recorrido::class);
    }
}
