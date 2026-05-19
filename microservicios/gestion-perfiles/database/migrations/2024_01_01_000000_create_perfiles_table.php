<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('perfiles', function (Blueprint $table) {
            $table->id();
            $table->string('empleado_id')->unique()->comment('ID del empleado en el servicio gestion-empleados');
            $table->string('nombre');
            $table->string('email')->unique();
            $table->string('foto_url')->nullable();
            $table->text('bio')->nullable();
            $table->string('departamento_id')->nullable()->comment('ID del departamento asociado');
            $table->boolean('activo')->default(true);
            $table->timestamps();
            $table->softDeletes();

            $table->index('empleado_id');
            $table->index('departamento_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('perfiles');
    }
};
