<?php

namespace Database\Seeders;

// use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Database\Seeders\LocalidadesSeeder;
use Database\Seeders\EntidadSeeder;
class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        $this->call([
            ZonaSeeder::class,
            LocalidadesSeeder::class,
            EntidadSeeder::class,
        ]);
    }
}
