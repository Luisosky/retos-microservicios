<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Str;

class Perfil extends Model
{
    use HasFactory;

    protected $table = 'perfiles';

    protected $primaryKey = 'id';

    public $incrementing = false;

    protected $keyType = 'string';

    public $timestamps = false;

    protected $fillable = [
        'id',
        'empleado_id',
        'nombre',
        'email',
        'telefono',
        'direccion',
        'ciudad',
        'biografia',
        'fecha_creacion',
    ];

    protected $casts = [
        'fecha_creacion' => 'datetime',
    ];

    protected static function booted(): void
    {
        static::creating(function (self $perfil): void {
            if (!$perfil->id) {
                $perfil->id = (string) Str::uuid();
            }

            if (!$perfil->fecha_creacion) {
                $perfil->fecha_creacion = now();
            }
        });
    }
}
