import re
from datetime import datetime, date
from typing import Union, Dict, Any, Optional
from .enums import Tipo_Inmueble

class Inmueble:
    """
    Clase base que representa un inmueble publicado para renta.

    Atributos:
        id_inmueble (str): Identificador único del inmueble.
        id_arrendador (str): Identificador del arrendador propietario.
        titulo (str): Título del anuncio (máximo 100 caracteres).
        descripcion (str): Descripción detallada (máximo 1000 caracteres).
        direccion (str): Dirección física del inmueble (máximo 200 caracteres).
        precio_renta (float): Precio de renta mensual (positivo).
        m2_construccion (int): Metros cuadrados de construcción (>= 0).
        recamaras (int): Número de recámaras (>= 0).
        banos (int): Número de baños completos (>= 0).
        medios_banos (int): Número de medios baños (>= 0).
        estacionamientos (int): Cajones de estacionamiento (>= 0).
        antiguedad (int): Antigüedad en años (>= 0).
        alberca (bool): Indica si tiene alberca.
        amueblado (bool): Indica si está amueblado.
        cocina_integral (bool): Indica si la cocina es integral.
        cuarto_servicio (bool): Indica si tiene cuarto de servicio.
        seguridad (bool): Indica si cuenta con seguridad privada.
        fecha_publicacion (date): Fecha en que se publicó el inmueble.
        tipo_inmueble (Tipo_Inmueble): Tipo de inmueble (casa o departamento).
        disponible (bool): Indica si el inmueble se encuentra disponible.
    """
    
    def __init__(self,
                    id_inmueble: str,
                    id_arrendador: str,
                    titulo: str,
                    descripcion: str,
                    direccion: str,
                    precio_renta: float,
                    m2_construccion: int,
                    recamaras: int,
                    banos: int,
                    medios_banos: int,
                    estacionamientos: int,
                    antiguedad: int,
                    alberca: bool,
                    amueblado: bool,
                    cocina_integral: bool,
                    cuarto_servicio: bool,
                    seguridad: bool,
                    fecha_publicacion: Union[str, datetime, date],
                    tipo_inmueble: Union[str, Tipo_Inmueble],
                    disponible: bool = True) -> None:
        self.__id_inmueble = str(id_inmueble)
        self.__id_arrendador = str(id_arrendador)
        self.titulo = titulo
        self.descripcion = descripcion
        self.direccion = direccion
        self.precio_renta = float(precio_renta)
        self.m2_construccion = int(m2_construccion)
        self.recamaras = int(recamaras)
        self.banos = int(banos)
        self.medios_banos = int(medios_banos)
        self.estacionamientos = int(estacionamientos)
        self.antiguedad = int(antiguedad)
        self.alberca = bool(alberca)
        self.amueblado = bool(amueblado)
        self.cocina_integral = bool(cocina_integral)
        self.cuarto_servicio = bool(cuarto_servicio)
        self.seguridad = bool(seguridad)
        self.__fecha_publicacion = self._validar_fecha_publicacion(fecha_publicacion)
        self.__tipo_inmueble = Tipo_Inmueble(tipo_inmueble) if not isinstance(tipo_inmueble, Tipo_Inmueble) else tipo_inmueble
        self.__disponible = disponible

    @property
    def id_inmueble(self) -> str:
        """Identificador único del inmueble."""
        return self.__id_inmueble

    @property
    def id_arrendador(self) -> str:
        """Identificador del arrendador propietario."""
        return self.__id_arrendador

    @property
    def fecha_publicacion(self) -> date:
        """Fecha de publicación del anuncio."""
        return self.__fecha_publicacion

    @property
    def tipo_inmueble(self) -> Tipo_Inmueble:
        """Tipo de inmueble (CASA o DEPARTAMENTO)."""
        return self.__tipo_inmueble

    @property
    def es_casa(self) -> bool:
        """True si el inmueble es una casa."""
        return self.__tipo_inmueble == Tipo_Inmueble.CASA

    @property
    def es_departamento(self) -> bool:
        """True si el inmueble es un departamento."""
        return self.__tipo_inmueble == Tipo_Inmueble.DEPARTAMENTO

    @property
    def disponible(self) -> bool:
        """
        Estado actual de disponibilidad.
        Solo se modifica mediante ``marcar_como_rentado()`` o ``marcar_como_disponible()``.
        """
        return self.__disponible

    @property
    def titulo(self) -> str:
        """Título del anuncio."""
        return self.__titulo

    @property
    def descripcion(self) -> str:
        """Descripción detallada del inmueble."""
        return self.__descripcion

    @property
    def direccion(self) -> str:
        """Dirección física del inmueble."""
        return self.__direccion

    @property
    def precio_renta(self) -> float:
        """Precio de renta mensual."""
        return self.__precio_renta

    @property
    def m2_construccion(self) -> int:
        """Metros cuadrados de construcción."""
        return self.__m2_construccion

    @property
    def recamaras(self) -> int:
        """Número de recámaras."""
        return self.__recamaras

    @property
    def banos(self) -> int:
        """Número de baños completos."""
        return self.__banos

    @property
    def medios_banos(self) -> int:
        """Número de medios baños."""
        return self.__medios_banos

    @property
    def estacionamientos(self) -> int:
        """Cajones de estacionamiento."""
        return self.__estacionamientos

    @property
    def antiguedad(self) -> int:
        """Antigüedad en años."""
        return self.__antiguedad

    @property
    def alberca(self) -> bool:
        """Indica si tiene alberca."""
        return self.__alberca

    @property
    def amueblado(self) -> bool:
        """Indica si está amueblado."""
        return self.__amueblado

    @property
    def cocina_integral(self) -> bool:
        """Indica si la cocina es integral."""
        return self.__cocina_integral

    @property
    def cuarto_servicio(self) -> bool:
        """Indica si tiene cuarto de servicio."""
        return self.__cuarto_servicio

    @property
    def seguridad(self) -> bool:
        """Indica si cuenta con seguridad privada."""
        return self.__seguridad

    @titulo.setter
    def titulo(self, valor: str) -> None:
        """
        Establece el título del anuncio después de validarlo.

        Lanza ValueError si está vacío, contiene caracteres no permitidos
        o excede los 100 caracteres.
        """
        if not valor or not isinstance(valor, str):
            raise ValueError("El titulo no puede estar vacío.")
        # Ejemplo para titulo y direccion:
        if not re.match(r'^[A-Za-zÁáÉéÍíÓóÚúÜüÑñ0-9\s.,#\-!¡¿?]+$', valor):
            raise ValueError("El título solo puede contener caracteres, números y espacios.")
        if len(valor) > 100:
            raise ValueError("El titulo no puede superar los 100 caracteres.")
        self.__titulo = valor.strip()

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        """
        Establece la descripción después de validarla.

        Lanza ValueError si está vacía, contiene caracteres no permitidos
        o excede los 1000 caracteres.
        """
        if not valor or not isinstance(valor, str):
            raise ValueError("La descripcion no puede estar vacío.")
        if not re.match(r'^[A-Za-zÁáÉéÍíÓóÚúÜüÑñ0-9\s.,#\-\r\n]+$', valor):
            raise ValueError("La descripcion solo puede contener letras, " \
                            "números, espacios, puntos, comas, guiones " \
                            "y saltos de linea.")
        if len(valor) > 1000:
            raise ValueError("La descripcion no puede superar los 1000 caracteres.")
        self.__descripcion = valor.strip()

    @direccion.setter
    def direccion(self, valor: str) -> None:
        """
        Establece la dirección después de validarla.

        Lanza ValueError si está vacía, contiene caracteres no permitidos
        o excede los 200 caracteres.
        """
        if not valor or not isinstance(valor, str):
            raise ValueError("La direccion no puede estar vacío.")
        if not re.match(r'^[A-Za-zÁáÉéÍíÓóÚúÜüÑñ0-9\s.,#\-]+$', valor):
            raise ValueError("La direccion solo puede contener letras, " \
                            "números, espacios, puntos, comas y guiones.")
        if len(valor) > 200:
            raise ValueError("La direccion no puede superar los 200 caracteres.")
        self.__direccion = valor.strip()

    @precio_renta.setter
    def precio_renta(self, nuevo_precio: Union[int, float]) -> None:
        """
        Establece el precio de renta.

        Lanza TypeError si no es un número y ValueError si no es positivo.
        """
        if not isinstance(nuevo_precio, (int, float)):
            raise TypeError("El precio de renta debe ser un numero.")
        if nuevo_precio <= 0:
            raise ValueError("El precio debe ser positivo y mayor a 0.")
        self.__precio_renta = float(nuevo_precio)

    @m2_construccion.setter
    def m2_construccion(self, nuevo_m2_construccion: int) -> None:
        """
        Establece los metros cuadrados de construcción.

        Lanza TypeError si no es entero y ValueError si es negativo.
        """
        if not isinstance(nuevo_m2_construccion, int):
            raise TypeError("Los m2 de construccion deben ser un numero entero.")
        if nuevo_m2_construccion < 0:
            raise ValueError("Los m2 de construccion deben ser positivos.")
        self.__m2_construccion = nuevo_m2_construccion

    @recamaras.setter
    def recamaras(self, nuevo_recamaras: int) -> None:
        """
        Establece el número de recámaras.

        Lanza TypeError si no es entero y ValueError si es negativo.
        """
        if not isinstance(nuevo_recamaras, int):
            raise TypeError("El numero de recamaras debe ser un entero.")
        if nuevo_recamaras < 0:
            raise ValueError("El numero de recamaras no puede ser negativo.")
        self.__recamaras = nuevo_recamaras

    @banos.setter
    def banos(self, nuevo_banos: int) -> None:
        """
        Establece el número de baños completos.

        Lanza TypeError si no es entero y ValueError si es negativo.
        """
        if not isinstance(nuevo_banos, int):
            raise TypeError("El numero de baños debe ser un entero.")
        if nuevo_banos < 0:
            raise ValueError("El numero de baños no puede ser negativo.")
        self.__banos = nuevo_banos

    @medios_banos.setter
    def medios_banos(self, nuevo_medios_banos: int) -> None:
        """
        Establece el número de medios baños.

        Lanza TypeError si no es entero y ValueError si es negativo.
        """
        if not isinstance(nuevo_medios_banos, int):
            raise TypeError("El numero de medios baños debe ser un entero.")
        if nuevo_medios_banos < 0:
            raise ValueError("El numero de medios baños no puede ser negativo.")
        self.__medios_banos = nuevo_medios_banos

    @estacionamientos.setter
    def estacionamientos(self, nuevo_estacionamiento: int) -> None:
        """
        Establece el número de cajones de estacionamiento.

        Lanza TypeError si no es entero y ValueError si es negativo.
        """
        if not isinstance(nuevo_estacionamiento, int):
            raise TypeError("El numero de cajones de estacionamiento debe ser un entero.")
        if nuevo_estacionamiento < 0:
            raise ValueError("El numero de cajones de estacionamiento no puede ser negativo.")
        self.__estacionamientos = nuevo_estacionamiento

    @antiguedad.setter
    def antiguedad(self, nueva_antiguedad: int) -> None:
        """
        Establece la antigüedad en años.

        Lanza TypeError si no es entero y ValueError si es negativo.
        """
        if not isinstance(nueva_antiguedad, int):
            raise TypeError("La antigüedad debe ser un numero entero.")
        if nueva_antiguedad < 0:
            raise ValueError("La antigüedad no puede ser negativa.")
        self.__antiguedad = nueva_antiguedad

    @alberca.setter
    def alberca(self, valor: bool) -> None:
        """Establece si el inmueble tiene alberca (conversión a booleano)."""
        self.__alberca = bool(valor)

    @amueblado.setter
    def amueblado(self, valor: bool) -> None:
        """Establece si el inmueble está amueblado (conversión a booleano)."""
        self.__amueblado = bool(valor)

    @cocina_integral.setter
    def cocina_integral(self, valor: bool) -> None:
        """Establece si la cocina es integral (conversión a booleano)."""
        self.__cocina_integral = bool(valor)

    @cuarto_servicio.setter
    def cuarto_servicio(self, valor: bool) -> None:
        """Establece si tiene cuarto de servicio (conversión a booleano)."""
        self.__cuarto_servicio = bool(valor)

    @seguridad.setter
    def seguridad(self, valor: bool) -> None:
        """Establece si cuenta con seguridad privada (conversión a booleano)."""
        self.__seguridad = bool(valor)

    @staticmethod
    def _validar_fecha_publicacion(valor: Union[str, datetime, date]) -> date:
        """
        Convierte y valida la fecha de publicación.

        - Si es str, debe tener formato 'YYYY-MM-DD'.
        - No puede ser una fecha futura.
        Retorna un objeto date.
        """
        if isinstance(valor, str):
            fecha = datetime.strptime(valor, "%Y-%m-%d").date()
        elif isinstance(valor, datetime):
            fecha = valor.date()
        elif isinstance(valor, date):
            fecha = valor
        else:
            raise TypeError("La fecha de publicación debe ser un string (YYYY-MM-DD), datetime o date.")

        if fecha > date.today():
            raise ValueError("La fecha de publicación no puede ser futura.")
        return fecha

    def calcular_tarifa(self, dias: Optional[int] = None, meses: Optional[int] = None) -> float:
        """
        Calcula la tarifa de renta según la duración y el tipo de inmueble.
        Debe ser implementado por las subclases (Casa, Departamento).
        """
        raise NotImplementedError(
            "El método calcular_tarifa() debe ser implementado por las subclases"
        )

    def actualizar_inmueble(self) -> bool:
        """
        Actualiza todos los atributos editables de forma atómica.
        Debe ser implementado por las subclases (Casa, Departamento).
        """
        raise NotImplementedError(
            "El método actualizar_inmueble() debe ser implementado por las subclases"
        )

    def obtener_datos_inmueble(self) -> Dict[str, Any]:
        """
        Devuelve un diccionario con todos los datos públicos del inmueble
        """
        return {
            "id_inmueble": self.id_inmueble,
            "id_arrendador": self.id_arrendador,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "direccion": self.direccion,
            "precio_renta": self.precio_renta,
            "m2_construccion": self.m2_construccion,
            "recamaras": self.recamaras,
            "banos": self.banos,
            "medios_banos": self.medios_banos,
            "estacionamientos": self.estacionamientos,
            "antiguedad": self.antiguedad,
            "alberca": self.alberca,
            "amueblado": self.amueblado,
            "cocina_integral": self.cocina_integral,
            "cuarto_servicio": self.cuarto_servicio,
            "seguridad": self.seguridad,
            "fecha_publicacion": str(self.fecha_publicacion),
            "tipo_inmueble": self.tipo_inmueble.value,
            "disponible": self.disponible,
        }

    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> "Inmueble":
        """
        Construye una instancia genérica de Inmueble a partir de un diccionario.
        No discrimina entre subclases; esa responsabilidad corresponde a una
        fábrica externa o a los ``from_dict`` de las subclases concretas.
        """
        return cls(
            id_inmueble=datos["id_inmueble"],
            id_arrendador=datos["id_arrendador"],
            titulo=datos["titulo"],
            descripcion=datos["descripcion"],
            direccion=datos["direccion"],
            precio_renta=datos["precio_renta"],
            m2_construccion=datos["m2_construccion"],
            recamaras=datos["recamaras"],
            banos=datos["banos"],
            medios_banos=datos["medios_banos"],
            estacionamientos=datos["estacionamientos"],
            antiguedad=datos["antiguedad"],
            alberca=datos["alberca"],
            amueblado=datos["amueblado"],
            cocina_integral=datos["cocina_integral"],
            cuarto_servicio=datos["cuarto_servicio"],
            seguridad=datos["seguridad"],
            fecha_publicacion=datos["fecha_publicacion"],
            tipo_inmueble=datos["tipo_inmueble"],
            disponible=datos.get("disponible", datos.get("esta_disponible", True))
        )