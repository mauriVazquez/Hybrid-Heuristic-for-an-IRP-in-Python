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
        Schema::create('soluciones', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->string('politica_reabastecimiento',2);
            $table->integer('estado');
            $table->float('costo');
            $table->foreignUuid('vehiculo_id')->constrained('vehiculos');
            $table->foreignUuid('proveedor_id')->constrained('proveedores');
            $table->foreignUuid('plantilla_id')->references('id')->on('plantillas');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('soluciones');
    }
};
