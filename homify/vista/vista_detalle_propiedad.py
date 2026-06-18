import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict
from datetime import date, datetime
from controlador.controlador_cliente import ControladorCliente

class VistaDetallePropiedad:
    """
    Vista de detalle de una propiedad. Muestra la información completa del inmueble,
    permite abrir la ubicación en Google Maps y solicitar una renta.
    """

    def __init__(self, parent: tk.Frame, app: Any, propiedad: Dict[str, Any]) -> None:
        """
        Inicializa la vista de detalle.

        Args:
            parent: Frame contenedor donde se despliega esta vista.
            app: Instancia principal de la aplicación.
            propiedad: Diccionario con todos los datos del inmueble.
        """
        self.parent = parent
        self.app = app
        self.propiedad = propiedad
        self.controlador = ControladorCliente()

        tk.Button(parent, text="← Volver", command=self.volver).pack(anchor="w", padx=20, pady=10)

        frame_detalle = tk.Frame(parent, padx=40, pady=20)
        frame_detalle.pack(fill="both", expand=True)

        tk.Label(frame_detalle, text=self.propiedad.get("titulo", "Sin título"),
                    font=("Arial", 22, "bold")).pack(anchor="w")

        direccion_raw = self.propiedad.get("direccion", "No especificada")
        tk.Label(frame_detalle, text=f"Ubicación: {direccion_raw}",
                    font=("Arial", 12)).pack(anchor="w", pady=5)

        tipo = self.propiedad.get("tipo_inmueble", self.propiedad.get("tipo", "N/A"))
        tk.Label(frame_detalle, text=f"Tipo: {tipo.capitalize()}",
                    font=("Arial", 12)).pack(anchor="w")

        precio = self.propiedad.get("precio_renta", self.propiedad.get("precio", 0))
        tk.Label(frame_detalle, text=f"Precio mensual: ${float(precio):,.2f}",
                    font=("Arial", 16, "bold"), fg="#27ae60").pack(anchor="w", pady=15)

        descripcion = self.propiedad.get("descripcion", "Sin descripción.")
        tk.Label(frame_detalle, text="Descripción:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 0))
        tk.Label(frame_detalle, text=descripcion,
                    wraplength=600, justify="left").pack(anchor="w", pady=5)

        self._mostrar_caracteristicas(frame_detalle)

        self.btn_rentar = tk.Button(frame_detalle, text="Solicitar Renta", bg="#3498db", fg="white",
                                    font=("Arial", 12, "bold"), width=20, height=2,
                                    command=self.solicitar_renta)
        self.btn_rentar.pack(pady=30)

    def _mostrar_caracteristicas(self, frame: tk.Frame) -> None:
        """Muestra características relevantes del inmueble (recámaras, baños, estacionamientos)."""
        linea = []
        if self.propiedad.get("recamaras"):
            linea.append(f"{self.propiedad['recamaras']} rec.")
        if self.propiedad.get("banos"):
            linea.append(f"{self.propiedad['banos']} baños")
        if self.propiedad.get("estacionamientos"):
            linea.append(f"{self.propiedad['estacionamientos']} est.")
        if linea:
            tk.Label(frame, text=" | ".join(linea), font=("Arial", 11), fg="#555").pack(anchor="w", pady=(5, 0))

    def solicitar_renta(self) -> None:
        """Abre ventana para capturar duración (días o meses) y método de pago, y registra la renta."""
        id_usuario = self.app.usuario_actual.get("id_usuario")
        id_propiedad = self.propiedad.get("id_inmueble")
        id_arrendador = self.propiedad.get("id_arrendador")
        precio = self.propiedad.get("precio_renta", self.propiedad.get("precio", 0))

        win = tk.Toplevel(self.parent)
        win.title("Confirmar Renta")
        win.geometry("350x300")
        win.resizable(False, False)

        tk.Label(win, text="Fecha de inicio (AAAA-MM-DD):", font=("Arial", 11)).pack(pady=(15, 5))
        ent_fecha_inicio = tk.Entry(win, width=15)
        ent_fecha_inicio.insert(0, date.today().isoformat())
        ent_fecha_inicio.pack()

        tk.Label(win, text="Duración:", font=("Arial", 11)).pack(pady=(15, 5))
        frame_duracion = tk.Frame(win)
        frame_duracion.pack()
        ent_cantidad = tk.Entry(frame_duracion, width=8)
        ent_cantidad.insert(0, "6")
        ent_cantidad.pack(side="left", padx=5)
        var_tipo = tk.StringVar(value="meses")
        combo_tipo = ttk.Combobox(frame_duracion, textvariable=var_tipo, values=["dias", "meses"],
                                    state="readonly", width=8)
        combo_tipo.pack(side="left")

        tk.Label(win, text="Método de pago:", font=("Arial", 11)).pack(pady=(10, 5))
        metodos = ["efectivo", "transferencia", "tarjeta"]
        var_metodo = tk.StringVar(value=metodos[0])
        combo_metodo = ttk.Combobox(win, textvariable=var_metodo, values=metodos, state="readonly")
        combo_metodo.pack()

        def confirmar() -> None:
            """Valida los datos de la renta y la registra mediante el controlador."""
            fecha_str = ent_fecha_inicio.get().strip()
            try:
                fecha_inicio = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                if fecha_inicio < date.today():
                    messagebox.showerror("Error", "La fecha de inicio no puede ser anterior a hoy.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use AAAA-MM-DD.")
                return
            
            cantidad_str = ent_cantidad.get().strip()
            if not cantidad_str.isdigit() or int(cantidad_str) <= 0:
                messagebox.showerror("Error", "Ingrese un número válido de días o meses.")
                return
            cantidad = int(cantidad_str)
            tipo_duracion = var_tipo.get()
            metodo = var_metodo.get()

            exito, msg = self.controlador.rentar_propiedad(
                id_cliente=id_usuario,
                id_inmueble=id_propiedad,
                id_arrendador=id_arrendador,
                precio_mensual=float(precio),
                dias_contrato=cantidad if tipo_duracion == "dias" else None,
                meses_contrato=cantidad if tipo_duracion == "meses" else None,
                metodo_pago=metodo,
                fecha_inicio=fecha_inicio
            )
            if exito:
                messagebox.showinfo("Éxito", msg)
                win.destroy()
                self.volver()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(win, text="Confirmar", command=confirmar, bg="#2ecc71", fg="white", width=15).pack(pady=20)

    def volver(self) -> None:
        """Regresa a la vista principal del cliente."""
        from vista.vista_cliente import VistaCliente
        self.app.cambiar_vista(VistaCliente)