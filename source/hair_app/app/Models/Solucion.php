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
        'plantilla_id',
        'conductor_id'
    ];

    protected $with = ['rutas.visitas.cliente', 'proveedor'];

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

    public function plantilla()
    {
        return $this->belongsTo(Plantilla::class);
    }

    public function visitas()
    {
        return $this->hasManyThrough(Visita::class, Ruta::class);
    }

    public function conductor() {
        return $this->belongsTo(User::class);
    }

    // public function clientes()
    // {
    //     return $this->hasManyThrough(Cliente::class, Ruta::class, 'id', 'id', 'id');
    // }
}
