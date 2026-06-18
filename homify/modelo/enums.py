from enum import Enum

class Tipo_Inmueble(Enum):
    """Tipos de inmuebles permitidos en el sistema."""
    CASA = "casa"
    DEPARTAMENTO = "departamento"

class Rol_Usuario(Enum):
    """Roles de usuario en el sistema."""
    ADMIN = "admin"
    CLIENTE = "cliente"
    ARRENDADOR = "arrendador"

class Estado_Usuario(Enum):
    """Estados posibles de una cuenta de usuario."""
    ACTIVO = "activo"
    SUSPENDIDO = "suspendido"
    ELIMINADO = "eliminado"

class Genero_Usuario(Enum):
    """Géneros de usuario."""
    MASCULINO = "masculino"
    FEMENINO = "femenino"
    OTRO = "otro"

class Metodo_Pago(Enum):
    """Métodos de pago aceptados en el sistema."""
    TARJETA = "tarjeta"
    TRANSFERENCIA = "transferencia"
    EFECTIVO = "efectivo"

class Estado_Renta(Enum):
    """Estados posibles de una renta."""
    ACTIVA = "activa"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"