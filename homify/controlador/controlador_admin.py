from typing import Tuple, Union, Dict, Any, List, Optional
from modelo.gestordb import GestorDB
from modelo.usuario import Usuario
from modelo.enums import Estado_Usuario
from modelo.renta import Renta

class ControladorAdmin:
    """
    Controlador para las operaciones del administrador.
    Permite gestionar usuarios, auditar inmuebles y administrar el sistema.
    """

    def __init__(self, ruta_db: str = "datos/sistema.db") -> None:
        """Inicializa el controlador con la ruta a la base de datos."""
        self.gestor_db = GestorDB(ruta_db)

    def obtener_usuarios(
        self,
        buscar_id: Optional[str] = None,
        ver_activos: bool = True,
        ver_suspendidos: bool = False,
        ver_eliminados: bool = False,
        rol: Optional[str] = None
    ) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        Obtiene la lista de usuarios según los filtros aplicados.

        Args:
            buscar_id: ID específico a buscar (opcional).
            ver_activos: Incluir usuarios activos.
            ver_suspendidos: Incluir usuarios suspendidos.
            ver_eliminados: Incluir usuarios eliminados.
            rol: Filtrar por rol (opcional).

        Returns:
            Tupla (éxito, lista_de_usuarios|mensaje_error).
        """
        usuarios = self.gestor_db.consultar_usuarios_admin(
            buscar_id=buscar_id,
            ver_activos=ver_activos,
            ver_suspendidos=ver_suspendidos,
            ver_eliminados=ver_eliminados,
            rol=rol
        )
        if usuarios:
            return True, usuarios
        return False, "No se encontraron usuarios con los filtros aplicados."

    def cambiar_estado_usuario(
        self,
        id_usuario_objetivo: str,
        id_admin_actual: str,
        nuevo_estado: str
    ) -> Tuple[bool, str]:
        """
        Cambia el estado de un usuario (suspender, activar, eliminar).

        Args:
            id_usuario_objetivo: ID del usuario a modificar.
            id_admin_actual: ID del administrador que realiza la acción.
            nuevo_estado: Nuevo estado ('activo', 'suspendido', 'eliminado').

        Returns:
            Tupla (éxito, mensaje).
        """
        if id_usuario_objetivo == id_admin_actual:
            return False, "Operación denegada: no puedes cambiar tu propio estado."

        try:
            Estado_Usuario(nuevo_estado)
        except ValueError:
            estados_validos = [e.value for e in Estado_Usuario]
            return False, f"Estado no válido. Debe ser uno de: {', '.join(estados_validos)}"

        datos = self.gestor_db.obtener_usuario_por_id(id_usuario_objetivo)
        if not datos:
            return False, "El usuario objetivo no existe."

        usuario_obj = Usuario.from_dict(datos)
        try:
            usuario_obj.estado = nuevo_estado
        except ValueError as e:
            return False, str(e)

        exito = self.gestor_db.actualizar_estado_usuario(id_usuario_objetivo, nuevo_estado)
        if exito:
            return True, f"El usuario {id_usuario_objetivo} ahora está {nuevo_estado}."
        return False, "No se pudo actualizar el estado en la base de datos."

    def auditar_inmuebles(
        self,
        buscar_id: Optional[str] = None,
        tipo_inmueble: Optional[str] = None,
        id_arrendador: Optional[str] = None,
        esta_disponible: Optional[bool] = None
    ) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        Obtiene todos los inmuebles (catálogo completo) o uno específico,
        con filtro opcional por tipo de inmueble, arrendador o disponibilidad.

        Args:
            buscar_id: ID del inmueble a buscar (opcional).
            tipo_inmueble: Filtrar por tipo ('casa', 'departamento', o None para todos).
            id_arrendador: ID del arrendador a buscar (opcional).
            esta_disponible: Filtrar por disponibilidad ('disponible', 'rentado', o None para todos).

        Returns:
            Tupla (éxito, lista_de_inmuebles|mensaje_error).
        """
        inmuebles = self.gestor_db.consultar_inmuebles_admin(
            buscar_id=buscar_id,
            tipo_inmueble=tipo_inmueble,
            id_arrendador=id_arrendador,
            esta_disponible=esta_disponible
        )
        if inmuebles:
            return True, inmuebles
        return False, "No se encontraron inmuebles con los criterios indicados."

    def obtener_perfil(self, id_usuario: str) -> Tuple[bool, Union[Dict[str, str], str]]:
        """
        Obtiene los datos del perfil del administrador, excluyendo la contraseña.

        Args:
            id_usuario: Identificador del usuario.

        Returns:
            Tupla (éxito, datos_perfil|mensaje_error).
        """
        datos = self.gestor_db.obtener_usuario_por_id(id_usuario)
        if not datos:
            return False, "Usuario no encontrado"
        usuario = Usuario.from_dict(datos)
        return True, usuario.obtener_datos_perfil()

    def actualizar_perfil(
        self,
        id_usuario: str,
        nombre: str,
        apellido: str,
        fecha_nacimiento: str,
        genero: str,
        email: str,
        telefono: str
    ) -> Tuple[bool, str]:
        """
        Actualiza los datos del perfil del administrador.

        Args:
            id_usuario: Identificador del usuario.
            nombre: Nuevo nombre.
            apellido: Nuevo apellido.
            fecha_nacimiento: Fecha de nacimiento (YYYY-MM-DD).
            genero: Género ('masculino', 'femenino', 'otro').
            email: Correo electrónico.
            telefono: Teléfono.

        Returns:
            Tupla (éxito, mensaje).
        """
        datos = self.gestor_db.obtener_usuario_por_id(id_usuario)
        if not datos:
            return False, "Usuario no encontrado"
        usuario = Usuario.from_dict(datos)
        try:
            usuario.actualizar_perfil(nombre, apellido, fecha_nacimiento, genero, email, telefono)
        except (ValueError, TypeError) as e:
            return False, str(e)
        exito = self.gestor_db.actualizar_perfil_usuario(
            id_usuario, usuario.nombre, usuario.apellido,
            usuario.fecha_nacimiento.isoformat(), usuario.genero.value,
            usuario.email, usuario.telefono
        )
        if exito:
            return True, "Perfil actualizado correctamente"
        return False, "Error al guardar los cambios"

    def cambiar_password(
        self,
        id_usuario: str,
        actual: str,
        nueva: str,
        confirmar: str
    ) -> Tuple[bool, str]:
        """
        Cambia la contraseña del administrador tras verificar la actual.

        Args:
            id_usuario: Identificador del usuario.
            actual: Contraseña actual.
            nueva: Nueva contraseña.
            confirmar: Confirmación de la nueva contraseña.

        Returns:
            Tupla (éxito, mensaje).
        """
        datos = self.gestor_db.obtener_usuario_por_id(id_usuario)
        if not datos:
            return False, "Usuario no existe"
        usuario = Usuario.from_dict(datos)
        try:
            usuario.cambiar_password(actual, nueva, confirmar)
        except ValueError as e:
            return False, str(e)
        nuevo_hash = usuario._obtener_password_hash()
        exito = self.gestor_db.actualizar_password_usuario(id_usuario, nuevo_hash)
        if exito:
            return True, "Contraseña actualizada correctamente"
        return False, "Error al actualizar la contraseña"

    def cancelar_renta(self, id_renta: str, motivo: str) -> Tuple[bool, str]:
        """
        Cancela forzosamente una renta activa y libera el inmueble.

        Args:
            id_renta: Identificador de la renta.
            motivo: Motivo de la cancelación.

        Returns:
            Tupla (éxito, mensaje).
        """
        if not motivo or not motivo.strip():
            return False, "Debe proporcionar un motivo para la cancelación."

        renta_data = self.gestor_db.obtener_renta_por_id(id_renta)
        if not renta_data:
            return False, "La renta no existe."

        renta = Renta.from_dict(renta_data)
        try:
            renta.cancelar_renta(motivo.strip())
        except RuntimeError as e:
            return False, str(e)

        datos_actualizados = renta.obtener_datos_renta()
        exito = self.gestor_db.actualizar_estado_renta(datos_actualizados)
        if exito:
            self.gestor_db.cambiar_disponibilidad_inmueble(renta.id_inmueble, 1)
            return True, f"Contrato {id_renta} cancelado y propiedad liberada."
        return False, "No se pudo cancelar el contrato. Verifique que esté activo."
    
    def finalizar_renta(self, id_renta: str, fecha_fin_real: str) -> Tuple[bool, str]:
        """
        Finaliza forzosamente una renta activa y libera el inmueble.

        Args:
            id_renta: Identificador de la renta.
            fecha_fin_real: Fecha real de finalización (YYYY-MM-DD).

        Returns:
            Tupla (éxito, mensaje).
        """
        renta_data = self.gestor_db.obtener_renta_por_id(id_renta)
        if not renta_data:
            return False, "La renta no existe."

        renta = Renta.from_dict(renta_data)
        try:
            renta.finalizar_renta(fecha_fin_real)
        except (RuntimeError, ValueError) as e:
            return False, str(e)

        datos_actualizados = renta.obtener_datos_renta()
        exito = self.gestor_db.actualizar_estado_renta(datos_actualizados)
        if exito:
            self.gestor_db.cambiar_disponibilidad_inmueble(renta.id_inmueble, 1)
            return True, f"Contrato {id_renta} finalizado y propiedad liberada."
        return False, "No se pudo finalizar el contrato."

    def cambiar_disponibilidad_inmueble(self, id_inmueble: str, disponible: bool) -> Tuple[bool, str]:
        """
        Activa o desactiva un inmueble (lo publica o lo retira del mercado).

        Args:
            id_inmueble: Identificador del inmueble.
            disponible: True para marcarlo como disponible, False para no disponible.

        Returns:
            Tupla (éxito, mensaje).
        """
        self.gestor_db.cambiar_disponibilidad_inmueble(id_inmueble, disponible)
        estado_str = "disponible" if disponible else "no disponible"
        return True, f"Inmueble {id_inmueble} ahora está {estado_str}."

    def actualizar_precio_inmueble(self, id_inmueble: str, nuevo_precio: float) -> Tuple[bool, str]:
        """
        Actualiza el precio de renta de un inmueble.

        Args:
            id_inmueble: Identificador del inmueble.
            nuevo_precio: Nuevo precio mensual.

        Returns:
            Tupla (éxito, mensaje).
        """
        if nuevo_precio <= 0:
            return False, "El precio debe ser mayor a cero."
        exito = self.gestor_db.actualizar_precio_inmueble(id_inmueble, nuevo_precio)
        if exito:
            return True, f"Precio del inmueble {id_inmueble} actualizado."
        return False, "No se pudo actualizar el precio."
    
    def obtener_todas_las_rentas(self, id_cliente: Optional[str] =None, 
                                    id_arrendador: Optional[str] =None, 
                                    estado: Optional[str] =None
                                    ) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
        """
        Obtiene todas las rentas del sistema con información extendida.
        Permite filtrar opcionalmente por id de cliente, id de arrendador y estado.

        Args:
            id_cliente: Identificador del cliente (opcional).
            id_arrendador: Identificador del arrendador (opcional).
            estado: Estado de la renta ('activa', 'finalizada', 'cancelada') (opcional).

        Returns:
            Tupla (éxito, lista_de_rentas|mensaje_error).
        """
        rentas = self.gestor_db.consultar_rentas_globales(id_cliente, id_arrendador, estado)
        if rentas:
            return True, rentas
        return False, "El sistema aún no tiene contratos de renta registrados."

    def exportar_inmuebles_csv(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los inmuebles y los devuelve en formato adecuado para exportar como CSV.

        Returns:
            Lista de diccionarios, cada uno con los campos requeridos para el CSV.
        """
        inmuebles = self.gestor_db.consultar_inmuebles_admin()
        datos_export: List[Dict[str, Any]] = []
        for inm in inmuebles:
            tipo = inm.get("tipo_inmueble", "casa")
            es_departamento = 1 if tipo == "departamento" else 0
            fila = {
                "precio": inm.get("precio_renta", 0),
                "m2_terreno": inm.get("m2_terreno", 0),
                "m2_construido": inm.get("m2_construccion", 0),
                "banos": inm.get("banos", 0),
                "medios_banos": inm.get("medios_banos", 0),
                "estacionamientos": inm.get("estacionamientos", 0),
                "antiguedad": inm.get("antiguedad", 0),
                "amen_Alberca": inm.get("alberca", 0),
                "amen_Cocina integral": inm.get("cocina_integral", 0),
                "amen_Amueblado": inm.get("amueblado", 0),
                "amen_Elevador": inm.get("elevador", 0),
                "amen_Cuartos de servicio": inm.get("cuarto_servicio", 0),
                "tipo_propiedad_departamento": es_departamento,
                "tipo_propiedad_original": tipo,
                "direccion": inm.get("direccion", "").lower()
            }
            datos_export.append(fila)
        return datos_export