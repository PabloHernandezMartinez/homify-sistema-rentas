from .inmueble import Inmueble, Tipo_Inmueble
from typing import Union, Dict, Any, Optional
from datetime import datetime, date

class Departamento(Inmueble):
    """
    Representa un inmueble tipo departamento para renta.

    Atributos adicionales:
        elevador (bool): Indica si el edificio cuenta con elevador.
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
                    elevador: bool,
                    fecha_publicacion: Union[str, datetime, date],
                    tipo_inmueble: Union[str, Tipo_Inmueble] = 'departamento',
                    disponible: bool = True) -> None:
        super().__init__(id_inmueble, id_arrendador, titulo, descripcion, direccion,
                            precio_renta, m2_construccion, recamaras, banos, medios_banos,
                            estacionamientos, antiguedad, alberca, amueblado, cocina_integral,
                            cuarto_servicio, seguridad, fecha_publicacion, 
                            tipo_inmueble = tipo_inmueble, disponible = disponible)
        self.__elevador = bool(elevador)

    @property
    def elevador(self) -> bool:
        """Indica si el departamento está en un edificio con elevador."""
        return self.__elevador

    @elevador.setter
    def elevador(self, valor: bool) -> None:
        """Establece si el edificio cuenta con elevador (conversión a booleano)."""
        self.__elevador = bool(valor)

    def calcular_tarifa(self, dias: Optional[int] = None, meses: Optional[int] = None) -> float:
        """
        Calcula la tarifa de renta para un departamento.

        - Si se renta por días, aplica un factor diario de 2.25 sobre el precio mensual.
        - Si se renta por meses, cobra el precio mensual por cada mes.
        """
        FACTOR_TARIFA = 2.25

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
                        nuevo_elevador: bool) -> bool:
        """
        Actualiza todos los atributos editables del departamento de forma atómica.
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
            'elevador': self.elevador,
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
            self.elevador = nuevo_elevador
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
            self.elevador = respaldo['elevador']
            raise

        return True

    def obtener_datos_inmueble(self) -> Dict[str, Any]:
        """Devuelve un diccionario con los datos del departamento, incluyendo los heredados."""
        datos = super().obtener_datos_inmueble()
        datos.update({
            "elevador": self.elevador
        })
        return datos

    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> "Departamento":
        """
        Construye una instancia de Departamento a partir de un diccionario.
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
            elevador=datos.get("elevador", False),
            fecha_publicacion=datos["fecha_publicacion"],
            tipo_inmueble=datos.get("tipo_inmueble", "departamento"),
            disponible=datos.get("disponible", datos.get("esta_disponible", True))
        )

    def __repr__(self) -> str:
        """Representación formal de la instancia."""
        return (f"Departamento(id={self.id_inmueble!r}, titulo={self.titulo!r}, "
                f"elevador={self.elevador}, disponible={self.disponible})")