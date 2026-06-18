from .inmueble import Inmueble, Tipo_Inmueble
from typing import Union, Dict, Any, Optional
from datetime import datetime, date

class Casa(Inmueble):
    """
    Representa un inmueble tipo casa para renta.

    Atributos adicionales:
        m2_terreno (int): Metros cuadrados de terreno (>= 0).
        patio (bool): Indica si tiene patio.
    """
    
    def __init__(self,
                    id_inmueble: str,
                    id_arrendador: str,
                    titulo: str,
                    descripcion: str,
                    direccion: str,
                    precio_renta: float,
                    m2_terreno: int,
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
                    patio: bool,
                    fecha_publicacion: Union[str, datetime, date],
                    tipo_inmueble: Union[str, Tipo_Inmueble] = 'casa',
                    disponible: bool = True) -> None:
        super().__init__(id_inmueble, id_arrendador, titulo, descripcion, direccion,
                            precio_renta, m2_construccion, recamaras, banos, medios_banos,
                            estacionamientos, antiguedad, alberca, amueblado, cocina_integral,
                            cuarto_servicio, seguridad, fecha_publicacion, 
                            tipo_inmueble = tipo_inmueble, disponible = disponible)
        self.m2_terreno = m2_terreno
        self.__patio = bool(patio)

    @property
    def m2_terreno(self) -> int:
        """Metros cuadrados de terreno."""
        return self.__m2_terreno

    @property
    def patio(self) -> bool:
        """Indica si la casa tiene patio."""
        return self.__patio

    @m2_terreno.setter
    def m2_terreno(self, nuevo_m2_terreno: int) -> None:
        """
        Establece los metros cuadrados de terreno.

        Lanza TypeError si no es entero y ValueError si es negativo.
        """
        if not isinstance(nuevo_m2_terreno, int):
            raise TypeError("Los m2 de terreno deben ser un número entero.")
        if nuevo_m2_terreno < 0:
            raise ValueError("Los m2 de terreno deben ser positivos.")
        self.__m2_terreno = nuevo_m2_terreno

    @patio.setter
    def patio(self, valor: bool) -> None:
        """Establece si la casa tiene patio (conversión a booleano)."""
        self.__patio = bool(valor)

    def calcular_tarifa(self, dias: Optional[int] = None, meses: Optional[int] = None) -> float:
        """
        Calcula la tarifa de renta para una casa.

        - Si se renta por días, aplica un factor diario de 1.5 sobre el precio mensual.
        - Si se renta por meses, cobra el precio mensual por cada mes.
        """
        FACTOR_TARIFA = 1.5

        if dias is not None and meses is not None:
            raise ValueError("Solo se puede especificar días o meses, no ambos.")
        if dias is not None:
            if not isinstance(dias, int) or dias <= 0:
                raise ValueError("Debe rentarse al menos 1 día.")
            return round((self.precio_renta / 30) * FACTOR_TARIFA * dias, 0)
        elif meses is not None:
            if not isinstance(meses, int) or meses <= 0:
                raise ValueError("Debe rentarse al menos 1 mes.")
            return round(self.precio_renta * meses, 0)
        else:
            raise ValueError("Debe especificar días o meses para calcular la tarifa.")

    def actualizar_inmueble(self,
                        nuevo_titulo: str,
                        nuevo_descripcion: str,
                        nuevo_direccion: str,
                        nuevo_precio_renta: float,
                        nuevo_m2_construccion: int,
                        nuevo_recamaras: int,
                        nuevo_medios_banos: int,
                        nuevo_banos: int,
                        nuevo_estacionamiento: int,
                        nuevo_antiguedad: int,
                        nuevo_alberca: bool,
                        nuevo_amueblado: bool,
                        nuevo_cocina_integral: bool,
                        nuevo_cuarto_servicio: bool,
                        nuevo_seguridad: bool,
                        nuevo_m2_terreno: int,
                        nuevo_patio: bool) -> bool:
        """
        Actualiza todos los atributos editables de la casa de forma atómica.
        Si cualquier validación falla, se revierten todos los cambios.
        """
        respaldo = {
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'direccion': self.direccion,
            'precio_renta': self.precio_renta,
            'm2_construccion': self.m2_construccion,
            'recamaras': self.recamaras,
            'banos': self.banos,
            'medios_banos': self.medios_banos,
            'estacionamientos': self.estacionamientos,
            'antiguedad': self.antiguedad,
            'alberca': self.alberca,
            'amueblado': self.amueblado,
            'cocina_integral': self.cocina_integral,
            'cuarto_servicio': self.cuarto_servicio,
            'seguridad': self.seguridad,
            'm2_terreno': self.m2_terreno,
            'patio': self.patio,
        }

        try:
            self.titulo = nuevo_titulo
            self.descripcion = nuevo_descripcion
            self.direccion = nuevo_direccion
            self.precio_renta = nuevo_precio_renta
            self.m2_construccion = nuevo_m2_construccion
            self.recamaras = nuevo_recamaras
            self.banos = nuevo_banos
            self.medios_banos = nuevo_medios_banos
            self.estacionamientos = nuevo_estacionamiento
            self.antiguedad = nuevo_antiguedad
            self.alberca = nuevo_alberca
            self.amueblado = nuevo_amueblado
            self.cocina_integral = nuevo_cocina_integral
            self.cuarto_servicio = nuevo_cuarto_servicio
            self.seguridad = nuevo_seguridad
            self.m2_terreno = nuevo_m2_terreno
            self.patio = nuevo_patio
        except Exception:
            self.titulo = respaldo['titulo']
            self.descripcion = respaldo['descripcion']
            self.direccion = respaldo['direccion']
            self.precio_renta = respaldo['precio_renta']
            self.m2_construccion = respaldo['m2_construccion']
            self.recamaras = respaldo['recamaras']
            self.banos = respaldo['banos']
            self.medios_banos = respaldo['medios_banos']
            self.estacionamientos = respaldo['estacionamientos']
            self.antiguedad = respaldo['antiguedad']
            self.alberca = respaldo['alberca']
            self.amueblado = respaldo['amueblado']
            self.cocina_integral = respaldo['cocina_integral']
            self.cuarto_servicio = respaldo['cuarto_servicio']
            self.seguridad = respaldo['seguridad']
            self.m2_terreno = respaldo['m2_terreno']
            self.patio = respaldo['patio']
            raise

        return True

    def obtener_datos_inmueble(self) -> Dict[str, Any]:
        """Devuelve un diccionario con los datos de la casa, incluyendo los heredados."""
        datos = super().obtener_datos_inmueble()
        datos.update({
            "m2_terreno": self.m2_terreno,
            "patio": self.patio
        })
        return datos

    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> "Casa":
        """
        Construye una instancia de Casa a partir de un diccionario.
        """
        return cls(
            id_inmueble=datos["id_inmueble"],
            id_arrendador=datos["id_arrendador"],
            titulo=datos["titulo"],
            descripcion=datos["descripcion"],
            direccion=datos["direccion"],
            precio_renta=datos["precio_renta"],
            m2_terreno=datos.get("m2_terreno", 0),
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
            patio=datos.get("patio", False),
            fecha_publicacion=datos["fecha_publicacion"],
            tipo_inmueble=datos.get("tipo_inmueble", "casa"),
            disponible=datos.get("disponible", datos.get("esta_disponible", True))
        )

    def __repr__(self) -> str:
        """Representación formal de la instancia."""
        return (f"Casa(id={self.id_inmueble!r}, titulo={self.titulo!r}, "
                f"m2_terreno={self.m2_terreno}, disponible={self.disponible})")