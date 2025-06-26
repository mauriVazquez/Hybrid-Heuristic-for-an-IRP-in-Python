<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class UserSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        User::firstOrCreate(
            ['name' => 'Administrador'],
            [
                'name' => 'Administrador',
                'email' => 'administrador@example.com',
                'password' => Hash::make('admin123123'),
            ]);
            
        User::firstOrCreate(
            ['name' => 'Conductor'],
            [
            'name' => 'Conductor',
            'email' => 'conductor@example.com',
            'password' => Hash::make('admin123123'),
        ]);
    }
}
