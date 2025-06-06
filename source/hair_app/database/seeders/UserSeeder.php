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
            ['name' => 'Admin'],
            [
                'name' => 'Admin',
                'email' => 'admin@admin.com',
                'password' => Hash::make('admin123'),
            ]);
            
        User::firstOrCreate(
            ['name' => 'Mauricio'],
            [
            'name' => 'Mauricio',
            'email' => 'test@example.com',
            'password' => Hash::make('password'),
        ]);
    }
}
