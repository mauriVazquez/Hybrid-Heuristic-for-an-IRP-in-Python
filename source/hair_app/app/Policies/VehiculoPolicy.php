<?php

namespace App\Policies;

use App\Models\User;
use App\Models\Vehiculo;
use Illuminate\Auth\Access\HandlesAuthorization;

class VehiculoPolicy
{
    use HandlesAuthorization;

    public function viewAny(User $user)
    {
        return $user->hasRole('admin');
    }

    public function view(User $user, Vehiculo $vehiculo)
    {
        return $user->hasRole('admin');
    }

    public function create(User $user)
    {
        return $user->hasRole('admin');
    }

    public function update(User $user, Vehiculo $vehiculo)
    {
        return $user->hasRole('admin');
    }

    public function delete(User $user, Vehiculo $vehiculo)
    {
        return $user->hasRole('admin');
    }
}
