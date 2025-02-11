<?php

namespace App\Policies;

use App\Models\User;
use App\Models\Zona;
use Illuminate\Auth\Access\HandlesAuthorization;

class ZonaPolicy
{
    use HandlesAuthorization;

    public function viewAny(User $user)
    {
        return $user->hasRole('admin');
    }

    public function view(User $user, Zona $zona)
    {
        return $user->hasRole('admin');
    }

    public function create(User $user)
    {
        return $user->hasRole('admin');
    }

    public function update(User $user, Zona $zona)
    {
        return $user->hasRole('admin');
    }

    public function delete(User $user, Zona $zona)
    {
        return $user->hasRole('admin');
    }
}
