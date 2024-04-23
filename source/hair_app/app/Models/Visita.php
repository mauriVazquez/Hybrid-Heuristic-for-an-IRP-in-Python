<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Visita extends Model
{
    use HasFactory, HasUuids;
    protected $table = 'visitas';

    protected $fillable = [
        'ruta_id',
        'cliente_id',
        'orden',
        'cantidad',
        'realizada'
    ];

    protected $casts = [
        'realizada' => 'boolean',
        'cantidad' => 'integer',
    ];

    public function ruta()
    {
        return $this->belongsTo(Ruta::class);
    }

    public function cliente()
    {
        return $this->belongsTo(Cliente::class);
    }
}
