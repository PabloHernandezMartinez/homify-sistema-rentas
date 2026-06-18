from datetime import datetime, date
from typing import Union, Dict, Any, Optional
from .enums import Metodo_Pago, Estado_Renta

class Renta:
    """
    Representa una renta (contrato) entre un cliente y un arrendador sobre un inmueble.

    Atributos:
        id_renta (str): Identificador único de la renta.
        id_cliente (str): Identificador del cliente que renta.
        id_inmueble (str): Identificador del inmueble rentado.
        id_arrendador (str): Identificador del arrendador propietario.
        fecha_inicio (date): Fecha de inicio del contrato (no anterior a hoy).
        fecha_fin (date): Fecha de finalización pactada (no anterior a hoy ni a fecha_inicio).
        precio_mensual (float): Precio de renta mensual pactado.
        total (float): Monto total calculado de la renta.
        deposito (float): Depósito o garantía entregado.
        metodo_pago (Metodo_Pago): Método de pago acordado (tarjeta, transferencia, efectivo).
        estado_renta (Estado_Renta): Estado actual de la renta (activa, finalizada, cancelada).
        fecha_fin_real (date or None): Fecha real en que finalizó o se canceló la renta.
        motivo_cancelacion (str or None): Motivo de la cancelación, si la hubo.

    Nota:
        Los métodos ``finalizar_renta()`` y ``cancelar_renta()`` permiten cambiar
        el estado de la renta y registrar los datos correspondientes.
    """

    def __init__(self,
                    id_renta: str,
                    id_cliente: str,
                    id_inmueble: str,
                    id_arrendador: str,
                    fecha_inicio: Union[str, datetime, date],
                    fecha_fin: Union[str, datetime, date],
                    precio_mensual: float,
                    total: float,
                    deposito: float,
                    metodo_pago: Union[str, Metodo_Pago]) -> None:
        self.__id_renta = str(id_renta)
        self.__id_cliente = str(id_cliente)
        self.__id_inmueble = str(id_inmueble)
        self.__id_arrendador = str(id_arrendador)
        self.__fecha_inicio = self._validar_fecha_inicio(fecha_inicio)
        self.__fecha_fin = self._validar_fecha_fin(fecha_fin)
        self.precio_mensual = float(precio_mensual)
        self.total = float(total)
        self.deposito = float(deposito)
        self.metodo_pago = metodo_pago
        self.__estado_renta = Estado_Renta.ACTIVA
        self.__fecha_fin_real: Optional[date] = None
        self.__motivo_cancelacion: Optional[str] = None

    @property
    def id_renta(self) -> str:
        """Identificador único de la renta."""
        return self.__id_renta

    @property
    def id_cliente(self) -> str:
        """Identificador del cliente que renta."""
        return self.__id_cliente

    @property
    def id_inmueble(self) -> str:
        """Identificador del inmueble rentado."""
        return self.__id_inmueble

    @property
    def id_arrendador(self) -> str:
        """Identificador del arrendador propietario."""
        return self.__id_arrendador

    @property
    def fecha_inicio(self) -> date:
        """Fecha de inicio del contrato (no anterior a hoy)."""
        return self.__fecha_inicio

    @property
    def fecha_fin(self) -> date:
        """Fecha de finalización pactada (no anterior a hoy ni a fecha de inicio)."""
        return self.__fecha_fin

    @property
    def estado_renta(self) -> Estado_Renta:
        """Estado actual de la renta."""
        return self.__estado_renta

    @property
    def fecha_fin_real(self) -> Optional[date]:
        """Fecha real en que finalizó o se canceló la renta (None si está activa)."""
        return self.__fecha_fin_real

    @property
    def motivo_cancelacion(self) -> Optional[str]:
        """Motivo de la cancelación (None si no ha sido cancelada)."""
        return self.__motivo_cancelacion

    @property
    def renta_activa(self) -> bool:
        """True si la renta está activa."""
        return self.__estado_renta == Estado_Renta.ACTIVA

    @property
    def renta_finalizada(self) -> bool:
        """True si la renta ha sido finalizada."""
        return self.__estado_renta == Estado_Renta.FINALIZADA

    @property
    def renta_cancelada(self) -> bool:
        """True si la renta ha sido cancelada."""
        return self.__estado_renta == Estado_Renta.CANCELADA

    @property
    def precio_mensual(self) -> float:
        """Precio de renta mensual pactado."""
        return self.__precio_mensual

    @precio_mensual.setter
    def precio_mensual(self, nuevo_precio: Union[int, float]) -> None:
        """
        Establece el precio mensual.

        Lanza TypeError si no es un número y ValueError si no es positivo.
        """
        if not isinstance(nuevo_precio, (int, float)):
            raise TypeError("El precio de renta mensual debe ser un número.")
        if nuevo_precio <= 0:
            raise ValueError("El precio de renta mensual debe ser positivo y mayor a 0.")
        self.__precio_mensual = float(nuevo_precio)

    @property
    def total(self) -> float:
        """Monto total calculado de la renta."""
        return self.__total

    @total.setter
    def total(self, nuevo_total: Union[int, float]) -> None:
        """
        Establece el monto total de la renta.

        Lanza TypeError si no es un número y ValueError si no es positivo.
        """
        if not isinstance(nuevo_total, (int, float)):
            raise TypeError("El precio total de renta debe ser un número.")
        if nuevo_total <= 0:
            raise ValueError("El precio total de renta debe ser positivo y mayor a 0.")
        self.__total = float(nuevo_total)

    @property
    def deposito(self) -> float:
        """Depósito o garantía entregado."""
        return self.__deposito

    @deposito.setter
    def deposito(self, nuevo_deposito: Union[int, float]) -> None:
        """
        Establece el depósito.

        Lanza TypeError si no es un número y ValueError si no es positivo.
        """
        if not isinstance(nuevo_deposito, (int, float)):
            raise TypeError("El depósito debe ser un número.")
        if nuevo_deposito <= 0:
            raise ValueError("El depósito debe ser positivo y mayor a 0.")
        self.__deposito = float(nuevo_deposito)

    @property
    def metodo_pago(self) -> Metodo_Pago:
        """Método de pago acordado."""
        return self.__metodo_pago

    @metodo_pago.setter
    def metodo_pago(self, nuevo_metodo_pago: Union[str, Metodo_Pago]) -> None:
        """
        Asigna el método de pago aceptando string o Enum Metodo_Pago.

        Lanza ValueError si el valor no corresponde a un método válido.
        """
        if isinstance(nuevo_metodo_pago, Metodo_Pago):
            self.__metodo_pago = nuevo_metodo_pago
        elif isinstance(nuevo_metodo_pago, str):
            self.__metodo_pago = Metodo_Pago(nuevo_metodo_pago)
        else:
            raise ValueError("Método de pago no válido. Debe ser 'tarjeta', 'transferencia' o 'efectivo'.")

    @estado_renta.setter
    def estado_renta(self, nuevo_estado: Union[str, Estado_Renta]) -> None:
        """
        Cambia el estado de la renta aceptando string o Enum Estado_Renta.

        Lanza ValueError si el estado no es válido.
        """
        if isinstance(nuevo_estado, Estado_Renta):
            self.__estado_renta = nuevo_estado
        elif isinstance(nuevo_estado, str):
            self.__estado_renta = Estado_Renta(nuevo_estado)
        else:
            raise ValueError("Estado no válido. Debe ser 'activa', 'finalizada' o 'cancelada'.")

    @staticmethod
    def _validar_fecha_inicio(valor: Union[str, datetime, date]) -> date:
        """
        Convierte y valida la fecha de inicio.

        - Si es str, debe tener formato 'YYYY-MM-DD'.
        - No puede ser una fecha anterior a hoy.
        Retorna un objeto date.
        """
        if isinstance(valor, str):
            fecha = datetime.strptime(valor, "%Y-%m-%d").date()
        elif isinstance(valor, datetime):
            fecha = valor.date()
        elif isinstance(valor, date):
            fecha = valor
        else:
            raise TypeError("La fecha de inicio debe ser un string (YYYY-MM-DD), datetime o date.")

        if fecha < date.today():
            raise ValueError("La fecha de inicio no puede ser anterior a hoy.")
        return fecha

    def _validar_fecha_fin(self, valor: Union[str, datetime, date]) -> date:
        """
        Convierte y valida la fecha de fin.

        - Si es str, debe tener formato 'YYYY-MM-DD'.
        - No puede ser anterior a hoy.
        - No puede ser anterior a la fecha de inicio.
        Retorna un objeto date.
        """
        if isinstance(valor, str):
            fecha = datetime.strptime(valor, "%Y-%m-%d").date()
        elif isinstance(valor, datetime):
            fecha = valor.date()
        elif isinstance(valor, date):
            fecha = valor
        else:
            raise TypeError("La fecha de fin debe ser un string (YYYY-MM-DD), datetime o date.")

        if fecha < date.today():
            raise ValueError("La fecha de fin no puede ser anterior a hoy.")
        if fecha < self.fecha_inicio:
            raise ValueError("La fecha de fin no puede ser anterior a la de inicio.")
        return fecha

    def finalizar_renta(self, fecha_finalizacion: Union[str, datetime, date]) -> None:
        """
        Finaliza la renta si está activa, registrando la fecha real de fin.

        Lanza RuntimeError si la renta no está activa.
        Lanza ValueError si la fecha es posterior al a de fin pactada.
        """
        if not self.renta_activa:
            raise RuntimeError("La renta ya fue finalizada o cancelada.")
        fecha = self._validar_fecha_fin(fecha_finalizacion)
        if fecha > self.fecha_fin:
            raise ValueError("La fecha de finalización no puede ser posterior a la fecha de fin pactada.")
        self.__fecha_fin_real = fecha
        self.__estado_renta = Estado_Renta.FINALIZADA

    def cancelar_renta(self, motivo: str) -> None:
        """
        Cancela la renta si está activa, registrando la fecha actual como fin real y el motivo.

        Lanza RuntimeError si la renta no está activa.
        """
        if not self.renta_activa:
            raise RuntimeError("La renta ya fue finalizada o cancelada.")
        self.__fecha_fin_real = date.today()
        self.__motivo_cancelacion = motivo
        self.__estado_renta = Estado_Renta.CANCELADA

    def obtener_datos_renta(self) -> Dict[str, Any]:
        """Devuelve un diccionario con todos los datos públicos de la renta."""
        return {
            "id_renta": self.id_renta,
            "id_cliente": self.id_cliente,
            "id_inmueble": self.id_inmueble,
            "id_arrendador": self.id_arrendador,
            "fecha_inicio": str(self.fecha_inicio),
            "fecha_fin": str(self.fecha_fin),
            "precio_mensual": self.precio_mensual,
            "total": self.total,
            "deposito": self.deposito,
            "metodo_pago": self.metodo_pago.value,
            "estado": self.estado_renta.value,
            "fecha_fin_real": str(self.fecha_fin_real) if self.fecha_fin_real else None,
            "motivo_cancelacion": self.motivo_cancelacion,
        }

    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> "Renta":
        """
        Construye una instancia de Renta a partir de un diccionario.
        Omite la validación de reglas complejas (fechas coherentes) porque
        los datos ya provienen de la base de datos y se asumen consistentes.
        """
        instance = cls.__new__(cls)
        instance.__id_renta = str(datos["id_renta"])
        instance.__id_cliente = str(datos["id_cliente"])
        instance.__id_inmueble = str(datos["id_inmueble"])
        instance.__id_arrendador = str(datos["id_arrendador"])
        instance.__fecha_inicio = cls._parse_fecha(datos["fecha_inicio"])
        instance.__fecha_fin = cls._parse_fecha(datos["fecha_fin"])
        instance.__precio_mensual = float(datos["precio_mensual"])
        instance.__total = float(datos["total"])
        instance.__deposito = float(datos["deposito"])
        instance.__metodo_pago = Metodo_Pago(datos["metodo_pago"]) if "metodo_pago" in datos else Metodo_Pago.EFECTIVO
        instance.__estado_renta = Estado_Renta(datos["estado"]) if "estado" in datos else Estado_Renta.ACTIVA
        instance.__fecha_fin_real = cls._parse_fecha(datos["fecha_fin_real"]) if datos.get("fecha_fin_real") else None
        instance.__motivo_cancelacion = datos.get("motivo_cancelacion")
        return instance

    @staticmethod
    def _parse_fecha(valor: Union[str, datetime, date]) -> date:
        """Convierte un valor de fecha (str, datetime o date) a date."""
        if isinstance(valor, str):
            return datetime.strptime(valor, "%Y-%m-%d").date()
        if isinstance(valor, datetime):
            return valor.date()
        return valor

    def __repr__(self) -> str:
        """Representación formal de la instancia."""
        return (f"Renta(id={self.id_renta!r}, inmueble={self.id_inmueble!r}, "
                f"cliente={self.id_cliente!r}, estado={self.estado_renta.value})")