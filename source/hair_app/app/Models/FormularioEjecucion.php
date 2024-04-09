<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class FormularioEjecucion extends Model
{
    use HasFactory, HasUuids;
    protected $table = 'formularios_ejecucion';

    protected $fillable = [
        'zona_id',
        'horizon_length',
        'vehiculo_id',
        'proveedor_id',
    ];

    public function zona()
    {
        return $this->belongsTo(Zona::class);
    }
    public function vehiculo()
    {
        return $this->belongsTo(Vehiculo::class);
    }
    public function proveedor()
    {
        return $this->belongsTo(Proveedor::class);
    }
    public function clientes()
    {
        return $this->belongsToMany(Cliente::class);
    }
}
