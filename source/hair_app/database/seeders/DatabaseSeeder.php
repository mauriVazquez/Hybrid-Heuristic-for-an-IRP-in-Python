<?php

namespace Database\Seeders;

// use Illuminate\Database\Console\Seeds\WithoutModelEvents;

use App\Models\User;
use Illuminate\Database\Seeder;
use Database\Seeders\LocalidadesSeeder;
use Database\Seeders\EntidadSeeder;
use Spatie\Permission\Models\Role;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     */
    public function run(): void
    {   
        // create admin role and conductor role
        Role::firstOrCreate(['name' => 'admin']);
        Role::firstOrCreate(['name' => 'conductor']);

        $this->call([
            LocalidadesSeeder::class,
            EntidadSeeder::class,
            UserSeeder::class,
        ]);

        $admin = User::where('name', 'Administrador')->first();
        $admin->assignRole('admin');

        $conductor = User::where('name', 'Conductor')->first();
        $conductor->assignRole('conductor');
    }
    
}
