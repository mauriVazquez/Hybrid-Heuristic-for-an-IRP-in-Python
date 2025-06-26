<?php

return [
    /*
    |--------------------------------------------------------------------------
    | Dashboard Configuration
    |--------------------------------------------------------------------------
    |
    | Configuration options for the Hair App Dashboard
    |
    */

    'mock_data' => [
        'enabled' => env('DASHBOARD_MOCK_DATA', true),
        'auto_refresh' => env('DASHBOARD_AUTO_REFRESH', true),
        'polling_intervals' => [
            'stats' => '15s',
            'charts' => '30s',
            'performance' => '60s',
        ],
    ],

    'widgets' => [
        'estadisticas_generales' => [
            'enabled' => true,
            'sort' => 1,
            'span' => 'full',
        ],
        'grafico_rutas' => [
            'enabled' => true,
            'sort' => 2,
            'span' => 2,
        ],
        'rendimiento_algoritmo' => [
            'enabled' => true,
            'sort' => 3,
            'span' => 2,
        ],
        'tabla_clientes' => [
            'enabled' => false,
            'sort' => 4,
            'span' => 'full',
        ],
        'grafico_costos' => [
            'enabled' => true,
            'sort' => 5,
            'span' => 1,
        ],
        'info_sistema' => [
            'enabled' => true,
            'sort' => 6,
            'span' => 'full',
        ],
    ],

    'algorithms' => [
        'hybrid' => [
            'name' => 'Algoritmo Híbrido',
            'description' => 'Simulated Annealing + Búsqueda Tabú',
            'enabled' => true,
        ],
        'simulated_annealing' => [
            'name' => 'Simulated Annealing',
            'description' => 'Optimización por recocido simulado',
            'enabled' => true,
        ],
        'tabu_search' => [
            'name' => 'Búsqueda Tabú',
            'description' => 'Búsqueda con memoria tabú',
            'enabled' => true,
        ],
        'ant_colony' => [
            'name' => 'Optimización por Colonia de Hormigas',
            'description' => 'ACO para problemas de ruteo',
            'enabled' => false,
        ],
    ],

    'features' => [
        'real_time_optimization' => 'Optimización de rutas en tiempo real',
        'demand_prediction' => 'Análisis predictivo de demanda',
        'inventory_management' => 'Gestión automática de inventarios',
        'performance_reports' => 'Reportes avanzados de rendimiento',
        'gps_integration' => 'Integración con sistemas GPS',
    ],

    'system' => [
        'version' => '2.1.4',
        'last_maintenance' => '2024-06-20',
        'next_update' => '2024-07-15',
        'server_status' => 'Online',
        'memory_usage' => '67%',
        'cpu_usage' => '42%',
    ],

    'chart_colors' => [
        'primary' => '#36A2EB',
        'secondary' => '#FF6384',
        'success' => '#4BC0C0',
        'warning' => '#FFCE56',
        'danger' => '#FF9F40',
        'info' => '#9966FF',
    ],

    'layout' => [
        'columns' => [
            'sm' => 1,
            'md' => 2,
            'lg' => 3,
        ],
        'responsive' => true,
    ],
];
