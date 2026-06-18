import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from typing import Any, Dict, Optional
from controlador.controlador_cliente import ControladorCliente
from vista.vista_detalle_propiedad import VistaDetallePropiedad

class VistaCliente:
    """
    Panel principal del cliente. Muestra inmuebles disponibles con paginación,
    permite ver el detalle de una propiedad, consultar sus rentas y gestionar su perfil.
    """

    def __init__(self, parent: tk.Frame, app: Any) -> None:
        """
        Inicializa la vista del cliente.

        Args:
            parent: Frame contenedor donde se despliega esta vista.
            app: Instancia principal de la aplicación (AplicacionPrincipal).
        """
        self.parent = parent
        self.app = app
        self.controlador = ControladorCliente()
        self.usuario = self.app.usuario_actual
        self.pagina_actual = 0
        self.limite = 20
        self.total_paginas = 1

        frame_header = tk.Frame(parent)
        frame_header.pack(fill="x", padx=20, pady=10)

        nombre_mostrar = self.usuario.get("nombre_completo", "Usuario")

        tk.Label(
            frame_header, text=f"Panel del Cliente | {nombre_mostrar}",
            font=("Arial", 14, "bold")
        ).pack(side="left")

        tk.Button(
            frame_header, text="Mi Perfil", bg="#2c3e50", fg="white",
            command=self.abrir_perfil
        ).pack(side="right", padx=5)
        tk.Button(
            frame_header, text="Cerrar Sesión", bg="#e74c3c", fg="white",
            command=self.cerrar_sesion
        ).pack(side="right", padx=5)

        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True)

        self.tab_explorar = tk.Frame(self.notebook, bg="white")
        self.tab_rentas = tk.Frame(self.notebook, bg="white")

        self.notebook.add(self.tab_explorar, text="Explorar Propiedades")
        self.notebook.add(self.tab_rentas, text="Mis Rentas")

        self._construir_pestana_explorar()
        self._construir_pestana_rentas()
        self.cargar_rentas()
        self.notebook.bind("<<NotebookTabChanged>>", self._al_cambiar_pestana)

        self.cargar_datos()

    def _construir_pestana_explorar(self) -> None:
        """Construye la pestaña de búsqueda de propiedades con scroll invisible y filtros."""
        frame_filtros = tk.Frame(self.tab_explorar, bg="white")
        frame_filtros.pack(fill="x", padx=20, pady=(10, 5))

        tk.Label(frame_filtros, text="Tipo:", bg="white").pack(side="left")
        self.cb_tipo = ttk.Combobox(frame_filtros, values=["Todos", "casa", "departamento"],
                                    state="readonly", width=12)
        self.cb_tipo.set("Todos")
        self.cb_tipo.pack(side="left", padx=5)

        tk.Label(frame_filtros, text="Precio min:", bg="white").pack(side="left", padx=(15, 0))
        self.ent_precio_min = tk.Entry(frame_filtros, width=8)
        self.ent_precio_min.pack(side="left", padx=2)

        tk.Label(frame_filtros, text="Precio max:", bg="white").pack(side="left", padx=(10, 0))
        self.ent_precio_max = tk.Entry(frame_filtros, width=8)
        self.ent_precio_max.pack(side="left", padx=2)

        tk.Label(frame_filtros, text="Recámaras:", bg="white").pack(side="left", padx=(15, 0))
        self.ent_recamaras = tk.Entry(frame_filtros, width=5)
        self.ent_recamaras.pack(side="left", padx=2)

        tk.Button(
            frame_filtros, text="Buscar", bg="#3498db", fg="white",
            command=self.buscar_con_filtros
        ).pack(side="left", padx=(15, 5))

        tk.Button(
            frame_filtros, text="Limpiar", bg="#95a5a6", fg="white",
            command=self.limpiar_filtros
        ).pack(side="left", padx=5)

        frame_canvas = tk.Frame(self.tab_explorar, bg="white")
        frame_canvas.pack(fill="both", expand=True, padx=20, pady=(5, 0))

        self.canvas = tk.Canvas(frame_canvas, bg="white", highlightthickness=0)
        self.scroll_y = tk.Scrollbar(
            frame_canvas, orient="vertical", command=self.canvas.yview,
            bg="white", troughcolor="white", activebackground="white",
            highlightbackground="white", highlightcolor="white"
        )
        self.frame_lista = tk.Frame(self.canvas, bg="white")
        self.frame_lista.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.frame_lista, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        def _on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        self.canvas.bind("<Configure>", _on_canvas_configure)

        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        self.frame_lista.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll_y.pack(side="right", fill="y")

        frame_paginacion = tk.Frame(self.tab_explorar, bg="white")
        frame_paginacion.pack(fill="x", pady=(5, 10))
        self.btn_ant = tk.Button(frame_paginacion, text="Anterior", command=self.ir_atras)
        self.btn_ant.pack(side="left", padx=20)
        self.lbl_pag = tk.Label(frame_paginacion, text="Página 1 de 1", bg="white")
        self.lbl_pag.pack(side="left", expand=True)
        self.btn_sig = tk.Button(frame_paginacion, text="Siguiente", command=self.ir_adelante)
        self.btn_sig.pack(side="right", padx=20)

    def _construir_pestana_rentas(self) -> None:
        """Construye la pestaña de historial de rentas del cliente."""
        frame_tabla = tk.Frame(self.tab_rentas)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal")
        scroll_x.pack(side="bottom", fill="x")

        columnas = ("id_renta", "inmueble", "arrendador", "fecha_inicio", "fecha_fin", "estado", "precio_mensual", "total", "id_inmueble")
        
        self.tree_rentas = ttk.Treeview(
            frame_tabla, 
            columns=columnas, 
            show="headings", 
            height=15,
            xscrollcommand=scroll_x.set
        )
        scroll_x.config(command=self.tree_rentas.xview)

        self.tree_rentas.heading("id_renta", text="ID Renta")
        self.tree_rentas.heading("inmueble", text="Inmueble")
        self.tree_rentas.heading("arrendador", text="Arrendador")
        self.tree_rentas.heading("fecha_inicio", text="Inicio")
        self.tree_rentas.heading("fecha_fin", text="Fin")
        self.tree_rentas.heading("estado", text="Estado")
        self.tree_rentas.heading("precio_mensual", text="Precio/mes")
        self.tree_rentas.heading("total", text="Total")

        anchos_columnas = {
            "id_renta": 150, 
            "inmueble": 280, 
            "arrendador": 200, 
            "fecha_inicio": 130, 
            "fecha_fin": 130, 
            "estado": 120, 
            "precio_mensual": 130, 
            "total": 180,
            "id_inmueble": 0
        }
        
        for col in columnas:
            self.tree_rentas.column(col, width=anchos_columnas[col], minwidth=anchos_columnas[col], stretch=False)

        self.tree_rentas.pack(side="top", fill="both", expand=True)

        frame_acciones = tk.Frame(self.tab_rentas, bg="white")
        frame_acciones.pack(fill="x", padx=20, pady=(0, 10))
        tk.Button(
            frame_acciones, text="Refrescar", bg="#3498db", fg="white",
            command=self.cargar_rentas
        ).pack(side="left", padx=5)
        tk.Button(
            frame_acciones, text="Cancelar Renta", bg="#e74c3c", fg="white",
            command=self.cancelar_renta_desde_historial
        ).pack(side="left", padx=5)

    def _al_cambiar_pestana(self, event: tk.Event) -> None:
        """Recarga las rentas cuando el usuario selecciona la pestaña Mis Rentas."""
        pestana_actual = self.notebook.index(self.notebook.select())
        if pestana_actual == 1:
            self.cargar_rentas()

    def _leer_filtros(self) -> Optional[Dict[str, Any]]:
        """Construye el diccionario de filtros a partir de los campos de la interfaz."""
        tipo = self.cb_tipo.get()
        precio_min = self.ent_precio_min.get().strip()
        precio_max = self.ent_precio_max.get().strip()
        recamaras = self.ent_recamaras.get().strip()

        filtros = {}
        if tipo and tipo != "Todos":
            filtros["tipo"] = tipo
        if precio_min:
            try:
                filtros["precio_min"] = float(precio_min)
            except ValueError:
                messagebox.showerror("Error", "Precio mínimo debe ser un número.")
                return None
        if precio_max:
            try:
                filtros["precio_max"] = float(precio_max)
            except ValueError:
                messagebox.showerror("Error", "Precio máximo debe ser un número.")
                return None
        if recamaras:
            try:
                filtros["recamaras"] = int(recamaras)
            except ValueError:
                messagebox.showerror("Error", "Recámaras debe ser un número entero.")
                return None
        return filtros if filtros else None

    def buscar_con_filtros(self) -> None:
        """Aplica los filtros y recarga la primera página de resultados."""
        self.pagina_actual = 0
        self.cargar_datos(con_filtros=True)

    def limpiar_filtros(self) -> None:
        """Limpia todos los campos de filtro y recarga sin filtros."""
        self.cb_tipo.set("Todos")
        self.ent_precio_min.delete(0, tk.END)
        self.ent_precio_max.delete(0, tk.END)
        self.ent_recamaras.delete(0, tk.END)
        self.pagina_actual = 0
        self.cargar_datos(con_filtros=False)

    def cargar_datos(self, con_filtros: bool = False) -> None:
        """Carga la lista de inmuebles disponibles (pestaña explorar)."""
        if con_filtros:
            filtros = self._leer_filtros()
            if filtros is None:   # hubo error al parsear
                return
            exito, resultado = self.controlador.buscar_inmuebles(
                pagina=self.pagina_actual, limite=self.limite, filtros=filtros
            )
        else:
            exito, resultado = self.controlador.buscar_inmuebles(
                pagina=self.pagina_actual, limite=self.limite
            )

        if exito:
            datos = resultado["datos"]
            total = resultado["total"]
            self.total_paginas = max(
                1,
                (total // self.limite) + (1 if total % self.limite > 0 else 0)
            )
            for widget in self.frame_lista.winfo_children():
                widget.destroy()
            if datos:
                for inmueble in datos:
                    self.crear_tarjeta(inmueble)
            else:
                tk.Label(
                    self.frame_lista, text="No se encontraron propiedades en esta página.",
                    fg="gray", bg="white"
                ).pack(pady=30)
            self.lbl_pag.config(
                text=f"Página {self.pagina_actual + 1} de {self.total_paginas}"
            )
        else:
            messagebox.showinfo("Información", resultado)
        self._actualizar_botones_navegacion()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _actualizar_botones_navegacion(self) -> None:
        """Habilita o deshabilita los botones de paginación."""
        self.btn_ant.config(state="normal" if self.pagina_actual > 0 else "disabled")
        self.btn_sig.config(
            state="normal" if self.pagina_actual < self.total_paginas - 1 else "disabled"
        )

    def ir_adelante(self) -> None:
        if self.pagina_actual < self.total_paginas - 1:
            self.pagina_actual += 1
            self.cargar_datos()

    def ir_atras(self) -> None:
        if self.pagina_actual > 0:
            self.pagina_actual -= 1
            self.cargar_datos()

    def crear_tarjeta(self, propiedad: Dict[str, Any]) -> None:
        """Crea una tarjeta enriquecida para un inmueble."""
        card = tk.Frame(self.frame_lista, bd=1, relief="raised", padx=15, pady=10, bg="white")
        card.pack(fill="x", pady=5, padx=5)

        titulo = propiedad.get("titulo", "Sin título")
        precio = propiedad.get("precio", 0)
        tipo = propiedad.get("tipo", "N/A")
        direccion = propiedad.get("direccion", "")
        m2 = propiedad.get("m2", 0)
        recamaras = propiedad.get("recamaras", "?")
        banos = propiedad.get("banos", "?")
        estacionamientos = propiedad.get("estacionamientos", "?")

        tk.Label(card, text=titulo, font=("Arial", 12, "bold"), bg="white").pack(anchor="w")
        tk.Label(card, text=f"Precio: ${float(precio):,.2f} / mes", fg="#27ae60", bg="white",
                    font=("Arial", 12, "bold")).pack(anchor="w", pady=(2, 0))

        detalle = f"{tipo.capitalize()} · {m2} m² · {recamaras} rec · {banos} baños · {estacionamientos} est."
        tk.Label(card, text=detalle, bg="white", fg="#555").pack(anchor="w")
        if direccion:
            tk.Label(card, text=f"📍 {direccion}", bg="white", fg="#888").pack(anchor="w", pady=(2, 0))

        def navegar(e: tk.Event) -> None:
            id_inmueble = propiedad.get("id_inmueble")
            if not id_inmueble:
                return
            exito_det, detalle = self.controlador.ver_detalle_propiedad(id_inmueble)
            if exito_det:
                self.app.cambiar_vista(VistaDetallePropiedad, detalle)
            else:
                messagebox.showerror("Error", detalle)

        card.bind("<Button-1>", navegar)
        for widget in card.winfo_children():
            widget.bind("<Button-1>", navegar)

    def cargar_rentas(self) -> None:
        """Carga las rentas del cliente en la tabla."""
        for item in self.tree_rentas.get_children():
            self.tree_rentas.delete(item)
        id_cliente = self.app.usuario_actual.get("id_usuario")
        exito, rentas = self.controlador.ver_mis_rentas(id_cliente, ver_activas=True,
                                                            ver_finalizadas=True, ver_canceladas=True)
        if exito:
            for r in rentas:
                self.tree_rentas.insert("", "end", values=(
                    r.get("id_renta"),
                    r.get("inmueble"),
                    r.get("arrendador"),
                    r.get("fecha_inicio"),
                    r.get("fecha_fin"),
                    r.get("estado"),
                    f"${r.get('precio_mensual', 0):,.2f}",
                    f"${r.get('total', 0):,.2f}",
                    r.get("id_inmueble", "")
                ))

    def cancelar_renta_desde_historial(self) -> None:
        """Permite al cliente cancelar una renta activa seleccionada en la tabla."""
        seleccion = self.tree_rentas.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una renta.")
            return
        
        item = self.tree_rentas.item(seleccion[0])
        id_renta = item["values"][0]
        estado = item["values"][5]

        if estado != "activa":
            messagebox.showwarning("Atención", "Solo se pueden cancelar rentas activas.")
            return
        
        motivo = simpledialog.askstring("Motivo", "Escribe el motivo de la cancelación:")

        if not motivo:
            return
        
        exito, msg = self.controlador.cancelar_mi_renta(id_renta,
                                                            self.app.usuario_actual["id_usuario"],
                                                            motivo)
        if exito:
            messagebox.showinfo("Cancelación", msg)
            self.cargar_rentas()
        else:
            messagebox.showerror("Error", msg)

    def abrir_perfil(self) -> None:
        from vista.vista_perfil import VistaPerfil
        win = tk.Toplevel(self.app)
        VistaPerfil(win, self.app, self.app.usuario_actual, self.controlador)

    def cerrar_sesion(self) -> None:
        self.app.mostrar_login()