from app.database.db_manager import DatabaseManager

DB_PATH = "fichaje.db"

def get_db():
    """Dependencia para obtener la instancia de la base de datos"""
    db = DatabaseManager(DB_PATH)
    try:
        yield db
    finally:
        # En una implementación más compleja aquí se cerraría la conexión
        pass
