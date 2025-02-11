<?php

namespace App\Policies;

use App\Models\User;
use App\Models\Solucion;
use Illuminate\Auth\Access\HandlesAuthorization;

class SolucionPolicy
{
    use HandlesAuthorization;

    public function viewAny(User $user)
    {
        return $user->hasRole('admin') || $user->hasRole('conductor');
    }

    public function view(User $user, Solucion $solucion)
    {
        return $user->hasRole('admin') || ($user->hasRole('conductor') && $user->id === $solucion->conductor_id);
    }

    public function create(User $user)
    {
        return $user->hasRole('admin');
    }

    public function update(User $user, Solucion $solucion)
    {
        return $user->hasRole('admin');
    }

    public function delete(User $user, Solucion $solucion)
    {
        return $user->hasRole('admin');
    }
}
