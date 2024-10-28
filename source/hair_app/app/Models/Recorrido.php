<?php

namespace App\Models;

use App\enums\EstadosEnum;
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
        'zona_id',
        'horizonte_tiempo',
        'estado'
    ];

    protected $casts = [
        'estado' => EstadosEnum::class
    ];

    public function proveedor()
    {
        return $this->belongsTo(Proveedor::class);
    }
    
    public function zona()
    {
        return $this->belongsTo(Zona::class);
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
