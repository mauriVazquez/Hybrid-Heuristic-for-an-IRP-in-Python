<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Proveedor extends Model
{
    use HasFactory, HasUuids;
    protected $table = 'proveedores';

    protected $fillable = [
        'nombre',
        'direccion',
        'coord_x',
        'coord_y',
        'costo_almacenamiento',
        'nivel_almacenamiento',
        'nivel_produccion',
        'zona_id',
        'localidad_id',
    ];

    public function zona()
    {
        return $this->belongsTo(Zona::class);
    }
    public function localidad()
    {
        return $this->belongsTo(Localidad::class);
    }
}
