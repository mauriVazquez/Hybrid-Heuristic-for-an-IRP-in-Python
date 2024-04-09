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
        Schema::create('formularios_ejecucion', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('zona_id')->constrained('zonas');
            $table->integer('horizon_length');
            $table->foreignUuid('vehiculo_id')->constrained('vehiculos');
            $table->foreignUuid('proveedor_id')->constrained('proveedores');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('formularios_ejecucion');
    }
};
