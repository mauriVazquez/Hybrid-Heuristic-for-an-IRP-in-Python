<?php

namespace App\Models;
use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Vehiculo extends Model
{
    use HasFactory, HasUuids;

    protected $fillable = [
        'patente',
        'marca',
        'nombre_modelo',
        'anio',
        'color',
        'capacidad',
        'zona_id'
    ];

    public function zona()
    {
        return $this->belongsTo(Zona::class);
    }
}
