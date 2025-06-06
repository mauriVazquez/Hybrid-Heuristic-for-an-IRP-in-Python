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
        Schema::create('plantillas', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('zona_id')->constrained('zonas');
            $table->foreignUuid('proveedor_id')->constrained('proveedores');
            $table->foreignUuid('vehiculo_id')->constrained('vehiculos');
            $table->integer('horizonte_tiempo')->default(3);
            $table->integer('estado');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('plantillas');
    }
};
