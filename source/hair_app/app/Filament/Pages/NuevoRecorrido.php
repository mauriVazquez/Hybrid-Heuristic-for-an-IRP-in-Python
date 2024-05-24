<?php

namespace App\Filament\Pages;

use App\enums\EstadosRecorrido;
use App\Models\Cliente;
use App\Models\Proveedor;
use App\Models\Recorrido;
use App\Models\Vehiculo;
use App\Models\Zona;
use App\Services\HairService;
use Filament\Forms\Contracts\HasForms;
use Filament\Forms\Concerns\InteractsWithForms;
use Filament\Forms\Form;
use Filament\Forms;
use Filament\Forms\Get;
use Filament\Forms\Set;
use Filament\Pages\Page;
use Illuminate\Support\Facades\DB;
use Throwable;

class NuevoRecorrido extends Page implements HasForms
{
    protected static ?string $navigationIcon = 'heroicon-o-document-text';

    protected static string $view = 'filament.pages.nuevo-recorrido';

    use InteractsWithForms;

    public ?array $data = [];

    public $zona_id;
    public $proveedor_id;
    public $clientes;
    public $vehiculo_id;
    public $horizon_length;

    public function mount(): void
    {
        $this->form->fill([
            'zona_id' => null,
            'horizon_length' => null,
            'vehiculo_id' => null,
            'proveedor_id' => null,
            'clientes' => null,
        ]);
    }

    public function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Select::make('zona_id')
                    ->label('Zona')
                    ->options(fn () => Zona::all()->pluck('nombre', 'id'))
                    ->searchable()
                    ->live(),
                Forms\Components\TextInput::make('horizon_length')
                    ->label('Horizonte de tiempo')
                    ->numeric()
                    ->integer()
                    ->default(3)
                    ->required(),
                Forms\Components\Section::make()
                    ->schema([
                        Forms\Components\Select::make('vehiculo_id')
                            ->label('Vehículo')
                            ->options(fn () => Vehiculo::all()->pluck('patente', 'id'))
                            ->searchable()
                            ->required(),
                        Forms\Components\Select::make('proveedor_id')
                            ->label('Proveedor')
                            ->options(fn () => Proveedor::all()->pluck('nombre', 'id'))
                            ->searchable()
                            ->required(),
                        Forms\Components\Select::make('clientes')
                            ->label('Clientes')
                            ->options(function (Get $get) {
                                $zona_id = $get('zona_id');
                                $clientes = $get('clientes');
                                if (!$zona_id)
                                    return Cliente::all()->pluck('nombre', 'id');

                                return Cliente::where('zona_id', $zona_id)->when(
                                    !empty($clientes),
                                    function ($query) use ($clientes) {
                                        $query->orWhereIn('id', $clientes);
                                    }
                                )->get()->pluck('nombre', 'id');
                            })
                            ->multiple()
                            ->required(),
                    ])
                    ->columns(1),

            ]);
    }

    public function submit()
    {
        try {
            DB::transaction(function () {
                $formData = $this->form->getState();
                $recorrido = Recorrido::create([
                    'proveedor_id' => $formData['proveedor_id'],
                    'vehiculo_id' => $formData['vehiculo_id'],
                    'horizon_length' => $formData['horizon_length'],
                    'estado' => EstadosRecorrido::Pendiente,
                ]);

                $recorrido->clientes()->attach($formData['clientes']);
                $hairService = new HairService;
                $response = $hairService->enviarSolicitudEjecucion($recorrido->id, $recorrido->proveedor, $recorrido->clientes->pluck('id'), $recorrido->vehiculo, $recorrido->horizon_length);
            });
        } catch (Throwable $th) {
            info($th->getMessage());
            info($th->getTraceAsString());
        }

        return redirect('admin/recorridos');
    }
}
