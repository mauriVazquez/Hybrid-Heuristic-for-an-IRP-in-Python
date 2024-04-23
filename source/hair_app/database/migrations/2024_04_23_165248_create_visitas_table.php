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
        Schema::create('visitas', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('ruta_id')->references('id')->on('rutas');
            $table->foreignUuid('cliente_id')->references('id')->on('clientes');
            $table->integer('orden');
            $table->integer('cantidad');
            $table->boolean('realizada');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('visitas');
    }
};
