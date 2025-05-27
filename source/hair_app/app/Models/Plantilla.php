<?php

namespace App\Models;

use App\enums\EstadosEnum;
use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Plantilla extends Model
{
    use HasFactory, HasUuids;

    protected $table = 'plantillas';

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

    public function vehiculo() : BelongsTo
    {
        return $this->belongsTo(Vehiculo::class);
    }

    public function clientes()
    {
        return $this->belongsToMany(Cliente::class, 'clientes_plantillas');
    }

    public function solucion()
    {
        return $this->hasOne(Solucion::class)->latestOfMany();
    }
}
