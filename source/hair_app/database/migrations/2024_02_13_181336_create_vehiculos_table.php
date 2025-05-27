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
        Schema::create('vehiculos', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->string('patente')->unique();
            $table->string('marca');
            $table->string('nombre_modelo');
            $table->integer('anio');
            $table->string('color');
            $table->unsignedBigInteger('capacidad');
            $table->foreignUuid('zona_id')->constrained('zonas');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('vehiculos');
    }
};
