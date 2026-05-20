<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('perfiles', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->string('empleado_id')->unique()->comment('ID del empleado en el servicio gestion-empleados');
            $table->string('nombre');
            $table->string('email')->unique();
            $table->string('telefono')->nullable();
            $table->string('direccion')->nullable();
            $table->string('ciudad')->nullable();
            $table->text('biografia')->nullable();
            $table->timestamp('fecha_creacion')->nullable();
            $table->softDeletes();

            $table->index('empleado_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('perfiles');
    }
};
