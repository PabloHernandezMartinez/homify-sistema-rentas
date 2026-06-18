import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

class GestorDB:
    """
    Gestor de base de datos SQLite para el sistema HOMIFY.
    Proporciona métodos CRUD y consultas específicas para usuarios, inmuebles y rentas.
    """

    def __init__(self, ruta_db: str = "sistema.db") -> None:
        self.ruta_db = ruta_db
        self.inicializar_bd()

    # -------------------------------------------------------------------------
    # Métodos de inicialización
    # -------------------------------------------------------------------------
    def inicializar_bd(self) -> None:
        """Crea las tablas necesarias si no existen."""
        conexion = sqlite3.connect(self.ruta_db)
        cursor = conexion.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            apellido TEXT,
            fecha_nacimiento TEXT,
            genero TEXT,
            email TEXT UNIQUE NOT NULL,
            telefono TEXT,
            password TEXT NOT NULL,
            fecha_registro TEXT,
            estado TEXT DEFAULT 'activo',
            rol TEXT NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inmuebles (
            id_inmueble TEXT PRIMARY KEY,
            id_arrendador TEXT NOT NULL,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            direccion TEXT NOT NULL,
            precio_renta REAL NOT NULL,
            m2_construccion INTEGER NOT NULL,
            recamaras INTEGER,
            banos INTEGER,
            medios_banos INTEGER,
            estacionamientos INTEGER,
            antiguedad INTEGER,
            alberca INTEGER DEFAULT 0,
            amueblado INTEGER DEFAULT 0,
            cocina_integral INTEGER DEFAULT 0,
            cuarto_servicio INTEGER DEFAULT 0,
            seguridad INTEGER DEFAULT 0,
            fecha_publicacion TEXT,
            tipo_inmueble TEXT NOT NULL,
            esta_disponible INTEGER DEFAULT 1,
            m2_terreno INTEGER,
            patio INTEGER,
            elevador INTEGER,
            FOREIGN KEY (id_arrendador) REFERENCES usuarios(id_usuario)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS rentas (
            id_renta TEXT PRIMARY KEY,
            id_cliente TEXT NOT NULL,
            id_inmueble TEXT NOT NULL,
            id_arrendador TEXT NOT NULL,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT NOT NULL,
            precio_mensual REAL NOT NULL,
            total REAL NOT NULL,
            deposito REAL,
            metodo_pago TEXT,
            estado TEXT DEFAULT 'activa',
            fecha_fin_real TEXT,
            motivo_cancelacion TEXT,
            FOREIGN KEY (id_cliente) REFERENCES usuarios(id_usuario),
            FOREIGN KEY (id_inmueble) REFERENCES inmuebles(id_inmueble),
            FOREIGN KEY (id_arrendador) REFERENCES usuarios(id_usuario)
        );
        """)

        conexion.commit()
        conexion.close()

    # -------------------------------------------------------------------------
    # Métodos de usuarios
    # -------------------------------------------------------------------------
    def actualizar_password_usuario(self, id_usuario: str, nuevo_hash: str) -> bool:
        """Actualiza el hash de la contraseña del usuario. Retorna True si se modificó al menos una fila."""
        conexion = sqlite3.connect(self.ruta_db)
        cursor = conexion.cursor()
        consulta = "UPDATE usuarios SET password = ? WHERE id_usuario = ?"
        try:
            cursor.execute(consulta, (nuevo_hash, id_usuario))
            conexion.commit()
            exito = cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al actualizar contraseña: {e}")
            exito = False
        finally:
            conexion.close()
        return exito

    def actualizar_perfil_usuario(
        self,
        id_usuario: str,
        nombre: str,
        apellido: str,
        fecha_nacimiento: str,
        genero: str,
        email: str,
        telefono: str
    ) -> bool:
        """Actualiza los datos personales del usuario. Retorna True si se afectó al menos un registro."""
        conexion = sqlite3.connect(self.ruta_db)
        cursor = conexion.cursor()
        consulta = """
            UPDATE usuarios 
            SET nombre = ?, apellido = ?, fecha_nacimiento = ?, genero = ?, email = ?, telefono = ?
            WHERE id_usuario = ?
        """
        try:
            cursor.execute(consulta, (nombre, apellido, fecha_nacimiento, genero, email, telefono, id_usuario))
            conexion.commit()
            exito = cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al actualizar perfil: {e}")
            exito = False
        finally:
            conexion.close()
        return exito

    def actualizar_estado_usuario(self, id_usuario: str, nuevo_estado: str) -> bool:
        """Cambia el estado de un usuario. Retorna True si se actualizó."""
        conexion = sqlite3.connect(self.ruta_db)
        cursor = conexion.cursor()
        consulta = "UPDATE usuarios SET estado = ? WHERE id_usuario = ?"
        cursor.execute(consulta, (nuevo_estado, id_usuario))
        conexion.commit()
        filas_afectadas = cursor.rowcount
        conexion.close()
        return filas_afectadas > 0

    def consultar_usuarios_admin(
        self,
        buscar_id: Optional[str] = None,
        ver_activos: bool = True,
        ver_suspendidos: bool = False,
        ver_eliminados: bool = False,
        rol: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Devuelve lista de usuarios según filtros para el panel de administración."""
        conexion = sqlite3.connect(self.ruta_db)
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        consulta = "SELECT id_usuario, nombre, apellido, email, telefono, rol, estado FROM usuarios WHERE 1=1"
        parametros: List[Any] = []

        if buscar_id:
            consulta += " AND id_usuario = ?"
            parametros.append(buscar_id)
        else:
            estados_seleccionados = []
            if ver_activos:
                estados_seleccionados.append('activo')
            if ver_suspendidos:
                estados_seleccionados.append('suspendido')
            if ver_eliminados:
                estados_seleccionados.append('eliminado')
            if estados_seleccionados:
                placeholders = ",".join(["?"] * len(estados_seleccionados))
                consulta += f" AND estado IN ({placeholders})"
                parametros.extend(estados_seleccionados)
            else:
                consulta += " AND 1=0"
            if rol:
                consulta += " AND rol = ?"
                parametros.append(rol)

        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()
        conexion.close()
        return [dict(fila) for fila in filas]

    def obtener_usuario_por_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Busca un usuario por email.
        Retorna un diccionario con 'fecha_registro' convertida a datetime, o None si no se encuentra.
        """
        conexion = sqlite3.connect(self.ruta_db)
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        consulta = "SELECT * FROM usuarios WHERE email = ?"
        cursor.execute(consulta, (email,))
        fila = cursor.fetchone()
        conexion.close()
        if fila:
            datos = dict(fila)
            if 'fecha_registro' in datos and datos['fecha_registro']:
                datos['fecha_registro'] = datetime.fromisoformat(datos['fecha_registro'])
            return datos
        return None

    def obtener_usuario_por_id(self, id_usuario: str) -> Optional[Dict[str, Any]]:
        """
        Busca un usuario por id.
        Retorna un diccionario con 'fecha_registro' convertida a datetime, o None.
        """
        conexion = sqlite3.connect(self.ruta_db)
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (id_usuario,))
        fila = cursor.fetchone()
        conexion.close()
        if fila:
            datos = dict(fila)
            if 'fecha_registro' in datos and datos['fecha_registro']:
                datos['fecha_registro'] = datetime.fromisoformat(datos['fecha_registro'])
            return datos
        return None

    def registrar_usuario(self, datos: Dict[str, Any]) -> bool:
        """
        Inserta un nuevo usuario.
        Requiere que 'fecha_nacimiento' y 'genero' no sean None.
        Retorna True si se insertó correctamente.
        """
        if not datos.get("fecha_nacimiento"):
            print("Error: fecha_nacimiento es obligatorio")
            return False
        if not datos.get("genero"):
            print("Error: genero es obligatorio")
            return False

        conexion = sqlite3.connect(self.ruta_db)
        cursor = conexion.cursor()
        consulta = """
            INSERT INTO usuarios (
                id_usuario, nombre, apellido, fecha_nacimiento, genero, 
                email, telefono, password, fecha_registro, estado, rol
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        if "nombre" in datos:
            nombre = datos["nombre"]
            apellido = datos.get("apellido", "")
        elif "nombre_completo" in datos:
            partes = datos["nombre_completo"].split()
            nombre = partes[0] if partes else ""
            apellido = " ".join(partes[1:]) if len(partes) > 1 else ""
        else:
            nombre = ""
            apellido = ""

        valores = (
            datos["id_usuario"],
            nombre,
            apellido,
            datos["fecha_nacimiento"],
            datos["genero"],
            datos["email"],
            datos.get("telefono"),
            datos["password"],
            datos.get("fecha_registro"),
            datos.get("estado", "activo"),
            datos["rol"]
        )
        try:
            cursor.execute(consulta, valores)
            conexion.commit()
            exito = True
        except sqlite3.IntegrityError as e:
            print(f"Error de integridad: {e}")
            exito = False
        finally:
            conexion.close()
        return exito
    
    def autoeliminar_usuario(self, id_usuario: str) -> bool:
        """
        Marca al usuario como eliminado y modifica su email para que quede libre.
        Retorna True si la operación afectó al menos una fila.
        """
        conexion = sqlite3.connect(self.ruta_db)
        cursor = conexion.cursor()
        consulta = """
            UPDATE usuarios SET estado = 'eliminado',
                email = 'eliminado_' || id_usuario || '@deleted.homify'
            WHERE id_usuario = ?
        """
        try:
            cursor.execute(consulta, (id_usuario,))
            conexion.commit()
            exito = cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al autoeliminar usuario: {e}")
            exito = False
        finally:
            conexion.close()
        return exito

    # -------------------------------------------------------------------------
    # Métodos de inmuebles
    # -------------------------------------------------------------------------
    def actualizar_precio_inmueble(self, id_inmueble: str, nuevo_precio: float) -> bool:
        """Actualiza el precio de renta de un inmueble."""
        conexion = sqlite3.connect(self.ruta_db)
        cursor = conexion.cursor()
        consulta = "UPDATE inmuebles SET precio_renta = ? WHERE id_inmueble = ?"
        try:
            cursor.execute(consulta, (float(nuevo_precio), id_inmueble))
            conexion.commit()
            exito = cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al actualizar precio del inmueble: {e}")
            exito = False
        finally:
            conexion.close()
        return exito

    def cambiar_disponibilidad_inmueble(self, id_inmueble: str, esta_disponible: bool) -> bool:
        """Actualiza la disponibilidad de un inmueble."""
        conexion = sqlite3.connect(self.ruta_db)
        cursor = conexion.cursor()
        consulta = "UPDATE inmuebles SET esta_disponible = ? WHERE id_inmueble = ?"
        cursor.execute(consulta, (int(esta_disponible), id_inmueble))
        conexion.commit()
        conexion.close()
        return True

    def consultar_detalle_inmueble(self, id_inmueble: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene todos los datos de un inmueble.
        Convierte campos booleanos a True/False.
        """
        conexion = sqlite3.connect(self.ruta_db)
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        consulta = "SELECT * FROM inmuebles WHERE id_inmueble = ?"
        cursor.execute(consulta, [id_inmueble])
        fila = cursor.fetchone()
        conexion.close()
        if fila:
            detalle = dict(fila)
            booleanos = ["alberca", "amueblado", "cocina_integral", "cuarto_servicio",
                            "seguridad", "esta_disponible"]
            for campo in booleanos:
                if campo in detalle and detalle[campo] is not None:
                    detalle[campo] = bool(detalle[campo])
            if detalle.get("patio") is not None:
                detalle["patio"] = bool(detalle["patio"])
            if detalle.get("elevador") is not None:
                detalle["elevador"] = bool(detalle["elevador"])
            detalle["disponible"] = bool(detalle.get("esta_disponible", False))
            return detalle
        return None

    def consultar_disponibles(
        self,
        direccion: Optional[str] = None,
        precio_min: Optional[float] = None,
        precio_max: Optional[float] = None,
        m2_min: Optional[float] = None,
        m2_max: Optional[float] = None,
        tipo: Optional[str] = None,
        recamaras: Optional[int] = None,
        banos: Optional[int] = None,
        estacionamientos: Optional[int] = None,
        antiguedad: Optional[int] = None,
        amueblado: bool = False,
        alberca: bool = False,
        cocina_integral: bool = False,
        cuarto_servicio: bool = False,
        seguridad: bool = False,
        patio: bool = False,
        elevador: bool = False
    ) -> List[Dict[str, Any]]:
        """Devuelve una lista de inmuebles disponibles según múltiples filtros."""
        conexion = sqlite3.connect(self.ruta_db)
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()

        consulta = "SELECT * FROM inmuebles WHERE esta_disponible = 1"
        parametros: List[Any] = []

        if direccion:
            consulta += " AND direccion LIKE ?"
            parametros.append(f"%{direccion}%")
        if precio_min:
            consulta += " AND precio_renta >= ?"
            parametros.append(float(precio_min))
        if precio_max:
            consulta += " AND precio_renta <= ?"
            parametros.append(float(precio_max))
        if m2_min:
            consulta += " AND m2_construccion >= ?"
            parametros.append(float(m2_min))
        if m2_max:
            consulta += " AND m2_construccion <= ?"
            parametros.append(float(m2_max))
        if tipo and tipo != "Todos":
            consulta += " AND tipo_inmueble = ?"
            parametros.append(tipo)
        if recamaras:
            consulta += " AND recamaras >= ?"
            parametros.append(int(recamaras))
        if banos:
            consulta += " AND banos >= ?"
            parametros.append(int(banos))
        if estacionamientos:
            consulta += " AND estacionamientos >= ?"
            parametros.append(int(estacionamientos))
        if antiguedad:
            consulta += " AND antiguedad <= ?"
            parametros.append(int(antiguedad))

        if amueblado:
            consulta += " AND amueblado = 1"
        if alberca:
            consulta += " AND alberca = 1"
        if cocina_integral:
            consulta += " AND cocina_integral = 1"
        if cuarto_servicio:
            consulta += " AND cuarto_servicio = 1"
        if seguridad:
            consulta += " AND seguridad = 1"
        if patio:
            consulta += " AND patio = 1"
        if elevador:
            consulta += " AND elevador = 1"

        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()
        conexion.close()

        resultados = []
        for fila in filas:
            resultados.append({
                "id_inmueble": fila["id_inmueble"],
                "titulo": fila["titulo"],
                "m2": fila["m2_construccion"],
                "precio": fila["precio_renta"],
                "direccion": fila["direccion"],
                "tipo": fila["tipo_inmueble"],
                "disponible": bool(fila["esta_disponible"])
            })
        return resultados

    def consultar_inmuebles_admin(self, buscar_id: Optional[str] = None,
                                    tipo_inmueble: Optional[str] = None,
                                    id_arrendador: Optional[str] = None,
                                    esta_disponible: Optional[bool] = None
                                    ) -> List[Dict[str, Any]]:
        """
        Devuelve todos los inmuebles, opcionalmente filtrados por id, 
        tipo, arrendador o estado de disponibilidad.
        """
        conexion = sqlite3.connect(self.ruta_db)
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        consulta = "SELECT * FROM inmuebles WHERE 1=1"
        parametros = []
        if buscar_id:
            consulta += " AND id_inmueble = ?"
            parametros.append(buscar_id)
        if tipo_inmueble:
            consulta += " AND tipo_inmueble = ?"
            parametros.append(tipo_inmueble)
        if id_arrendador:
            consulta += " AND id_arrendador = ?"
            parametros.append(id_arrendador)
        if esta_disponible is not None:
            consulta += " AND esta_disponible = ?"
            parametros.append(int(esta_disponible))
        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()
        conexion.close()
        return [dict(fila) for fila in filas]

    def consultar_inmuebles_arrendador(self, id_arrendador: str) -> List[Dict[str, Any]]:
        """
        Devuelve los inmuebles de un arrendador, incluyendo datos de la renta activa
        (si existe), el inquilino, las fechas del contrato y la ganancia mensual.
        """
        conexion = sqlite3.connect(self.ruta_db)
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()

        consulta = """
            SELECT 
                i.id_inmueble, 
                i.titulo, 
                i.tipo_inmueble, 
                i.esta_disponible,
                i.direccion,
                i.precio_renta,
                r.id_renta,
                r.precio_mensual AS ganancia,
                r.fecha_inicio,
                r.fecha_fin,
                u.nombre || ' ' || u.apellido AS inquilino
            FROM inmuebles i
            LEFT JOIN rentas r ON i.id_inmueble = r.id_inmueble AND r.estado = 'activa'
            LEFT JOIN usuarios u ON r.id_cliente = u.id_usuario
            WHERE i.id_arrendador = ?
        """
        cursor.execute(consulta, [id_arrendador])
        filas = cursor.fetchall()
        conexion.close()

        resultados = []
        for fila in filas:
            renta_activa = fila["id_renta"] is not None
            ganancia = fila["ganancia"] if fila["ganancia"] else 0.0
            resultados.append({
                "id_inmueble": fila["id_inmueble"],
                "titulo": fila["titulo"],
                "tipo": fila["tipo_inmueble"],
                "disponible": bool(fila["esta_disponible"]),
                "direccion": fila["direccion"],
                "precio_renta": fila["precio_renta"],
                "tiene_renta_activa": renta_activa,
                "id_renta_activa": fila["id_renta"],
                "inquilino": fila["inquilino"] or "",
                "fecha_inicio_renta": fila["fecha_inicio"],
                "fecha_fin_renta": fila["fecha_fin"],
                "ganancia_mensual": ganancia
            })
        return resultados

    def consultar_inmuebles_paginados(self, limit: int, offset: int) -> List[Dict[str, Any]]:
        """Devuelve una página de inmuebles disponibles."""
        conexion = sqlite3.connect(self.ruta_db)
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        consulta = "SELECT * FROM inmuebles WHERE esta_disponible = 1 LIMIT ? OFFSET ?"
        cursor.execute(consulta, (limit, offset))
        filas = cursor.fetchall()
        conexion.close()

        resultados = []
        for fila in filas:
            resultados.append({
                "id_inmueble": fila["id_inmueble"],
                "titulo": fila["titulo"],
                "m2": fila["m2_construccion"],
                "precio": fila["precio_renta"],
                "direccion": fila["direccion"],
                "tipo": fila["tipo_inmueble"],
                "disponible": bool(fila["esta_disponible"])
            })
        return resultados

    def contar_inmuebles_disponibles(self) -> int:
        """Cuenta los inmuebles actualmente disponibles."""
        conexion = sqlite3.connect(self.ruta_db)
        cursor = conexion.cursor()
        consulta = "SELECT COUNT(*) FROM inmuebles WHERE esta_disponible = 1"
        cursor.execute(consulta)
        total = cursor.fetchone()[0]
        conexion.close()
        return total

    def registrar_inmueble(self, datos: Dict[str, Any]) -> bool:
        """Inserta un nuevo inmueble en la base de datos."""
        conexion = sqlite3.connect(self.ruta_db)
        cursor = conexion.cursor()
        consulta = """
            INSERT INTO inmuebles (
                id_inmueble, id_arrendador, titulo, descripcion, direccion, 
                precio_renta, m2_construccion, recamaras, banos, medios_banos, 
                estacionamientos, antiguedad, alberca, amueblado, cocina_integral, 
                cuarto_servicio, seguridad, fecha_publicacion, tipo_inmueble, 
                esta_disponible, m2_terreno, patio, elevador
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        valores = (
            datos["id_inmueble"], datos["id_arrendador"], datos["titulo"],
            datos["descripcion"], datos["direccion"], datos["precio_renta"],
            datos["m2_construccion"], datos["recamaras"], datos["banos"],
            datos["medios_banos"], datos["estacionamientos"], datos["antiguedad"],
            int(datos.get("alberca", 0)), int(datos.get("amueblado", 0)),
            int(datos.get("cocina_integral", 0)), int(datos.get("cuarto_servicio", 0)),
            int(datos.get("seguridad", 0)), datos["fecha_publicacion"],
            datos["tipo_inmueble"], int(datos.get("esta_disponible", datos.get("disponible", 1))),
            datos.get("m2_terreno"),
            int(datos["patio"]) if datos.get("patio") is not None else None,
            int(datos["elevador"]) if datos.get("elevador") is not None else None
        )
        try:
            cursor.execute(consulta, valores)
            conexion.commit()
            exito = True
        except sqlite3.Error as e:
            print(f"Error al registrar inmueble: {e}")
            exito = False
        finally:
            conexion.close()
        return exito

    def actualizar_inmueble(self, datos: Dict[str, Any]) -> bool:
        """Actualiza todos los campos editables de un inmueble existente."""
        conexion = sqlite3.connect(self.ruta_db)
        cursor = conexion.cursor()
        consulta = """
            UPDATE inmuebles SET
                titulo = ?, descripcion = ?, direccion = ?, precio_renta = ?,
                m2_construccion = ?, recamaras = ?, banos = ?, medios_banos = ?,
                estacionamientos = ?, antiguedad = ?, alberca = ?, amueblado = ?,
                cocina_integral = ?, cuarto_servicio = ?, seguridad = ?,
                tipo_inmueble = ?, m2_terreno = ?, patio = ?, elevador = ?
            WHERE id_inmueble = ?
        """
        valores = (
            datos["titulo"],
            datos["descripcion"],
            datos["direccion"],
            datos["precio_renta"],
            datos["m2_construccion"],
            datos["recamaras"],
            datos["banos"],
            datos["medios_banos"],
            datos["estacionamientos"],
            datos["antiguedad"],
            int(datos.get("alberca", 0)),
            int(datos.get("amueblado", 0)),
            int(datos.get("cocina_integral", 0)),
            int(datos.get("cuarto_servicio", 0)),
            int(datos.get("seguridad", 0)),
            datos["tipo_inmueble"],
            datos.get("m2_terreno"),
            int(datos["patio"]) if datos.get("patio") is not None else None,
            int(datos["elevador"]) if datos.get("elevador") is not None else None,
            datos["id_inmueble"]
        )
        try:
            cursor.execute(consulta, valores)
            conexion.commit()
            exito = cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al actualizar inmueble: {e}")
            exito = False
        finally:
            conexion.close()
        return exito

    # -------------------------------------------------------------------------
    # Métodos de rentas
    # -------------------------------------------------------------------------
    def consultar_rentas_arrendador(self, id_arrendador: str) -> List[Dict[str, Any]]:
        """Devuelve las rentas asociadas a los inmuebles de un arrendador."""
        conexion = sqlite3.connect(self.ruta_db)
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        consulta = """
            SELECT 
                r.id_renta,
                r.fecha_inicio,
                r.fecha_fin,
                r.precio_mensual,
                r.total,
                r.estado,
                i.titulo AS inmueble,
                i.tipo_inmueble,
                u.nombre || ' ' || u.apellido AS inquilino,
                u.email AS email_inquilino,
                u.telefono AS telefono_inquilino
            FROM rentas r
            JOIN inmuebles i ON r.id_inmueble = i.id_inmueble
            JOIN usuarios u ON r.id_cliente = u.id_usuario
            WHERE i.id_arrendador = ?
            ORDER BY r.fecha_inicio DESC
        """
        cursor.execute(consulta, [id_arrendador])
        filas = cursor.fetchall()
        conexion.close()
        resultados = []
        for fila in filas:
            resultados.append({
                "id_renta": fila["id_renta"],
                "inmueble": fila["inmueble"],
                "tipo_propiedad": fila["tipo_inmueble"],
                "inquilino": fila["inquilino"],
                "contacto_inquilino": f"📧 {fila['email_inquilino']} | 📱 {fila['telefono_inquilino']}",
                "fecha_inicio": fila["fecha_inicio"],
                "fecha_fin": fila["fecha_fin"],
                "precio_mensual": fila["precio_mensual"],
                "total_contrato": fila["total"],
                "estado": fila["estado"]
            })
        return resultados

    def consultar_rentas_cliente(
        self,
        id_cliente: str,
        ver_activas: bool = True,
        ver_finalizadas: bool = False,
        ver_canceladas: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Devuelve las rentas de un cliente según los estados solicitados, 
        incluyendo el nombre del arrendador.
        """
        conexion = sqlite3.connect(self.ruta_db)
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        consulta = """
            SELECT r.*, i.titulo, i.direccion, a.nombre || ' ' || a.apellido AS arrendador
            FROM rentas r
            JOIN inmuebles i ON r.id_inmueble = i.id_inmueble
            JOIN usuarios a ON r.id_arrendador = a.id_usuario
            WHERE r.id_cliente = ?
        """
        parametros: List[Any] = [id_cliente]
        estados_seleccionados = []
        if ver_activas:
            estados_seleccionados.append('activa')
        if ver_finalizadas:
            estados_seleccionados.append('finalizada')
        if ver_canceladas:
            estados_seleccionados.append('cancelada')
        if estados_seleccionados:
            placeholders = ",".join(["?"] * len(estados_seleccionados))
            consulta += f" AND r.estado IN ({placeholders})"
            parametros.extend(estados_seleccionados)
        else:
            consulta += " AND 1=0"
        consulta += " ORDER BY r.fecha_inicio DESC"
        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()
        conexion.close()
        resultados = []
        for fila in filas:
            resultados.append({
                "id_renta": fila["id_renta"],
                "inmueble": fila["titulo"],
                "arrendador": fila["arrendador"],
                "direccion": fila["direccion"],
                "fecha_inicio": fila["fecha_inicio"],
                "fecha_fin": fila["fecha_fin"],
                "estado": fila["estado"],
                "precio_mensual": fila["precio_mensual"],
                "total": fila["total"]
            })
        return resultados

    def consultar_rentas_globales(self, id_cliente: Optional[str] = None,
                                    id_arrendador: Optional[str] = None,
                                    estado: Optional[str] = None
                                    ) -> List[Dict[str, Any]]:
        """
        Obtiene todas las rentas con datos extendidos para el administrador.
        Permite filtrar opcionalmente por id de cliente, id de arrendador y estado.
        """
        conexion = sqlite3.connect(self.ruta_db)
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        consulta = """
            SELECT r.id_renta, r.estado, r.fecha_inicio, r.precio_mensual,
                    i.titulo AS inmueble,
                    c.id_usuario AS id_cliente, c.nombre || ' ' || c.apellido AS cliente,
                    a.id_usuario AS id_arrendador, a.nombre || ' ' || a.apellido AS propietario
            FROM rentas r
            JOIN inmuebles i ON r.id_inmueble = i.id_inmueble
            JOIN usuarios c ON r.id_cliente = c.id_usuario
            JOIN usuarios a ON r.id_arrendador = a.id_usuario
            WHERE 1=1
        """
        parametros = []
        if id_cliente:
            consulta += " AND r.id_cliente = ?"
            parametros.append(id_cliente)
        if id_arrendador:
            consulta += " AND r.id_arrendador = ?"
            parametros.append(id_arrendador)
        if estado:
            consulta += " AND r.estado = ?"
            parametros.append(estado)
        consulta += " ORDER BY r.fecha_inicio DESC"
        cursor.execute(consulta, parametros)
        filas = cursor.fetchall()
        conexion.close()
        return [dict(fila) for fila in filas]

    def hay_solapamiento(self, id_inmueble: str, fecha_inicio: str, fecha_fin: str) -> bool:
        """Verifica si hay otra renta activa que se solape con el rango dado."""
        conexion = sqlite3.connect(self.ruta_db)
        cursor = conexion.cursor()
        consulta = """
            SELECT COUNT(*) FROM rentas
            WHERE id_inmueble = ?
            AND estado = 'activa'
            AND (
                (fecha_inicio BETWEEN ? AND ?) OR
                (fecha_fin BETWEEN ? AND ?) OR
                (? BETWEEN fecha_inicio AND fecha_fin) OR
                (? BETWEEN fecha_inicio AND fecha_fin)
            )
        """
        cursor.execute(consulta, (id_inmueble, fecha_inicio, fecha_fin, fecha_inicio, fecha_fin, fecha_inicio, fecha_fin))
        count = cursor.fetchone()[0]
        conexion.close()
        return count > 0
    
    def obtener_renta_solapada(self, id_inmueble: str, fecha_inicio: str, fecha_fin: str) -> Optional[Dict[str, Any]]:
        """
        Retorna la primera renta activa que se solape con el rango dado, o None.
        El diccionario incluye las claves 'fecha_inicio' y 'fecha_fin'.
        """
        conexion = sqlite3.connect(self.ruta_db)
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        consulta = """
            SELECT fecha_inicio, fecha_fin FROM rentas
            WHERE id_inmueble = ?
            AND estado = 'activa'
            AND (
                (fecha_inicio BETWEEN ? AND ?) OR
                (fecha_fin BETWEEN ? AND ?) OR
                (? BETWEEN fecha_inicio AND fecha_fin) OR
                (? BETWEEN fecha_inicio AND fecha_fin)
            )
            LIMIT 1
        """
        cursor.execute(consulta, (id_inmueble, fecha_inicio, fecha_fin, fecha_inicio, fecha_fin, fecha_inicio, fecha_fin))
        fila = cursor.fetchone()
        conexion.close()
        if fila:
            return dict(fila)
        return None

    def obtener_renta_por_id(self, id_renta: str) -> Optional[Dict[str, Any]]:
        """Obtiene una renta por su id."""
        conexion = sqlite3.connect(self.ruta_db)
        conexion.row_factory = sqlite3.Row
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM rentas WHERE id_renta = ?", (id_renta,))
        fila = cursor.fetchone()
        conexion.close()
        if fila:
            return dict(fila)
        return None
    
    def actualizar_estado_renta(self, datos: Dict[str, Any]) -> bool:
        """
        Actualiza el estado, fecha_fin_real y motivo_cancelacion de una renta.
        """
        conexion = sqlite3.connect(self.ruta_db)
        cursor = conexion.cursor()
        consulta = """
            UPDATE rentas SET estado = ?, fecha_fin_real = ?, motivo_cancelacion = ?
            WHERE id_renta = ?
        """
        try:
            cursor.execute(consulta, (
                datos["estado"],
                datos["fecha_fin_real"],
                datos.get("motivo_cancelacion"),
                datos["id_renta"]
            ))
            conexion.commit()
            exito = cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al actualizar estado de renta: {e}")
            exito = False
        finally:
            conexion.close()
        return exito

    def registrar_renta(self, datos: Dict[str, Any]) -> bool:
        """Inserta una nueva renta."""
        conexion = sqlite3.connect(self.ruta_db)
        cursor = conexion.cursor()
        consulta = """
            INSERT INTO rentas (
                id_renta, id_cliente, id_inmueble, id_arrendador, fecha_inicio, 
                fecha_fin, precio_mensual, total, deposito, metodo_pago, 
                estado, fecha_fin_real, motivo_cancelacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        valores = (
            datos["id_renta"], datos["id_cliente"], datos["id_inmueble"],
            datos["id_arrendador"], datos["fecha_inicio"], datos["fecha_fin"],
            datos["precio_mensual"], datos["total"], datos["deposito"],
            datos["metodo_pago"], datos["estado"],
            datos.get("fecha_fin_real"), datos.get("motivo_cancelacion")
        )
        try:
            cursor.execute(consulta, valores)
            conexion.commit()
            exito = True
        except sqlite3.Error as e:
            print(f"Error al registrar renta: {e}")
            exito = False
        finally:
            conexion.close()
        return exito