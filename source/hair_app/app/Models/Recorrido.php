<?php

namespace App\Models;

use App\enums\EstadosRecorrido;
use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Recorrido extends Model
{
    use HasFactory, HasUuids;

    protected $table = 'recorridos';

    protected $fillable = [
        'proveedor_id',
        'vehiculo_id',
        'horizon_length',
        'estado'
    ];

    protected $casts = [
        'estado' => EstadosRecorrido::class
    ];

    public function proveedor()
    {
        return $this->belongsTo(Proveedor::class);
    }

    public function vehiculo()
    {
        return $this->belongsTo(Vehiculo::class);
    }

    public function clientes()
    {
        return $this->belongsToMany(Cliente::class, 'clientes_recorridos');
    }

    public function solucion()
    {
        return $this->hasOne(Solucion::class)->latestOfMany();
    }
}
