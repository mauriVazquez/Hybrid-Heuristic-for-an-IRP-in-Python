<?php

namespace App\Policies;

use App\Models\User;

class UserPolicy
{
    /**
     * Determine if the user can update their own password.
     */
    public function updatePassword(User $user, User $model): bool
    {
        return $user->id === $model->id && $user->hasRole('conductor');
    }

    /**
     * Determine if the user can update other fields.
     */
    public function update(User $user, User $model): bool
    {
        return $user->hasRole('admin');
    }

    /**
     * Determine if the user can delete.
     */
    public function delete(User $user, User $model): bool
    {
        return $user->hasRole('admin');
    }

    /**
     * Determine if the user can view any user.
     */
    public function viewAny(User $user): bool
    {
        return $user->hasRole('admin');
    }

    /**
     * Determine if the user can view a specific user.
     */
    public function view(User $user, User $model): bool
    {
        return $user->hasRole('admin') || $user->id === $model->id;
    }
}
