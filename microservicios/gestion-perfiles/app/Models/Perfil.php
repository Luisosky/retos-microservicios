<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Perfil extends Model
{
    use HasFactory, SoftDeletes;

    protected $table = 'perfiles';

    protected $fillable = [
        'empleado_id',
        'nombre',
        'email',
        'telefono',
        'direccion',
        'ciudad',
        'biografia',
        'foto_url',
        'bio',
        'departamento_id',
        'activo',
    ];

    protected $casts = [
        'activo' => 'boolean',
        'created_at' => 'datetime',
    ];

    protected $hidden = [
        'deleted_at',
    ];
}
