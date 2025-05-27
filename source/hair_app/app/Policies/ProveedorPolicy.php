<?php

namespace App\Policies;

use App\Models\User;
use App\Models\Proveedor;
use Illuminate\Auth\Access\HandlesAuthorization;

class ProveedorPolicy
{
    use HandlesAuthorization;

    public function viewAny(User $user)
    {
        return $user->hasRole('admin');
    }

    public function view(User $user, Proveedor $proveedor)
    {
        return $user->hasRole('admin');
    }

    public function create(User $user)
    {
        return $user->hasRole('admin');
    }

    public function update(User $user, Proveedor $proveedor)
    {
        return $user->hasRole('admin');
    }

    public function delete(User $user, Proveedor $proveedor)
    {
        return $user->hasRole('admin');
    }
}
