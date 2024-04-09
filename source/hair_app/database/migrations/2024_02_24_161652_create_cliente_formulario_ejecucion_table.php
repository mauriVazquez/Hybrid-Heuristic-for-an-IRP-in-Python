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
        Schema::create('cliente_formulario_ejecucion', function (Blueprint $table) {
            $table->foreignUuid('formulario_ejecucion_id')->constrained('formularios_ejecucion');
            $table->foreignUuid('cliente_id')->constrained('clientes');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('cliente_formulario_ejecucion');
    }
};
