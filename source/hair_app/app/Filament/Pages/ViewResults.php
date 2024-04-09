<?php

namespace App\Filament\Pages;

use App\Models\Zona;
use Filament\Pages\Page;
use Illuminate\Support\Facades\Request;

class ViewResults extends Page
{
    protected static ?string $navigationIcon = 'heroicon-o-document-text';

    protected static string $view = 'filament.pages.view-results';

}
