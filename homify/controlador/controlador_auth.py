import uuid
from datetime import datetime
from typing import Tuple, Union, Dict
from modelo.gestordb import GestorDB
from modelo.usuario import Usuario

class ControladorAuth:
    """
    Controlador de autenticación y registro de usuarios.
    Interactúa con el gestor de base de datos y el modelo Usuario.
    """

    def __init__(self, ruta_db: str = "datos/sistema.db") -> None:
        """Inicializa el controlador con la ruta a la base de datos."""
        self.gestor_db = GestorDB(ruta_db)

    def login(self, email: str, password: str) -> Tuple[bool, Union[Dict[str, str], str]]:
        """
        Autentica a un usuario por email y contraseña.

        Args:
            email: Correo electrónico del usuario.
            password: Contraseña en texto plano.

        Returns:
            Una tupla (éxito, datos_sesion|mensaje_error).
        """
        email = email.strip()
        password = password.strip()
        if not email or not password:
            return False, "Por favor, llena todos los campos."

        datos_usuario = self.gestor_db.obtener_usuario_por_email(email)
        if not datos_usuario:
            return False, "El correo electrónico no está registrado."

        usuario = Usuario.from_dict(datos_usuario)

        if not usuario.esta_activo:
            return False, f"Tu cuenta no está disponible. Estado actual: {usuario.estado.value}."

        if not usuario.verificar_password(password):
            return False, "Contraseña incorrecta."

        datos_sesion = usuario.obtener_datos_perfil()
        return True, datos_sesion

    def registrar(
        self,
        nombre: str,
        apellido: str,
        email: str,
        telefono: str,
        password: str,
        confirmar_password: str,
        genero: str,
        fecha_nacimiento: str,
        rol: str = "cliente"
    ) -> Tuple[bool, str]:
        """
        Registra un nuevo usuario en el sistema.

        Args:
            nombre: Nombre(s) del usuario.
            apellido: Apellido(s).
            email: Correo electrónico.
            telefono: Teléfono (formato libre).
            password: Contraseña en texto plano.
            confirmar_password: Confirmación de la contraseña.
            genero: Género ('masculino', 'femenino', 'otro').
            fecha_nacimiento: Fecha de nacimiento (YYYY-MM-DD).
            rol: Rol del usuario ('cliente', 'arrendador', 'admin').

        Returns:
            Tupla (éxito, mensaje).
        """
        nombre = nombre.strip()
        apellido = apellido.strip()
        email = email.strip().lower()
        telefono = telefono.strip()
        password = password.strip()
        confirmar_password = confirmar_password.strip()

        if rol not in ("cliente", "arrendador"):
            return False, "Rol no válido para registro público."
        if not (nombre and email and password and confirmar_password):
            return False, "Los campos Nombre, Email, Contraseña y Confirmación son obligatorios."
        if password != confirmar_password:
            return False, "Las contraseñas no coinciden."
        if not fecha_nacimiento:
            return False, "La fecha de nacimiento es obligatoria."
        if not genero:
            return False, "El género es obligatorio."

        if self.gestor_db.obtener_usuario_por_email(email):
            return False, "Este correo electrónico ya está registrado."

        prefijo = {"cliente": "CLI", "arrendador": "ARR", "admin": "ADM"}.get(rol, "USR")
        id_unico = f"{prefijo}-{str(uuid.uuid4())[:8].upper()}"

        try:
            nuevo_usuario = Usuario(
                id_usuario=id_unico,
                nombre=nombre,
                apellido=apellido,
                fecha_nacimiento=fecha_nacimiento,
                genero=genero,
                email=email,
                telefono=telefono if telefono else None,
                password=password,
                fecha_registro=datetime.now(),
                rol=rol,
                estado="activo",
                es_hash=False
            )
        except (ValueError, TypeError) as e:
            return False, str(e)

        password_hash = nuevo_usuario._obtener_password_hash()

        datos_db = nuevo_usuario.obtener_datos_perfil()
        datos_db["password"] = password_hash
        datos_db["fecha_registro"] = nuevo_usuario.fecha_registro.isoformat()

        exito = self.gestor_db.registrar_usuario(datos_db)
        if exito:
            return True, f"¡Registro exitoso! Tu ID de usuario es: {id_unico}"
        else:
            return False, "Hubo un error al guardar en la base de datos."