<?php

namespace App\Policies;

use App\Models\User;
use App\Models\Cliente;
use Illuminate\Auth\Access\HandlesAuthorization;

class ClientePolicy
{
    use HandlesAuthorization;

    public function viewAny(User $user)
    {
        return $user->hasRole('admin');
    }

    public function view(User $user, Cliente $cliente)
    {
        return $user->hasRole('admin');
    }

    public function create(User $user)
    {
        return $user->hasRole('admin');
    }

    public function update(User $user, Cliente $cliente)
    {
        return $user->hasRole('admin');
    }

    public function delete(User $user, Cliente $cliente)
    {
        return $user->hasRole('admin');
    }
}
