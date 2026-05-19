"""
Script para probar la conexión a la base de datos PostgreSQL
"""
import sys
from app.core.config import settings
from sqlalchemy import create_engine, text

def test_connection():
    """Intenta conectarse a la base de datos y reporte el resultado"""
    print("=" * 60)
    print("PRUEBA DE CONEXIÓN A LA BASE DE DATOS")
    print("=" * 60)
    
    try:
        # Mostrar datos de conexión (sin mostrar contraseña completa)
        print(f"\n📍 Host: {settings.db_host}")
        print(f"📍 Puerto: {settings.db_port}")
        print(f"📍 Base de datos: {settings.db_name}")
        print(f"📍 Usuario: {settings.db_user}")
        print(f"\n🔗 URL de conexión: postgresql+psycopg2://{settings.db_user}:****@{settings.db_host}:{settings.db_port}/{settings.db_name}")
        
        print(f"\n⏳ Intentando conectar...")
        
        # Crear motor de base de datos
        engine = create_engine(settings.sqlalchemy_database_uri, pool_pre_ping=True, echo=False)
        
        # Probar conexión
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ ¡CONEXIÓN EXITOSA!")
            
            # Intentar consultar las tablas
            print(f"\n📋 Consultando tablas...")
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables_result = connection.execute(tables_query)
            tables = tables_result.fetchall()
            
            if tables:
                print(f"✅ Tablas encontradas:")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("⚠️  No hay tablas en la base de datos")
            
            # Verificar si existe la tabla Departamentos
            print(f"\n🔍 Verificando tabla 'Departamentos'...")
            check_table = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'Departamentos'
                )
            """)
            check_result = connection.execute(check_table)
            table_exists = check_result.scalar()
            
            if table_exists:
                print("✅ Tabla 'Departamentos' existe")
                
                # Contar registros
                count_query = text("SELECT COUNT(*) FROM \"Departamentos\"")
                count_result = connection.execute(count_query)
                count = count_result.scalar()
                print(f"   Registros en la tabla: {count}")
            else:
                print("⚠️  Tabla 'Departamentos' NO existe (puedes crearla desde el código)")
        
        print("\n" + "=" * 60)
        print("✅ PRUEBA COMPLETADA CON ÉXITO")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR DE CONEXIÓN:")
        print(f"   {type(e).__name__}: {str(e)}")
        print("\n" + "=" * 60)
        print("❌ PRUEBA FALLIDA")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
