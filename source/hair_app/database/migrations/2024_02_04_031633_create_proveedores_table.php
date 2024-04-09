<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('proveedores', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->string('nombre');
            $table->string('direccion');
            $table->float('coord_x');
            $table->float('coord_y');
            $table->float('costo_almacenamiento');
            $table->integer('nivel_almacenamiento');
            $table->integer('nivel_produccion');
            $table->foreignUuid('zona_id')->constrained('zonas');
            $table->foreignId('localidad_id')->constrained('localidades');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('proveedores');
    }
};
