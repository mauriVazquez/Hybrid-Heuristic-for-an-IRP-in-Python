<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Proveedor extends Model
{
    use HasFactory, HasUuids;
    protected $table = 'proveedores';


    public function zona()
    {
        return $this->belongsTo(Zona::class);
    }
    public function localidad()
    {
        return $this->belongsTo(Localidad::class);
    }
}
