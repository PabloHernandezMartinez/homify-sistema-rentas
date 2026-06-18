from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from email_validator import validate_email, EmailNotValidError
import re
import bcrypt
from typing import Union, Dict, Any
from .enums import Rol_Usuario, Estado_Usuario, Genero_Usuario

TELEFONO_REGEX: re.Pattern = re.compile(r'^\d{2}-\d{4}-\d{4}$')

class Usuario:
    """
    Clase base que representa un usuario del sistema de gestión de rentas HOMIFY.

    Atributos:
        id_usuario (str): Identificador único del usuario.
        nombre (str): Nombre(s) del usuario.
        apellido (str): Apellido(s) del usuario.
        fecha_nacimiento (date): Fecha de nacimiento (mayor de edad).
        genero (Genero): Género del usuario.
        email (str): Correo electrónico normalizado.
        telefono (str): Número telefónico con formato XX-XXXX-XXXX.
        password (str): Hash de la contraseña (bcrypt).
        fecha_registro (datetime): Momento de creación de la cuenta.
        estado (Estado): Estado actual de la cuenta.
        rol (Rol): Rol del usuario en el sistema.

    Nota:
        La contraseña no puede leerse directamente; se debe usar el setter
        para asignar una nueva o `_establecer_password_hash` para cargar
        un hash ya existente.
    """

    def __init__(self,
                    id_usuario: str,
                    nombre: str,
                    apellido: str,
                    fecha_nacimiento: Union[str, datetime, date],
                    genero: Union[str, Genero_Usuario],
                    email: str,
                    telefono: str,
                    password: str,
                    fecha_registro: datetime,
                    estado: Union[str, Estado_Usuario],
                    rol: Union[str, Rol_Usuario],
                    es_hash: bool = False) -> None:
        self.__id_usuario = str(id_usuario)
        self.nombre = nombre
        self.apellido = apellido
        self.fecha_nacimiento = fecha_nacimiento
        self.genero = genero
        self.email = email
        self.telefono = telefono
        if es_hash:
            self._establecer_password_hash(password)
        else:
            self.password = password
        self.__fecha_registro = self._validar_fecha_registro(fecha_registro)
        self.estado = estado
        self.__rol = Rol_Usuario(rol) if not isinstance(rol, Rol_Usuario) else rol

    @property
    def id_usuario(self) -> str:
        """Identificador único del usuario."""
        return self.__id_usuario

    @property
    def nombre(self) -> str:
        """Nombre(s) del usuario, capitalizado y sin espacios extra."""
        return self.__nombre

    @property
    def apellido(self) -> str:
        """Apellido(s) del usuario, capitalizado y sin espacios extra."""
        return self.__apellido

    @property
    def fecha_nacimiento(self) -> date:
        """Fecha de nacimiento del usuario."""
        return self.__fecha_nacimiento

    @property
    def genero(self) -> Genero_Usuario:
        """Género del usuario."""
        return self.__genero

    @property
    def email(self) -> str:
        """Correo electrónico normalizado."""
        return self.__email

    @property
    def telefono(self) -> str:
        """Número de teléfono (formato XX-XXXX-XXXX)."""
        return self.__telefono

    @property
    def password(self) -> None:
        """
        Impide la lectura directa de la contraseña.
        Use `verificar_password()` para comparar.
        """
        raise AttributeError("El password no puede leerse directamente")

    @property
    def fecha_registro(self) -> datetime:
        """Fecha y hora en que se registró el usuario."""
        return self.__fecha_registro

    @property
    def estado(self) -> Estado_Usuario:
        """Estado actual de la cuenta."""
        return self.__estado

    @property
    def rol(self) -> Rol_Usuario:
        """Rol asignado al usuario."""
        return self.__rol

    @property
    def es_admin(self) -> bool:
        """Verdadero si el rol es administrador."""
        return self.__rol == Rol_Usuario.ADMIN

    @property
    def es_cliente(self) -> bool:
        """Verdadero si el rol es cliente."""
        return self.__rol == Rol_Usuario.CLIENTE

    @property
    def es_arrendador(self) -> bool:
        """Verdadero si el rol es arrendador."""
        return self.__rol == Rol_Usuario.ARRENDADOR

    @property
    def esta_activo(self) -> bool:
        """Verdadero si el estado es 'activo'."""
        return self.__estado == Estado_Usuario.ACTIVO

    @property
    def esta_suspendido(self) -> bool:
        """Verdadero si el estado es 'suspendido'."""
        return self.__estado == Estado_Usuario.SUSPENDIDO

    @property
    def esta_eliminado(self) -> bool:
        """Verdadero si el estado es 'eliminado'."""
        return self.__estado == Estado_Usuario.ELIMINADO

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """
        Establece el nombre después de validar y limpiar.

        Lanza ValueError si está vacío, contiene caracteres no permitidos
        o excede los 30 caracteres.
        """
        if not valor or not isinstance(valor, str):
            raise ValueError("El nombre no puede estar vacío.")
        if not re.match(r'^[A-Za-zÁáÉéÍíÓóÚúÜüÑñ\s]+$', valor):
            raise ValueError("El nombre solo puede contener letras y espacios.")
        if len(valor) > 30:
            raise ValueError("El nombre no puede superar los 30 caracteres.")
        self.__nombre = valor.strip().title()

    @apellido.setter
    def apellido(self, valor: str) -> None:
        """
        Establece el apellido después de validar y limpiar.

        Lanza ValueError si está vacío, contiene caracteres no permitidos
        o excede los 30 caracteres.
        """
        if not valor or not isinstance(valor, str):
            raise ValueError("El apellido no puede estar vacío.")
        if not re.match(r'^[A-Za-zÁáÉéÍíÓóÚúÜüÑñ\s]+$', valor):
            raise ValueError("El apellido solo puede contener letras y espacios.")
        if len(valor) > 30:
            raise ValueError("El apellido no puede superar los 30 caracteres.")
        self.__apellido = valor.strip().title()

    @fecha_nacimiento.setter
    def fecha_nacimiento(self, valor: Union[str, datetime, date]) -> None:
        """
        Convierte y valida la fecha de nacimiento.

        - Si es str, debe tener formato 'YYYY-MM-DD'.
        - Debe ser anterior a hoy.
        - El usuario debe ser mayor de 18 años.
        """
        if isinstance(valor, str):
            fecha = datetime.strptime(valor, "%Y-%m-%d").date()
        elif isinstance(valor, datetime):
            fecha = valor.date()
        else:
            fecha = valor

        if fecha >= date.today():
            raise ValueError("La fecha de nacimiento debe ser anterior a hoy.")
        if date.today() < fecha + relativedelta(years=18):
            raise ValueError("Debes ser mayor de edad.")
        self.__fecha_nacimiento = fecha

    @genero.setter
    def genero(self, nuevo_genero: Union[str, Genero_Usuario]) -> None:
        """
        Asigna el género aceptando tanto el string como el Enum Genero.
        """
        if isinstance(nuevo_genero, Genero_Usuario):
            self.__genero = nuevo_genero
        elif isinstance(nuevo_genero, str):
            self.__genero = Genero_Usuario(nuevo_genero)
        else:
            raise ValueError("Género no válido. Debe ser 'masculino', 'femenino' o 'otro'.")

    @email.setter
    def email(self, valor: str) -> None:
        """
        Valida y normaliza el correo electrónico.

        Lanza ValueError si el formato o dominio son inválidos.
        """
        try:
            info_correo = validate_email(valor, check_deliverability=False)
            self.__email = info_correo.normalized
        except EmailNotValidError as e:
            raise ValueError(f"El correo o su dominio no son válidos. Motivo: {e}")

    @telefono.setter
    def telefono(self, valor: str) -> None:
        """
        Valida el número de teléfono contra el formato XX-XXXX-XXXX.
        """
        if not isinstance(valor, str) or not TELEFONO_REGEX.match(valor):
            raise ValueError("Teléfono inválido. Debe contener 10 digitos (formato XX-XXXX-XXXX).")
        self.__telefono = valor

    @password.setter
    def password(self, nuevo_password: str) -> None:
        """
        Aplica reglas de complejidad y almacena el hash bcrypt.

        Requiere mínimo 8 caracteres, una mayúscula, una minúscula,
        un número y un carácter especial.
        """
        if not isinstance(nuevo_password, str):
            raise TypeError("El password debe ser una cadena de texto (string).")
        if len(nuevo_password) < 8:
            raise ValueError("El password debe tener al menos 8 caracteres.")
        if not re.search(r"[A-Z]", nuevo_password):
            raise ValueError("El password debe contener al menos una letra mayúscula.")
        if not re.search(r"[a-z]", nuevo_password):
            raise ValueError("El password debe contener al menos una letra minúscula.")
        if not re.search(r"[0-9]", nuevo_password):
            raise ValueError("El password debe contener al menos un número.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", nuevo_password):
            raise ValueError("El password debe contener al menos un carácter especial (ej: !@#$).")
        self.__password = bcrypt.hashpw(nuevo_password.encode(), bcrypt.gensalt()).decode()

    @estado.setter
    def estado(self, nuevo_estado: Union[str, Estado_Usuario]) -> None:
        """
        Cambia el estado de la cuenta aceptando string o Enum Estado.
        """
        if isinstance(nuevo_estado, Estado_Usuario):
            self.__estado = nuevo_estado
        elif isinstance(nuevo_estado, str):
            self.__estado = Estado_Usuario(nuevo_estado)
        else:
            raise ValueError("Estado no válido. Debe ser 'activo', 'suspendido' o 'eliminado'.")
        
    @staticmethod
    def _validar_fecha_registro(valor: datetime) -> datetime:
        """
        Valida que la fecha de registro no sea futura.
        Retorna el mismo objeto datetime si es válido.
        """
        if not isinstance(valor, datetime):
            raise TypeError("La fecha de registro debe ser un objeto datetime.")
        if valor > datetime.now():
            raise ValueError("La fecha de registro no puede ser futura.")
        return valor

    def _establecer_password_hash(self, hash_almacenado: str) -> None:
        """
        Carga directamente un hash de contraseña (ej. desde la BD) sin validar.
        """
        if not isinstance(hash_almacenado, str):
            raise ValueError("El hash debe ser una cadena.")
        self.__password = hash_almacenado

    def verificar_password(self, password_plano: str) -> bool:
        """
        Compara una contraseña en texto plano con el hash almacenado.
        """
        return bcrypt.checkpw(password_plano.encode(), self.__password.encode())

    def cambiar_password(self,
                            actual_password: str,
                            nuevo_password: str,
                            confirmacion: str) -> bool:
        """
        Cambia la contraseña verificando la actual y la coincidencia de la nueva.

        Retorna True si se cambió exitosamente.
        """
        if not self.verificar_password(actual_password):
            raise ValueError("La contraseña actual es incorrecta.")
        if nuevo_password != confirmacion:
            raise ValueError("La nueva contraseña y la confirmación no coinciden.")
        self.password = nuevo_password
        return True
    
    def _obtener_password_hash(self) -> str:
        """
        Devuelve el hash de la contraseña almacenado.
        """
        return self.__password

    def actualizar_perfil(self,
                            nuevo_nombre: str,
                            nuevo_apellido: str,
                            nuevo_fecha_nacimiento: Union[str, datetime, date],
                            nuevo_genero: Union[str, Genero_Usuario],
                            nuevo_email: str,
                            nuevo_telefono: str) -> bool:
        """
        Actualiza múltiples campos del perfil de forma atómica.

        Si alguna validación falla, se revierten todos los cambios realizados.
        Retorna True cuando la actualización es exitosa.
        """
        respaldo: Dict[str, Any] = {
            'nombre': self.__nombre,
            'apellido': self.__apellido,
            'fecha_nacimiento': self.__fecha_nacimiento,
            'genero': self.__genero,
            'email': self.__email,
            'telefono': self.__telefono,
        }
        try:
            self.nombre = nuevo_nombre
            self.apellido = nuevo_apellido
            self.fecha_nacimiento = nuevo_fecha_nacimiento
            self.genero = nuevo_genero
            self.email = nuevo_email
            self.telefono = nuevo_telefono
        except Exception:
            self.__nombre = respaldo['nombre']
            self.__apellido = respaldo['apellido']
            self.__fecha_nacimiento = respaldo['fecha_nacimiento']
            self.__genero = respaldo['genero']
            self.__email = respaldo['email']
            self.__telefono = respaldo['telefono']
            raise
        return True

    def obtener_datos_perfil(self) -> Dict[str, str]:
        """
        Devuelve un diccionario con los datos públicos del perfil.
        """
        return {
            "id_usuario": self.id_usuario,
            "nombre_completo": f"{self.nombre} {self.apellido}",
            "fecha_nacimiento": str(self.fecha_nacimiento),
            "genero": self.genero.value,
            "email": self.email,
            "telefono": self.telefono,
            "estado": self.estado.value,
            "rol": self.rol.value
        }
    
    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> "Usuario":
        """
        Construye una instancia genérica de Usuario a partir de un diccionario.
        Optimizado para evitar sobreprocesamiento de bcrypt.
        """
        if "password" not in datos or not datos["password"]:
            raise ValueError("El diccionario debe contener un hash de contraseña válido.")

        return cls(
            id_usuario=datos["id_usuario"],
            nombre=datos["nombre"],
            apellido=datos["apellido"],
            fecha_nacimiento=datos["fecha_nacimiento"],
            genero=datos["genero"],
            email=datos["email"],
            telefono=datos["telefono"],
            password=datos["password"],
            fecha_registro=datos["fecha_registro"],
            estado=datos["estado"],
            rol=datos["rol"],
            es_hash=True
        )