import uuid
from datetime import date, timedelta
from typing import Tuple, Union, Dict, Any, List, Optional
from modelo.gestordb import GestorDB
from modelo.usuario import Usuario
from modelo.casa import Casa
from modelo.departamento import Departamento
from modelo.renta import Renta

class ControladorCliente:
    """
    Controlador para las operaciones del cliente.
    Gestiona búsqueda de inmuebles, rentas, cancelaciones y perfil personal.
    """

    def __init__(self, ruta_db: str = "datos/sistema.db") -> None:
        """Inicializa el controlador con la ruta a la base de datos."""
        self.gestor_db = GestorDB(ruta_db)

    def buscar_inmuebles(
        self,
        pagina: int = 0,
        limite: int = 50,
        filtros: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """
        Busca inmuebles disponibles con paginación o filtros.

        Args:
            pagina: Número de página (comienza en 0).
            limite: Cantidad de resultados por página.
            filtros: Diccionario opcional con criterios de filtrado.

        Returns:
            Tupla (éxito, datos|mensaje_error). En caso de éxito, 'datos' contiene
            la lista de inmuebles y el total de registros.
        """
        offset = pagina * limite

        if filtros:
            # Mapea los nombres de filtro de la vista a los que espera el gestor
            params = {
                "direccion": filtros.get("direccion"),
                "precio_min": filtros.get("precio_min"),
                "precio_max": filtros.get("precio_max"),
                "m2_min": filtros.get("m2_min"),
                "m2_max": filtros.get("m2_max"),
                "tipo": filtros.get("tipo"),
                "recamaras": filtros.get("recamaras"),
                "banos": filtros.get("banos"),
                "estacionamientos": filtros.get("estacionamientos"),
                "antiguedad": filtros.get("antiguedad"),
                "amueblado": filtros.get("amueblado", False),
                "alberca": filtros.get("alberca", False),
                "cocina_integral": filtros.get("cocina_integral", False),
                "cuarto_servicio": filtros.get("cuarto_servicio", False),
                "seguridad": filtros.get("seguridad", False),
                "patio": filtros.get("patio", False),
                "elevador": filtros.get("elevador", False),
            }
            # Elimina parámetros nulos para no pasarlos al gestor
            params = {k: v for k, v in params.items() if v is not None}
            resultados = self.gestor_db.consultar_disponibles(**params)
            total = len(resultados)  # Nota: total aproximado, no es paginación real
        else:
            resultados = self.gestor_db.consultar_inmuebles_paginados(limite, offset)
            total = self.gestor_db.contar_inmuebles_disponibles()

        if resultados:
            return True, {"datos": resultados, "total": total}
        return False, "No se encontraron más propiedades."

    def ver_detalle_propiedad(self, id_inmueble: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """
        Obtiene el detalle completo de un inmueble.

        Args:
            id_inmueble: Identificador del inmueble.

        Returns:
            Tupla (éxito, datos|mensaje_error).
        """
        detalle = self.gestor_db.consultar_detalle_inmueble(id_inmueble)
        if detalle:
            return True, detalle
        return False, "La propiedad ya no existe o no está disponible."

    def ver_mis_rentas(
        self,
        id_cliente: str,
        ver_activas: bool = True,
        ver_finalizadas: bool = False,
        ver_canceladas: bool = False
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Obtiene las rentas del cliente según los estados solicitados.

        Args:
            id_cliente: Identificador del cliente.
            ver_activas: Incluir rentas activas.
            ver_finalizadas: Incluir rentas finalizadas.
            ver_canceladas: Incluir rentas canceladas.

        Returns:
            Tupla (éxito, lista_de_rentas).
        """
        rentas = self.gestor_db.consultar_rentas_cliente(
            id_cliente, ver_activas, ver_finalizadas, ver_canceladas
        )
        return True, rentas

    def rentar_propiedad(
        self,
        id_cliente: str,
        id_inmueble: str,
        id_arrendador: str,
        precio_mensual: float,
        metodo_pago: str,
        dias_contrato: Optional[int] = None,
        meses_contrato: Optional[int] = None,
        fecha_inicio: Optional[date] = None
    ) -> Tuple[bool, str]:
        """
        Crea una nueva renta para el cliente.

        Args:
            id_cliente: Identificador del cliente.
            id_inmueble: Identificador del inmueble.
            id_arrendador: Identificador del arrendador.
            precio_mensual: Precio mensual de renta.
            metodo_pago: Método de pago ('tarjeta', 'transferencia', 'efectivo').
            dias_contrato: Duración en días (opcional, excluyente con meses_contrato).
            meses_contrato: Duración en meses (opcional, excluyente con dias_contrato).
            fecha_inicio: Fecha de inicio de la renta (opcional, por defecto hoy).

        Returns:
            Tupla (éxito, mensaje).
        """
        if dias_contrato is None and meses_contrato is None:
            return False, "Debe especificar días o meses de renta."
        if dias_contrato is not None and meses_contrato is not None:
            return False, "Solo puede elegir días o meses, no ambos."

        inmueble_data = self.gestor_db.consultar_detalle_inmueble(id_inmueble)
        if not inmueble_data:
            return False, "La propiedad no existe."
        if not inmueble_data.get("disponible", False):
            return False, "La propiedad no está disponible."

        if fecha_inicio is None:
            fecha_inicio = date.today()
        elif fecha_inicio < date.today():
            return False, "La fecha de inicio no puede ser anterior a hoy."

        if meses_contrato is not None:
            fecha_fin = fecha_inicio + timedelta(days=30 * meses_contrato)
        else:
            fecha_fin = fecha_inicio + timedelta(days=dias_contrato)

        renta_conflictiva = self.gestor_db.obtener_renta_solapada(id_inmueble, fecha_inicio.isoformat(), fecha_fin.isoformat())
        if renta_conflictiva:
            ini = renta_conflictiva['fecha_inicio']
            fin = renta_conflictiva['fecha_fin']
            return False, f"La propiedad ya está rentada del {ini} al {fin}. Elige otras fechas."

        tipo = inmueble_data.get("tipo_inmueble", "casa")
        if tipo == "departamento":
            inmueble_obj = Departamento.from_dict(inmueble_data)
        else:
            inmueble_obj = Casa.from_dict(inmueble_data)

        total_pagar = inmueble_obj.calcular_tarifa(dias=dias_contrato, meses=meses_contrato)
        deposito = float(precio_mensual)

        id_renta = f"RNT-{str(uuid.uuid4())[:8].upper()}"
        try:
            nueva_renta = Renta(
                id_renta=id_renta,
                id_cliente=id_cliente,
                id_inmueble=id_inmueble,
                id_arrendador=id_arrendador,
                fecha_inicio=fecha_inicio.isoformat(),
                fecha_fin=fecha_fin.isoformat(),
                precio_mensual=float(precio_mensual),
                total=total_pagar,
                deposito=deposito,
                metodo_pago=metodo_pago,
            )
        except (ValueError, TypeError) as e:
            return False, f"Error al crear la renta: {e}"

        datos_renta = nueva_renta.obtener_datos_renta()
        exito_renta = self.gestor_db.registrar_renta(datos_renta)

        if exito_renta:
            return True, f"¡Felicidades! Has rentado la propiedad con éxito. Tu ID de contrato es: {id_renta}"
        return False, "Ocurrió un error al intentar generar tu contrato de renta."

    def cancelar_mi_renta(
        self,
        id_renta: str,
        id_cliente: str,
        motivo: str
    ) -> Tuple[bool, str]:
        """
        Cancela una renta activa que pertenece al cliente.

        Args:
            id_renta: Identificador de la renta.
            id_cliente: Identificador del cliente.
            motivo: Motivo de la cancelación.

        Returns:
            Tupla (éxito, mensaje).
        """
        if not motivo or not motivo.strip():
            return False, "Debes proporcionar un motivo de cancelación."

        renta_data = self.gestor_db.obtener_renta_por_id(id_renta)
        if not renta_data:
            return False, "La renta no existe."

        renta = Renta.from_dict(renta_data)
        if renta.id_cliente != id_cliente:
            return False, "No puedes cancelar una renta que no es tuya."

        try:
            renta.cancelar_renta(motivo.strip())
        except RuntimeError as e:
            return False, str(e)

        datos_actualizados = renta.obtener_datos_renta()
        exito = self.gestor_db.actualizar_estado_renta(datos_actualizados)
        if exito:
            self.gestor_db.cambiar_disponibilidad_inmueble(renta.id_inmueble, 1)
            return True, "Tu contrato ha sido cancelado y la propiedad ha sido liberada."
        return False, "No se pudo cancelar el contrato. Verifica que esté activo."

    def obtener_perfil(self, id_usuario: str) -> Tuple[bool, Union[Dict[str, str], str]]:
        """
        Obtiene los datos del perfil del usuario, excluyendo la contraseña.

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
        Actualiza los datos del perfil del cliente.

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
        return False, "Error al guardar los cambios en la base de datos"

    def cambiar_password(
        self,
        id_usuario: str,
        actual: str,
        nueva: str,
        confirmar: str
    ) -> Tuple[bool, str]:
        """
        Cambia la contraseña del usuario tras verificar la actual.

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
        return False, "Error al actualizar la contraseña en la base de datos"
    
    def eliminar_mi_cuenta(self, id_usuario: str) -> Tuple[bool, str]:
        """
        Autoelimina la cuenta del cliente, liberando su email.
        No se permite si tiene rentas activas.

        Args:
            id_usuario: Identificador del usuario.

        Returns:
            Tupla (éxito, mensaje).
        """
        rentas = self.gestor_db.consultar_rentas_cliente(id_usuario, ver_activas=True)
        if rentas:
            return False, "No puedes eliminar tu cuenta porque tienes rentas activas."
        exito = self.gestor_db.autoeliminar_usuario(id_usuario)
        if exito:
            return True, "Tu cuenta ha sido eliminada. Ya no podrás acceder."
        return False, "No se pudo eliminar la cuenta."