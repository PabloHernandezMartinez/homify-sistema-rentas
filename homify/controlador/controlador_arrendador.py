import uuid
from datetime import datetime, date
from typing import Tuple, Union, Dict, Any, List, Optional
from modelo.gestordb import GestorDB
from modelo.usuario import Usuario
from modelo.casa import Casa
from modelo.departamento import Departamento
from modelo.renta import Renta
from collections import defaultdict

class ControladorArrendador:
    """
    Controlador para las operaciones del arrendador.
    Permite gestionar propiedades, consultar rentas, ver dashboard de ganancias y actualizar su perfil.
    """

    def __init__(self, ruta_db: str = "datos/sistema.db") -> None:
        """Inicializa el controlador con la ruta a la base de datos."""
        self.gestor_db = GestorDB(ruta_db)

    def obtener_propiedades(self, id_arrendador: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Obtiene todos los inmuebles asociados a un arrendador.

        Args:
            id_arrendador: Identificador del arrendador.

        Returns:
            Tupla (éxito, lista_de_inmuebles).
        """
        inmuebles = self.gestor_db.consultar_inmuebles_arrendador(id_arrendador)
        return True, inmuebles

    def registrar_propiedad(self, datos_formulario: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Registra una nueva propiedad (casa o departamento) a partir de los datos del formulario.

        Args:
            datos_formulario: Diccionario con los campos del inmueble.
                Campos requeridos: titulo, direccion, precio, tipo, id_arrendador.

        Returns:
            Tupla (éxito, mensaje).
        """
        campos_requeridos = ["titulo", "direccion", "precio", "tipo", "id_arrendador"]
        for campo in campos_requeridos:
            if campo not in datos_formulario or not str(datos_formulario[campo]).strip():
                return False, f"El campo '{campo.capitalize()}' es obligatorio."

        tipo = datos_formulario["tipo"]
        if tipo not in ("casa", "departamento"):
            return False, "Tipo de inmueble no válido."

        id_inmueble = f"INM-{str(uuid.uuid4())[:8].upper()}"

        try:
            if tipo == "casa":
                inmueble = Casa(
                    id_inmueble=id_inmueble,
                    id_arrendador=datos_formulario["id_arrendador"],
                    titulo=datos_formulario["titulo"],
                    descripcion=datos_formulario.get("descripcion", ""),
                    direccion=datos_formulario["direccion"],
                    precio_renta=float(datos_formulario["precio"]),
                    m2_terreno=int(datos_formulario.get("m2_terreno", 0)),
                    m2_construccion=int(datos_formulario.get("m2_construccion", 0)),
                    recamaras=int(datos_formulario.get("recamaras", 0)),
                    banos=int(datos_formulario.get("banos", 0)),
                    medios_banos=int(datos_formulario.get("medios_banos", 0)),
                    estacionamientos=int(datos_formulario.get("estacionamientos", 0)),
                    antiguedad=int(datos_formulario.get("antiguedad", 0)),
                    alberca=bool(datos_formulario.get("alberca", False)),
                    amueblado=bool(datos_formulario.get("amueblado", False)),
                    cocina_integral=bool(datos_formulario.get("cocina_integral", False)),
                    cuarto_servicio=bool(datos_formulario.get("cuarto_servicio", False)),
                    seguridad=bool(datos_formulario.get("seguridad", False)),
                    patio=bool(datos_formulario.get("patio", False)),
                    fecha_publicacion=date.today(),
                    tipo_inmueble="casa",
                    disponible=True
                )
            else:
                inmueble = Departamento(
                    id_inmueble=id_inmueble,
                    id_arrendador=datos_formulario["id_arrendador"],
                    titulo=datos_formulario["titulo"],
                    descripcion=datos_formulario.get("descripcion", ""),
                    direccion=datos_formulario["direccion"],
                    precio_renta=float(datos_formulario["precio"]),
                    m2_construccion=int(datos_formulario.get("m2_construccion", 0)),
                    recamaras=int(datos_formulario.get("recamaras", 0)),
                    banos=int(datos_formulario.get("banos", 0)),
                    medios_banos=int(datos_formulario.get("medios_banos", 0)),
                    estacionamientos=int(datos_formulario.get("estacionamientos", 0)),
                    antiguedad=int(datos_formulario.get("antiguedad", 0)),
                    alberca=bool(datos_formulario.get("alberca", False)),
                    amueblado=bool(datos_formulario.get("amueblado", False)),
                    cocina_integral=bool(datos_formulario.get("cocina_integral", False)),
                    cuarto_servicio=bool(datos_formulario.get("cuarto_servicio", False)),
                    seguridad=bool(datos_formulario.get("seguridad", False)),
                    elevador=bool(datos_formulario.get("elevador", False)),
                    fecha_publicacion=date.today(),
                    tipo_inmueble="departamento",
                    disponible=True
                )
        except (ValueError, TypeError) as e:
            return False, f"Error en los datos: {e}"

        datos_bd = inmueble.obtener_datos_inmueble()
        datos_bd["esta_disponible"] = int(datos_bd.pop("disponible"))

        if tipo == "casa":
            datos_bd["elevador"] = None
        else:
            datos_bd["m2_terreno"] = None
            datos_bd["patio"] = None

        exito = self.gestor_db.registrar_inmueble(datos_bd)
        if exito:
            return True, f"¡Propiedad publicada con éxito! ID: {id_inmueble}"
        return False, "Ocurrió un error al intentar guardar en la base de datos."
    
    def editar_propiedad(self, datos_formulario: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Actualiza los datos de una propiedad existente.

        Args:
            datos_formulario: Diccionario con los campos del inmueble, incluyendo 'id_inmueble'.

        Returns:
            Tupla (éxito, mensaje).
        """
        campos_requeridos = ["id_inmueble", "titulo", "direccion", "precio", "tipo", "id_arrendador"]
        for campo in campos_requeridos:
            if campo not in datos_formulario or not str(datos_formulario[campo]).strip():
                return False, f"El campo '{campo.capitalize()}' es obligatorio."

        tipo = datos_formulario["tipo"]
        if tipo not in ("casa", "departamento"):
            return False, "Tipo de inmueble no válido."

        id_inmueble = datos_formulario["id_inmueble"]
        detalle = self.gestor_db.consultar_detalle_inmueble(id_inmueble)
        if not detalle:
            return False, "La propiedad no existe."
        if detalle.get("id_arrendador") != datos_formulario["id_arrendador"]:
            return False, "No puedes editar una propiedad que no es tuya."

        inmuebles = self.gestor_db.consultar_inmuebles_arrendador(datos_formulario["id_arrendador"])
        for inm in inmuebles:
            if inm["id_inmueble"] == id_inmueble and inm.get("tiene_renta_activa"):
                return False, "No puedes editar una propiedad con renta activa."

        try:
            if tipo == "casa":
                inmueble = Casa(
                    id_inmueble=id_inmueble,
                    id_arrendador=datos_formulario["id_arrendador"],
                    titulo=datos_formulario["titulo"],
                    descripcion=datos_formulario.get("descripcion", ""),
                    direccion=datos_formulario["direccion"],
                    precio_renta=float(datos_formulario["precio"]),
                    m2_terreno=int(datos_formulario.get("m2_terreno", 0)),
                    m2_construccion=int(datos_formulario.get("m2_construccion", 0)),
                    recamaras=int(datos_formulario.get("recamaras", 0)),
                    banos=int(datos_formulario.get("banos", 0)),
                    medios_banos=int(datos_formulario.get("medios_banos", 0)),
                    estacionamientos=int(datos_formulario.get("estacionamientos", 0)),
                    antiguedad=int(datos_formulario.get("antiguedad", 0)),
                    alberca=bool(datos_formulario.get("alberca", False)),
                    amueblado=bool(datos_formulario.get("amueblado", False)),
                    cocina_integral=bool(datos_formulario.get("cocina_integral", False)),
                    cuarto_servicio=bool(datos_formulario.get("cuarto_servicio", False)),
                    seguridad=bool(datos_formulario.get("seguridad", False)),
                    patio=bool(datos_formulario.get("patio", False)),
                    fecha_publicacion=detalle["fecha_publicacion"],
                    tipo_inmueble="casa",
                    disponible=detalle.get("disponible", True)
                )
            else:
                inmueble = Departamento(
                    id_inmueble=id_inmueble,
                    id_arrendador=datos_formulario["id_arrendador"],
                    titulo=datos_formulario["titulo"],
                    descripcion=datos_formulario.get("descripcion", ""),
                    direccion=datos_formulario["direccion"],
                    precio_renta=float(datos_formulario["precio"]),
                    m2_construccion=int(datos_formulario.get("m2_construccion", 0)),
                    recamaras=int(datos_formulario.get("recamaras", 0)),
                    banos=int(datos_formulario.get("banos", 0)),
                    medios_banos=int(datos_formulario.get("medios_banos", 0)),
                    estacionamientos=int(datos_formulario.get("estacionamientos", 0)),
                    antiguedad=int(datos_formulario.get("antiguedad", 0)),
                    alberca=bool(datos_formulario.get("alberca", False)),
                    amueblado=bool(datos_formulario.get("amueblado", False)),
                    cocina_integral=bool(datos_formulario.get("cocina_integral", False)),
                    cuarto_servicio=bool(datos_formulario.get("cuarto_servicio", False)),
                    seguridad=bool(datos_formulario.get("seguridad", False)),
                    elevador=bool(datos_formulario.get("elevador", False)),
                    fecha_publicacion=detalle["fecha_publicacion"],
                    tipo_inmueble="departamento",
                    disponible=detalle.get("disponible", True)
                )
        except (ValueError, TypeError) as e:
            return False, f"Error en los datos: {e}"

        datos_bd = inmueble.obtener_datos_inmueble()
        datos_bd["id_inmueble"] = id_inmueble
        datos_bd["esta_disponible"] = int(datos_bd.pop("disponible"))

        if tipo == "casa":
            datos_bd["elevador"] = None
        else:
            datos_bd["m2_terreno"] = None
            datos_bd["patio"] = None

        exito = self.gestor_db.actualizar_inmueble(datos_bd)
        if exito:
            return True, f"Propiedad {id_inmueble} actualizada con éxito."
        return False, "Ocurrió un error al intentar guardar los cambios."
    
    def obtener_detalle_propiedad(self, id_inmueble: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene el detalle completo de un inmueble.

        Args:
            id_inmueble: Identificador del inmueble.

        Returns:
            Diccionario con los datos del inmueble o None si no existe.
        """
        return self.gestor_db.consultar_detalle_inmueble(id_inmueble)
    
    def obtener_rentas(self, id_arrendador: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Obtiene todas las rentas asociadas a los inmuebles del arrendador.

        Args:
            id_arrendador: Identificador del arrendador.

        Returns:
            Tupla (éxito, lista_de_rentas).
        """
        rentas = self.gestor_db.consultar_rentas_arrendador(id_arrendador)
        if rentas:
            return True, rentas
        return False, "No se encontraron rentas."
    
    def cancelar_renta_propia(self, id_renta: str, id_arrendador: str, motivo: str) -> Tuple[bool, str]:
        """
        Permite al arrendador cancelar una de sus rentas activas.

        Args:
            id_renta: Identificador de la renta.
            id_arrendador: Identificador del arrendador (dueño).
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
        if renta.id_arrendador != id_arrendador:
            return False, "No puedes cancelar una renta que no pertenece a tus inmuebles."

        try:
            renta.cancelar_renta(motivo.strip())
        except RuntimeError as e:
            return False, str(e)

        datos_actualizados = renta.obtener_datos_renta()
        exito = self.gestor_db.actualizar_estado_renta(datos_actualizados)
        if exito:
            self.gestor_db.cambiar_disponibilidad_inmueble(renta.id_inmueble, 1)
            return True, f"La renta {id_renta} ha sido cancelada y el inmueble liberado."
        return False, "No se pudo cancelar la renta."
    
    def finalizar_renta_propia(self, id_renta: str, id_arrendador: str, fecha_fin_real: str) -> Tuple[bool, str]:
        """
        Permite al arrendador finalizar una de sus rentas activas.

        Args:
            id_renta: Identificador de la renta.
            id_arrendador: Identificador del arrendador (dueño).
            fecha_fin_real: Fecha real de finalización (YYYY-MM-DD).

        Returns:
            Tupla (éxito, mensaje).
        """
        renta_data = self.gestor_db.obtener_renta_por_id(id_renta)
        if not renta_data:
            return False, "La renta no existe."

        renta = Renta.from_dict(renta_data)
        if renta.id_arrendador != id_arrendador:
            return False, "No puedes finalizar una renta que no pertenece a tus inmuebles."

        try:
            renta.finalizar_renta(fecha_fin_real)
        except (RuntimeError, ValueError) as e:
            return False, str(e)

        datos_actualizados = renta.obtener_datos_renta()
        exito = self.gestor_db.actualizar_estado_renta(datos_actualizados)
        if exito:
            self.gestor_db.cambiar_disponibilidad_inmueble(renta.id_inmueble, 1)
            return True, f"La renta {id_renta} ha sido finalizada."
        return False, "No se pudo finalizar la renta."
    
    def desactivar_propiedad(self, id_inmueble: str, id_arrendador: str) -> Tuple[bool, str]:
        """
        Desactiva una propiedad propia, siempre que no tenga una renta activa.

        Args:
            id_inmueble: Identificador del inmueble.
            id_arrendador: Identificador del arrendador propietario.

        Returns:
            Tupla (éxito, mensaje).
        """
        detalle = self.gestor_db.consultar_detalle_inmueble(id_inmueble)
        if not detalle:
            return False, "La propiedad no existe."
        if detalle.get("id_arrendador") != id_arrendador:
            return False, "No puedes modificar una propiedad que no es tuya."
        if not detalle.get("disponible"):
            return False, "La propiedad ya está desactivada."

        inmuebles = self.gestor_db.consultar_inmuebles_arrendador(id_arrendador)
        for inm in inmuebles:
            if inm["id_inmueble"] == id_inmueble and inm.get("tiene_renta_activa"):
                return False, "No puedes desactivar una propiedad con renta activa."

        self.gestor_db.cambiar_disponibilidad_inmueble(id_inmueble, False)
        return True, "Propiedad desactivada correctamente."


    def reactivar_propiedad(self, id_inmueble: str, id_arrendador: str) -> Tuple[bool, str]:
        """
        Reactiva (vuelve a publicar) una propiedad propia que estaba desactivada.

        Args:
            id_inmueble: Identificador del inmueble.
            id_arrendador: Identificador del arrendador propietario.

        Returns:
            Tupla (éxito, mensaje).
        """
        detalle = self.gestor_db.consultar_detalle_inmueble(id_inmueble)
        if not detalle:
            return False, "La propiedad no existe."
        if detalle.get("id_arrendador") != id_arrendador:
            return False, "No puedes modificar una propiedad que no es tuya."
        if detalle.get("disponible"):
            return False, "La propiedad ya está activa."

        self.gestor_db.cambiar_disponibilidad_inmueble(id_inmueble, True)
        return True, "Propiedad reactivada correctamente."

    def obtener_perfil(self, id_usuario: str) -> Tuple[bool, Union[Dict[str, str], str]]:
        """
        Obtiene los datos del perfil del arrendador, excluyendo la contraseña.

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
        Actualiza los datos del perfil del arrendador.

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
        Cambia la contraseña del arrendador tras verificar la actual.

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
        Autoelimina la cuenta del arrendador, liberando su email.
        No se permite si tiene propiedades con rentas activas.

        Args:
            id_usuario: Identificador del usuario.

        Returns:
            Tupla (éxito, mensaje).
        """
        inmuebles = self.gestor_db.consultar_inmuebles_arrendador(id_usuario)
        for inm in inmuebles:
            if inm.get("tiene_renta_activa"):
                return False, "No puedes eliminar tu cuenta porque tienes propiedades con rentas activas."
        exito = self.gestor_db.autoeliminar_usuario(id_usuario)
        if exito:
            return True, "Tu cuenta ha sido eliminada. Ya no podrás acceder."
        return False, "No se pudo eliminar la cuenta."
    
    def obtener_datos_dashboard(
        self,
        id_arrendador: str,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        estados: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Devuelve métricas y datos agrupados por mes para el dashboard del arrendador.

        Args:
            id_arrendador: Identificador del arrendador.
            fecha_inicio: Fecha inicial en formato YYYY-MM-DD (opcional).
            fecha_fin: Fecha final en formato YYYY-MM-DD (opcional).
            estados: Lista de estados a incluir (ej. ['activa']). None para todas.

        Returns:
            Diccionario con total_contratos, contratos_activos, ingresos_totales y rentas_por_mes.
        """
        rentas = self.gestor_db.consultar_rentas_arrendador(id_arrendador)
        if estados is None:
            estados = ['activa', 'finalizada', 'cancelada']
        filtradas = []
        for r in rentas:
            if r['estado'] not in estados:
                continue
            if fecha_inicio and r['fecha_inicio'] < fecha_inicio:
                continue
            if fecha_fin and r['fecha_inicio'] > fecha_fin:
                continue
            filtradas.append(r)

        total_contratos = len(filtradas)
        contratos_activos = sum(1 for r in filtradas if r['estado'] == 'activa')
        ingresos_totales = sum(r['total_contrato'] for r in filtradas if r['total_contrato'])

        por_mes = defaultdict(lambda: {'ingresos': 0.0, 'contratos': 0})
        for r in filtradas:
            fecha = datetime.strptime(r['fecha_inicio'], '%Y-%m-%d')
            mes = fecha.strftime('%Y-%m')
            por_mes[mes]['ingresos'] += r['total_contrato']
            por_mes[mes]['contratos'] += 1

        rentas_por_mes = [{'mes': k, **v} for k, v in sorted(por_mes.items())]

        return {
            'total_contratos': total_contratos,
            'contratos_activos': contratos_activos,
            'ingresos_totales': ingresos_totales,
            'rentas_por_mes': rentas_por_mes,
        }