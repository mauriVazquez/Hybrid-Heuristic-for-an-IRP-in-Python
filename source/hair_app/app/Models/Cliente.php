<?php

namespace App\Models;
use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Cliente extends Model
{
    use HasFactory, HasUuids;
    protected $table = 'clientes';

    protected $fillable = [
        'nombre',
        'direccion',
        'coord_x',
        'coord_y',
        'nivel_maximo',
        'nivel_minimo',
        'nivel_almacenamiento',
        'nivel_demanda',
        'costo_almacenamiento',
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
    public function plantillas()
    {
        return $this->belongsToMany(Plantilla::class);
    }
}
