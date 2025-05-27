<?php

namespace App\Policies;

use App\Models\User;
use App\Models\Plantilla;
use Illuminate\Auth\Access\HandlesAuthorization;

class PlantillaPolicy
{
    use HandlesAuthorization;

    public function viewAny(User $user)
    {
        return $user->hasRole('admin');
    }

    public function view(User $user, Plantilla $plantilla)
    {
        return $user->hasRole('admin');
    }

    public function create(User $user)
    {
        return $user->hasRole('admin');
    }

    public function update(User $user, Plantilla $plantilla)
    {
        return $user->hasRole('admin');
    }

    public function delete(User $user, Plantilla $plantilla)
    {
        return $user->hasRole('admin');
    }
}
