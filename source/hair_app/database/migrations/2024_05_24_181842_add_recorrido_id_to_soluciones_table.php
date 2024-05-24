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
        Schema::table('soluciones', function (Blueprint $table) {
            //
            $table->foreignUuid('recorrido_id')->references('id')->on('recorridos');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('soluciones', function (Blueprint $table) {
            //
            $table->dropColumn('recorrido_id');
        });
    }
};
