<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Ruta extends Model
{
    use HasFactory, HasUuids;
    protected $table = 'rutas';

    protected $fillable = [
        'costo',
        'orden',
        'solucion_id'
    ];

    public function solucion()
    {
        return $this->belongsTo(Solucion::class);
    }

    public function visitas()
    {
        return $this->hasMany(Visita::class);
    }

    // public function clientes()
    // {
    //     return $this->hasManyThrough(Cliente::class, Visita::class);
    // }
}
