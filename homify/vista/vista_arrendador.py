import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from typing import Any, Dict, Optional, List
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from controlador.controlador_arrendador import ControladorArrendador

class VistaArrendador:
    """
    Panel principal del arrendador. Muestra sus propiedades registradas,
    permite publicar nuevas, cancelar rentas activas y gestionar su perfil.
    """

    def __init__(self, parent: tk.Frame, app: Any) -> None:
        """
        Inicializa la vista del arrendador.

        Args:
            parent: Frame contenedor donde se despliega esta vista.
            app: Instancia principal de la aplicación.
        """
        self.parent = parent
        self.app = app
        self.controlador = ControladorArrendador()
        self.usuario = self.app.usuario_actual
        self.id_arrendador = self.usuario.get("id_usuario")
        self.pagina_actual = 0
        self.limite_por_pagina = 10
        self.total_paginas = 1

        frame_header = tk.Frame(parent)
        frame_header.pack(fill="x", padx=20, pady=10)
        nombre_mostrar = self.usuario.get("nombre_completo", "Usuario")
        titulo = f"Panel de Arrendador | Bienvenido, {nombre_mostrar}"
        tk.Label(frame_header, text=titulo, font=("Arial", 14, "bold")).pack(side="left")

        tk.Button(frame_header, text="Mi Perfil", bg="#2c3e50", fg="white",
                    command=self.abrir_perfil).pack(side="right", padx=5)
        tk.Button(frame_header, text="Cerrar Sesión", bg="#e74c3c", fg="white",
                    command=self.cerrar_sesion).pack(side="right", padx=5)
        tk.Button(frame_header, text="+ Nueva Propiedad", bg="#3498db", fg="white",
                    command=self.abrir_formulario_propiedad).pack(side="right", padx=10)

        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True)

        self.tab_propiedades = tk.Frame(self.notebook, bg="white")
        self.tab_rentas = tk.Frame(self.notebook, bg="white")
        self.tab_dashboard = tk.Frame(self.notebook, bg="white")

        self.notebook.add(self.tab_propiedades, text="Mis Propiedades")
        self.notebook.add(self.tab_rentas, text="Mis Rentas")
        self.notebook.add(self.tab_dashboard, text="Dashboard")

        self._construir_pestana_propiedades()
        self._construir_pestana_rentas()
        self._construir_pestana_dashboard()

        self.cargar_mis_propiedades()
        self.cargar_rentas()
        self.cargar_dashboard()

    def _construir_pestana_propiedades(self) -> None:
        """Construye la pestaña de propiedades con filtro, scroll invisible y paginación."""
        tk.Label(self.tab_propiedades, text="Tus Propiedades Registradas:", font=("Arial", 12),
                    bg="white").pack(anchor="w", padx=20, pady=5)

        frame_filtro = tk.Frame(self.tab_propiedades, bg="white")
        frame_filtro.pack(fill="x", padx=20, pady=(0, 5))
        tk.Label(frame_filtro, text="Mostrar:", bg="white").pack(side="left")
        self.filtro_estado = ttk.Combobox(frame_filtro, values=["Todas", "Disponibles", "Dadas de baja"],
                                            state="readonly", width=15)
        self.filtro_estado.set("Todas")
        self.filtro_estado.pack(side="left", padx=5)
        self.filtro_estado.bind("<<ComboboxSelected>>", lambda e: self.cargar_mis_propiedades())

        frame_canvas = tk.Frame(self.tab_propiedades, bg="white")
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

        frame_paginacion = tk.Frame(self.tab_propiedades, bg="white")
        frame_paginacion.pack(fill="x", pady=(5, 10))
        self.btn_ant = tk.Button(frame_paginacion, text="Anterior", command=self.ir_atras)
        self.btn_ant.pack(side="left", padx=20)
        self.lbl_pag = tk.Label(frame_paginacion, text="Página 1 de 1", bg="white")
        self.lbl_pag.pack(side="left", expand=True)
        self.btn_sig = tk.Button(frame_paginacion, text="Siguiente", command=self.ir_adelante)
        self.btn_sig.pack(side="right", padx=20)

    def _construir_pestana_rentas(self) -> None:
        """Construye la pestaña de historial de rentas del arrendador."""
        frame_tabla = tk.Frame(self.tab_rentas)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

        scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal")
        scroll_x.pack(side="bottom", fill="x")

        columnas = ("id_renta", "inmueble", "inquilino", "contacto", "fecha_inicio", "fecha_fin",
                    "estado", "precio_mensual", "total_contrato")
        
        self.tree_rentas = ttk.Treeview(
            frame_tabla, 
            columns=columnas, 
            show="headings", 
            height=12, 
            xscrollcommand=scroll_x.set
        )
        scroll_x.config(command=self.tree_rentas.xview)

        self.tree_rentas.heading("id_renta", text="ID Renta")
        self.tree_rentas.heading("inmueble", text="Inmueble")
        self.tree_rentas.heading("inquilino", text="Inquilino")
        self.tree_rentas.heading("contacto", text="Contacto")
        self.tree_rentas.heading("fecha_inicio", text="Inicio")
        self.tree_rentas.heading("fecha_fin", text="Fin")
        self.tree_rentas.heading("estado", text="Estado")
        self.tree_rentas.heading("precio_mensual", text="Precio/mes")
        self.tree_rentas.heading("total_contrato", text="Total")

        anchos_columnas = {
            "id_renta": 120, 
            "inmueble": 200, 
            "inquilino": 160, 
            "contacto": 350,
            "fecha_inicio": 110, 
            "fecha_fin": 110, 
            "estado": 100, 
            "precio_mensual": 120, 
            "total_contrato": 150
        }
        
        for col in columnas:
            self.tree_rentas.column(col, width=anchos_columnas[col], minwidth=anchos_columnas[col], stretch=False)

        self.tree_rentas.pack(side="top", fill="both", expand=True)

        frame_acciones = tk.Frame(self.tab_rentas, bg="white")
        frame_acciones.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(frame_acciones, text="Estado:", bg="white").pack(side="left", padx=(0,5))
        self.cb_filtro_estado_rentas = ttk.Combobox(
            frame_acciones, values=["Todas", "Activas", "Finalizadas", "Canceladas"],
            state="readonly", width=12
        )
        self.cb_filtro_estado_rentas.set("Todas")
        self.cb_filtro_estado_rentas.pack(side="left", padx=5)
        self.cb_filtro_estado_rentas.bind("<<ComboboxSelected>>", lambda e: self.cargar_rentas())

        tk.Button(
            frame_acciones, text="Refrescar", bg="#3498db", fg="white",
            command=self.cargar_rentas
        ).pack(side="left", padx=5)
        tk.Button(
            frame_acciones, text="Finalizar Renta", bg="#2ecc71", fg="white",
            command=self.finalizar_renta_desde_lista
        ).pack(side="left", padx=5)
        tk.Button(
            frame_acciones, text="Cancelar Renta", bg="#e74c3c", fg="white",
            command=self.cancelar_renta_desde_lista
        ).pack(side="left", padx=5)

    def _construir_pestana_dashboard(self) -> None:
        """Construye la pestaña del dashboard con filtros, métricas y gráfico."""
        frame_filtros = tk.Frame(self.tab_dashboard, bg="white")
        frame_filtros.pack(fill="x", padx=20, pady=10)
        tk.Label(frame_filtros, text="Desde:", bg="white").pack(side="left")
        self.ent_fecha_ini = tk.Entry(frame_filtros, width=12)
        self.ent_fecha_ini.pack(side="left", padx=5)
        tk.Label(frame_filtros, text="Hasta:", bg="white").pack(side="left")
        self.ent_fecha_fin = tk.Entry(frame_filtros, width=12)
        self.ent_fecha_fin.pack(side="left", padx=5)
        tk.Label(frame_filtros, text="Estado:", bg="white").pack(side="left", padx=(15, 0))
        self.cb_estado_dash = ttk.Combobox(
            frame_filtros, values=["Todas", "Activas", "Finalizadas", "Canceladas"],
            state="readonly", width=12
        )
        self.cb_estado_dash.set("Todas")
        self.cb_estado_dash.pack(side="left", padx=5)
        tk.Button(frame_filtros, text="Actualizar", bg="#3498db", fg="white",
                    command=self.cargar_dashboard).pack(side="left", padx=10)

        frame_metricas = tk.Frame(self.tab_dashboard, bg="white")
        frame_metricas.pack(fill="x", padx=20, pady=(10, 0))
        self.lbl_contratos = tk.Label(frame_metricas, text="Contratos totales: --", font=("Arial", 12), bg="white")
        self.lbl_contratos.pack(anchor="w")
        self.lbl_activos = tk.Label(frame_metricas, text="Contratos activos: --", font=("Arial", 12), bg="white")
        self.lbl_activos.pack(anchor="w")
        self.lbl_ingresos = tk.Label(frame_metricas, text="Ingresos totales: --", font=("Arial", 12), bg="white")
        self.lbl_ingresos.pack(anchor="w")

        self.frame_grafico = tk.Frame(self.tab_dashboard, bg="white")
        self.frame_grafico.pack(fill="both", expand=True, padx=20, pady=10)

    def cargar_mis_propiedades(self) -> None:
        """Obtiene y muestra las propiedades según el filtro activo."""
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        exito, resultado = self.controlador.obtener_propiedades(self.id_arrendador)
        if not exito:
            messagebox.showerror("Error de Base de Datos", resultado)
            return

        self.todas_las_propiedades = resultado if resultado else []

        filtro = self.filtro_estado.get()
        if filtro == "Disponibles":
            propiedades_filtradas = [p for p in self.todas_las_propiedades if p.get("disponible")]
        elif filtro == "Dadas de baja":
            propiedades_filtradas = [p for p in self.todas_las_propiedades if not p.get("disponible")]
        else:
            propiedades_filtradas = self.todas_las_propiedades

        self.total_paginas = max(1, (len(propiedades_filtradas) // self.limite_por_pagina) +
                                    (1 if len(propiedades_filtradas) % self.limite_por_pagina > 0 else 0))

        if self.pagina_actual >= self.total_paginas:
            self.pagina_actual = self.total_paginas - 1

        inicio = self.pagina_actual * self.limite_por_pagina
        fin = inicio + self.limite_por_pagina
        pagina_actual = propiedades_filtradas[inicio:fin]

        if not pagina_actual:
            tk.Label(self.frame_lista, text="No hay propiedades en esta categoría.", fg="gray", bg="white").pack(pady=20)
        else:
            for prop in pagina_actual:
                self.crear_tarjeta_propiedad(prop)

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.lbl_pag.config(text=f"Página {self.pagina_actual + 1} de {self.total_paginas}")
        self._actualizar_botones_paginacion()

    def cargar_rentas(self) -> None:
        """Carga las rentas del arrendador en la tabla, con filtro por estado."""
        for item in self.tree_rentas.get_children():
            self.tree_rentas.delete(item)
        exito, rentas = self.controlador.obtener_rentas(self.id_arrendador)
        if exito:
            filtro = self.cb_filtro_estado_rentas.get()
            for r in rentas:
                if filtro == "Activas" and r.get("estado") != "activa":
                    continue
                if filtro == "Finalizadas" and r.get("estado") != "finalizada":
                    continue
                if filtro == "Canceladas" and r.get("estado") != "cancelada":
                    continue
                self.tree_rentas.insert("", "end", values=(
                    r.get("id_renta"),
                    r.get("inmueble"),
                    r.get("inquilino"),
                    r.get("contacto_inquilino"),
                    r.get("fecha_inicio"),
                    r.get("fecha_fin"),
                    r.get("estado"),
                    f"${r.get('precio_mensual', 0):,.2f}",
                    f"${r.get('total_contrato', 0):,.2f}"
                ))

    def cargar_dashboard(self) -> None:
        """Obtiene los datos según filtros y actualiza métricas y gráfico."""
        fecha_ini = self.ent_fecha_ini.get().strip() or None
        fecha_fin = self.ent_fecha_fin.get().strip() or None
        estado_sel = self.cb_estado_dash.get()
        if estado_sel == "Activas":
            estados = ['activa']
        elif estado_sel == "Finalizadas":
            estados = ['finalizada']
        elif estado_sel == "Canceladas":
            estados = ['cancelada']
        else:
            estados = None

        datos = self.controlador.obtener_datos_dashboard(
            self.id_arrendador, fecha_ini, fecha_fin, estados
        )
        self.lbl_contratos.config(text=f"Contratos totales: {datos['total_contratos']}")
        self.lbl_activos.config(text=f"Contratos activos: {datos['contratos_activos']}")
        self.lbl_ingresos.config(text=f"Ingresos totales: ${datos['ingresos_totales']:,.2f}")

        for widget in self.frame_grafico.winfo_children():
            widget.destroy()
        self._dibujar_grafico(datos['rentas_por_mes'])

    def finalizar_renta_desde_lista(self) -> None:
        """Solicita una fecha y finaliza la renta activa seleccionada."""
        seleccion = self.tree_rentas.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una renta.")
            return
        item = self.tree_rentas.item(seleccion[0])
        id_renta = item["values"][0]
        estado = item["values"][6]
        if estado != "activa":
            messagebox.showwarning("Atención", "Solo se pueden finalizar rentas activas.")
            return
        fecha = simpledialog.askstring("Fecha de finalización", "Ingresa la fecha real de fin (AAAA-MM-DD):")
        if not fecha:
            return
        exito, msg = self.controlador.finalizar_renta_propia(id_renta, self.id_arrendador, fecha.strip())
        if exito:
            messagebox.showinfo("Finalización exitosa", msg)
            self.cargar_rentas()
            self.cargar_mis_propiedades()
        else:
            messagebox.showerror("Error", msg)

    def cancelar_renta_desde_lista(self) -> None:
        """Cancela una renta activa seleccionada de la lista."""
        seleccion = self.tree_rentas.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una renta.")
            return
        item = self.tree_rentas.item(seleccion[0])
        id_renta = item["values"][0]
        estado = item["values"][6]
        if estado != "activa":
            messagebox.showwarning("Atención", "Solo se pueden cancelar rentas activas.")
            return
        motivo = simpledialog.askstring("Motivo", "Escribe el motivo de la cancelación:")
        if not motivo:
            return
        exito, msg = self.controlador.cancelar_renta_propia(id_renta, self.id_arrendador, motivo.strip())
        if exito:
            messagebox.showinfo("Cancelación exitosa", msg)
            self.cargar_rentas()
            self.cargar_mis_propiedades()
        else:
            messagebox.showerror("Error", msg)

    def _actualizar_botones_paginacion(self) -> None:
        """Habilita o deshabilita los botones de paginación según la página actual."""
        if self.pagina_actual == 0:
            self.btn_ant.config(state="disabled")
        else:
            self.btn_ant.config(state="normal")
        if self.pagina_actual >= self.total_paginas - 1:
            self.btn_sig.config(state="disabled")
        else:
            self.btn_sig.config(state="normal")

    def ir_adelante(self) -> None:
        """Avanza a la siguiente página si está disponible y recarga las propiedades."""
        if self.pagina_actual < self.total_paginas - 1:
            self.pagina_actual += 1
            self.cargar_mis_propiedades()

    def ir_atras(self) -> None:
        """Retrocede a la página anterior si no es la primera y recarga las propiedades."""
        if self.pagina_actual > 0:
            self.pagina_actual -= 1
            self.cargar_mis_propiedades()

    def crear_tarjeta_propiedad(self, prop: Dict[str, Any]) -> None:
        """
        Crea una tarjeta visual para una propiedad con sus detalles y acciones disponibles.

        Args:
            prop: Diccionario con los datos de la propiedad.
        """
        card = tk.Frame(self.frame_lista, bd=1, relief="solid", padx=15, pady=10, bg="white")
        card.pack(fill="x", pady=5, padx=5)

        disponible = prop.get("disponible", True)
        estado_visual = "🟢 Disponible" if disponible else "🔴 Rentada"
        ganancia = prop.get("ganancia_mensual", 0)
        precio_renta = prop.get("precio_renta", 0)
        titulo = prop.get("titulo", "Sin título")
        direccion = prop.get("direccion", "Dirección no especificada")
        tiene_renta_activa = prop.get("tiene_renta_activa", False)
        id_renta_activa = prop.get("id_renta_activa")

        tk.Label(card, text=f"{titulo}", font=("Arial", 11, "bold"), bg="white").pack(anchor="w")
        tk.Label(card, text=f"Dirección: {direccion}", bg="white").pack(anchor="w")
        tk.Label(card, text=f"Precio de renta: ${precio_renta:,.2f} / mes", bg="white").pack(anchor="w")
        tk.Label(card, text=f"Tipo: {prop.get('tipo', 'N/A').capitalize()}", bg="white").pack(anchor="w")
        tk.Label(card, text=f"Estado: {estado_visual}", bg="white").pack(anchor="w")

        if disponible:
            if not tiene_renta_activa:
                btn_editar = tk.Button(card, text="Editar", bg="#f1c40f", fg="black",
                                        command=lambda i=prop.get("id_inmueble"): self.abrir_edicion_propiedad(i))
                btn_editar.pack(anchor="w", pady=(0, 2))
                btn_baja = tk.Button(card, text="Dar de baja", bg="#95a5a6", fg="white",
                                        command=lambda i=prop.get("id_inmueble"): self.desactivar_propiedad(i))
                btn_baja.pack(anchor="w", pady=2)
            else:
                if id_renta_activa:
                    inquilino = prop.get("inquilino", "N/A")
                    fecha_ini = prop.get("fecha_inicio_renta", "")
                    fecha_fin = prop.get("fecha_fin_renta", "")
                    tk.Label(card, text=f"Inquilino: {inquilino}", bg="white").pack(anchor="w")
                    tk.Label(card, text=f"Periodo: {fecha_ini} → {fecha_fin}", bg="white").pack(anchor="w")
                    if ganancia > 0:
                        tk.Label(card, text=f"Ingreso actual: ${ganancia:,.2f} / mes", fg="green", bg="white").pack(anchor="w")
                    btn_cancelar = tk.Button(card, text="Cancelar Renta", bg="#e67e22", fg="white",
                                                command=lambda r=id_renta_activa: self.cancelar_renta_desde_tarjeta(r))
                    btn_cancelar.pack(anchor="w", pady=5)
        else:
            btn_reactivar = tk.Button(card, text="Reactivar", bg="#27ae60", fg="white",
                                        command=lambda i=prop.get("id_inmueble"): self.reactivar_propiedad(i))
            btn_reactivar.pack(anchor="w", pady=2)
            for child in card.winfo_children():
                child.config(fg="gray")
            card.config(bg="#f5f5f5")

    def cancelar_renta_desde_tarjeta(self, id_renta: str) -> None:
        """
        Solicita un motivo y cancela la renta activa de una propiedad.

        Args:
            id_renta: Identificador de la renta a cancelar.
        """
        motivo = simpledialog.askstring("Motivo de cancelación", "Explica brevemente el motivo:")
        if motivo is None:
            return
        if not motivo.strip():
            messagebox.showwarning("Motivo requerido", "Debes proporcionar un motivo para cancelar la renta.")
            return
        exito, msg = self.controlador.cancelar_renta_propia(id_renta, self.id_arrendador, motivo.strip())
        if exito:
            messagebox.showinfo("Cancelación exitosa", msg)
            self.cargar_mis_propiedades()
        else:
            messagebox.showerror("Error", msg)

    def _dibujar_grafico(self, rentas_por_mes: List[Dict[str, Any]]) -> None:
        """Dibuja un gráfico de barras de ingresos por mes."""
        if not rentas_por_mes:
            tk.Label(self.frame_grafico, text="Sin datos para el gráfico.", bg="white", fg="gray").pack()
            return

        meses = [r['mes'] for r in rentas_por_mes]
        ingresos = [r['ingresos'] for r in rentas_por_mes]

        fig = Figure(figsize=(8, 3), dpi=100)
        ax = fig.add_subplot(111)
        bars = ax.bar(meses, ingresos, color='#3498db')
        ax.set_title("Ingresos por mes")
        ax.set_ylabel("Ingresos ($)")
        ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def abrir_formulario_propiedad(self) -> None:
        """Abre una ventana emergente con el formulario para publicar una nueva propiedad."""
        self.win_prop = tk.Toplevel(self.app)
        self.win_prop.title("Publicar Inmueble")
        self.win_prop.geometry("450x750")

        tk.Label(self.win_prop, text="Detalles del Inmueble", font=("Arial", 14, "bold")).pack(pady=10)

        campos_basicos = [
            ("Título", "titulo"),
            ("Dirección", "direccion"),
            ("Precio mensual ($)", "precio"),
            ("Metros de construcción", "m2_construccion"),
            ("Recámaras", "recamaras"),
            ("Baños completos", "banos"),
            ("Medios baños", "medios_banos"),
            ("Estacionamientos", "estacionamientos"),
            ("Antigüedad (años)", "antiguedad")
        ]
        self.entradas_prop: Dict[str, tk.Entry] = {}
        for label, key in campos_basicos:
            frame = tk.Frame(self.win_prop)
            frame.pack(fill="x", padx=20, pady=2)
            tk.Label(frame, text=label, width=20, anchor="w").pack(side="left")
            ent = tk.Entry(frame)
            ent.pack(side="right", expand=True, fill="x")
            self.entradas_prop[key] = ent

        tk.Label(self.win_prop, text="Descripción:", font=("Arial", 10)).pack(anchor="w", padx=20, pady=(10, 0))
        self.txt_descripcion = tk.Text(self.win_prop, height=4, width=40)
        self.txt_descripcion.pack(padx=20, pady=5)

        tk.Label(self.win_prop, text="Amenidades:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(10, 0))
        amenities_frame = tk.Frame(self.win_prop)
        amenities_frame.pack(fill="x", padx=20)
        self.amen_vars: Dict[str, tk.BooleanVar] = {}
        amenities = ["alberca", "amueblado", "cocina_integral", "cuarto_servicio", "seguridad"]
        for i, amen in enumerate(amenities):
            var = tk.BooleanVar()
            cb = tk.Checkbutton(amenities_frame, text=amen.capitalize(), variable=var)
            cb.grid(row=i // 3, column=i % 3, sticky="w", padx=5)
            self.amen_vars[amen] = var

        tk.Label(self.win_prop, text="Tipo de Inmueble:").pack(anchor="w", padx=20, pady=(10, 0))
        self.cb_tipo = ttk.Combobox(self.win_prop, values=["casa", "departamento"], state="readonly")
        self.cb_tipo.set("casa")
        self.cb_tipo.pack(pady=5)
        self.cb_tipo.bind("<<ComboboxSelected>>", self.actualizar_campos_especificos)

        self.frame_especifico = tk.Frame(self.win_prop)
        self.frame_especifico.pack(fill="x", padx=20, pady=5)
        self.actualizar_campos_especificos()

        tk.Button(self.win_prop, text="Guardar y Publicar", bg="#2ecc71", fg="white",
                    command=self.guardar_propiedad).pack(pady=20)

    def actualizar_campos_especificos(self, event: Optional[tk.Event] = None) -> None:
        """Muestra los campos adicionales según el tipo de inmueble seleccionado."""
        for widget in self.frame_especifico.winfo_children():
            widget.destroy()
        tipo = self.cb_tipo.get()
        if tipo == "casa":
            tk.Label(self.frame_especifico, text="Metros de terreno:").pack(anchor="w")
            self.ent_m2_terreno = tk.Entry(self.frame_especifico)
            self.ent_m2_terreno.pack(fill="x", pady=2)
            self.var_patio = tk.BooleanVar()
            tk.Checkbutton(self.frame_especifico, text="Tiene patio", variable=self.var_patio).pack(anchor="w")
        else:
            self.var_elevador = tk.BooleanVar()
            tk.Checkbutton(self.frame_especifico, text="Edificio con elevador", variable=self.var_elevador).pack(anchor="w")

    def guardar_propiedad(self) -> None:
        """Valida y envía los datos del formulario para registrar la propiedad."""
        datos = {k: v.get().strip() for k, v in self.entradas_prop.items()}
        datos["tipo"] = self.cb_tipo.get()
        datos["id_arrendador"] = self.id_arrendador

        obligatorios = ["titulo", "direccion", "precio"]
        for campo in obligatorios:
            if not datos.get(campo):
                messagebox.showwarning("Atención", f"El campo {campo} es obligatorio.")
                return

        campos_numericos = {
            "precio": float,
            "m2_construccion": int,
            "recamaras": int,
            "banos": int,
            "medios_banos": int,
            "estacionamientos": int,
            "antiguedad": int
        }
        for campo, tipo in campos_numericos.items():
            if campo in datos:
                try:
                    datos[campo] = tipo(datos[campo])
                except ValueError:
                    messagebox.showerror("Error", f"El campo '{campo}' debe ser un número válido.")
                    return

        for amen, var in self.amen_vars.items():
            datos[amen] = var.get()

        datos["descripcion"] = self.txt_descripcion.get("1.0", "end").strip()

        if datos["tipo"] == "casa":
            m2_terreno = self.ent_m2_terreno.get().strip()
            try:
                datos["m2_terreno"] = int(m2_terreno) if m2_terreno else 0
            except ValueError:
                messagebox.showerror("Error", "Metros de terreno debe ser un número entero.")
                return
            datos["patio"] = self.var_patio.get()
        else:
            datos["elevador"] = self.var_elevador.get()

        exito, msg = self.controlador.registrar_propiedad(datos)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.win_prop.destroy()
            self.cargar_mis_propiedades()
        else:
            messagebox.showerror("Error al guardar", msg)

    def desactivar_propiedad(self, id_inmueble: str) -> None:
        """
        Solicita confirmación y desactiva una propiedad del arrendador.

        Args:
            id_inmueble: Identificador del inmueble a desactivar.
        """
        if not messagebox.askyesno("Confirmar", "¿Dar de baja esta propiedad?\nDejará de mostrarse en búsquedas."):
            return
        exito, msg = self.controlador.desactivar_propiedad(id_inmueble, self.id_arrendador)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.cargar_mis_propiedades()
        else:
            messagebox.showerror("Error", msg)

    def reactivar_propiedad(self, id_inmueble: str) -> None:
        """
        Solicita confirmación y reactiva una propiedad del arrendador.

        Args:
            id_inmueble: Identificador del inmueble a reactivar.
        """
        if not messagebox.askyesno("Confirmar", "¿Volver a publicar esta propiedad?"):
            return
        exito, msg = self.controlador.reactivar_propiedad(id_inmueble, self.id_arrendador)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.cargar_mis_propiedades()
        else:
            messagebox.showerror("Error", msg)

    def abrir_edicion_propiedad(self, id_inmueble: str) -> None:
        """
        Abre una ventana con el formulario precargado para editar la propiedad.

        Args:
            id_inmueble: Identificador del inmueble a editar.
        """
        detalle = self.controlador.obtener_detalle_propiedad(id_inmueble)
        if not detalle:
            messagebox.showerror("Error", "No se pudo cargar la información de la propiedad.")
            return

        self.win_edit = tk.Toplevel(self.app)
        self.win_edit.title("Editar Inmueble")
        self.win_edit.geometry("450x750")

        tk.Label(self.win_edit, text="Editar Inmueble", font=("Arial", 14, "bold")).pack(pady=10)

        campos_basicos = [
            ("Título", "titulo"),
            ("Dirección", "direccion"),
            ("Precio mensual ($)", "precio"),
            ("Metros de construcción", "m2_construccion"),
            ("Recámaras", "recamaras"),
            ("Baños completos", "banos"),
            ("Medios baños", "medios_banos"),
            ("Estacionamientos", "estacionamientos"),
            ("Antigüedad (años)", "antiguedad")
        ]
        self.entradas_edit: Dict[str, tk.Entry] = {}
        for label, key in campos_basicos:
            frame = tk.Frame(self.win_edit)
            frame.pack(fill="x", padx=20, pady=2)
            tk.Label(frame, text=label, width=20, anchor="w").pack(side="left")
            ent = tk.Entry(frame)
            ent.insert(0, str(detalle.get(key, "")))
            ent.pack(side="right", expand=True, fill="x")
            self.entradas_edit[key] = ent

        tk.Label(self.win_edit, text="Descripción:", font=("Arial", 10)).pack(anchor="w", padx=20, pady=(10, 0))
        self.txt_desc_edit = tk.Text(self.win_edit, height=4, width=40)
        self.txt_desc_edit.insert("1.0", detalle.get("descripcion", ""))
        self.txt_desc_edit.pack(padx=20, pady=5)

        tk.Label(self.win_edit, text="Amenidades:", font=("Arial", 10, "bold")).pack(anchor="w", padx=20, pady=(10, 0))
        amenities_frame = tk.Frame(self.win_edit)
        amenities_frame.pack(fill="x", padx=20)
        self.amen_edit: Dict[str, tk.BooleanVar] = {}
        amenities = ["alberca", "amueblado", "cocina_integral", "cuarto_servicio", "seguridad"]
        for i, amen in enumerate(amenities):
            var = tk.BooleanVar(value=bool(detalle.get(amen, False)))
            cb = tk.Checkbutton(amenities_frame, text=amen.capitalize(), variable=var)
            cb.grid(row=i // 3, column=i % 3, sticky="w", padx=5)
            self.amen_edit[amen] = var

        tipo_actual = detalle.get("tipo_inmueble", "casa")
        tk.Label(self.win_edit, text="Tipo de Inmueble:").pack(anchor="w", padx=20, pady=(10, 0))
        self.cb_tipo_edit = ttk.Combobox(self.win_edit, values=["casa", "departamento"], state="readonly")
        self.cb_tipo_edit.set(tipo_actual)
        self.cb_tipo_edit.pack(pady=5)
        self.cb_tipo_edit.bind("<<ComboboxSelected>>", self.actualizar_campos_especificos_edit)

        self.frame_especifico_edit = tk.Frame(self.win_edit)
        self.frame_especifico_edit.pack(fill="x", padx=20, pady=5)
        self.actualizar_campos_especificos_edit(tipo_inicial=tipo_actual, detalle=detalle)

        self.id_inmueble_edit = id_inmueble

        tk.Button(self.win_edit, text="Guardar Cambios", bg="#2ecc71", fg="white",
                    command=self.guardar_edicion_propiedad).pack(pady=20)

    def actualizar_campos_especificos_edit(self, event: Optional[tk.Event] = None,
                                                tipo_inicial: Optional[str] = None,
                                                detalle: Optional[Dict[str, Any]] = None
                                                ) -> None:
        """
        Muestra los campos adicionales según el tipo de inmueble seleccionado en edición.

        Args:
            event: Evento de Tkinter (opcional).
            tipo_inicial: Tipo de inmueble precargado.
            detalle: Diccionario con los datos actuales del inmueble.
        """
        for widget in self.frame_especifico_edit.winfo_children():
            widget.destroy()
        tipo = self.cb_tipo_edit.get() if tipo_inicial is None else tipo_inicial
        if tipo == "casa":
            tk.Label(self.frame_especifico_edit, text="Metros de terreno:").pack(anchor="w")
            self.ent_m2_terreno_edit = tk.Entry(self.frame_especifico_edit)
            if detalle:
                self.ent_m2_terreno_edit.insert(0, str(detalle.get("m2_terreno", 0)))
            self.ent_m2_terreno_edit.pack(fill="x", pady=2)
            self.var_patio_edit = tk.BooleanVar(value=bool(detalle.get("patio", False)) if detalle else False)
            tk.Checkbutton(self.frame_especifico_edit, text="Tiene patio", variable=self.var_patio_edit).pack(anchor="w")
        else:
            self.var_elevador_edit = tk.BooleanVar(value=bool(detalle.get("elevador", False)) if detalle else False)
            tk.Checkbutton(self.frame_especifico_edit, text="Edificio con elevador", variable=self.var_elevador_edit).pack(anchor="w")

    def guardar_edicion_propiedad(self) -> None:
        """Recoge los datos del formulario de edición y envía la actualización al controlador."""
        datos = {k: v.get().strip() for k, v in self.entradas_edit.items()}
        datos["tipo"] = self.cb_tipo_edit.get()
        datos["id_arrendador"] = self.id_arrendador
        datos["id_inmueble"] = self.id_inmueble_edit

        obligatorios = ["titulo", "direccion", "precio"]
        for campo in obligatorios:
            if not datos.get(campo):
                messagebox.showwarning("Atención", f"El campo {campo} es obligatorio.")
                return

        campos_numericos = {
            "precio": float,
            "m2_construccion": int,
            "recamaras": int,
            "banos": int,
            "medios_banos": int,
            "estacionamientos": int,
            "antiguedad": int
        }
        for campo, tipo in campos_numericos.items():
            if campo in datos:
                try:
                    datos[campo] = tipo(datos[campo])
                except ValueError:
                    messagebox.showerror("Error", f"El campo '{campo}' debe ser un número válido.")
                    return

        for amen, var in self.amen_edit.items():
            datos[amen] = var.get()

        datos["descripcion"] = self.txt_desc_edit.get("1.0", "end").strip()

        if datos["tipo"] == "casa":
            m2_terreno = self.ent_m2_terreno_edit.get().strip()
            try:
                datos["m2_terreno"] = int(m2_terreno) if m2_terreno else 0
            except ValueError:
                messagebox.showerror("Error", "Metros de terreno debe ser un número entero.")
                return
            datos["patio"] = self.var_patio_edit.get()
        else:
            datos["elevador"] = self.var_elevador_edit.get()

        exito, msg = self.controlador.editar_propiedad(datos)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.win_edit.destroy()
            self.cargar_mis_propiedades()
        else:
            messagebox.showerror("Error al guardar", msg)

    def abrir_perfil(self) -> None:
        """Abre la ventana de edición de perfil del arrendador."""
        from vista.vista_perfil import VistaPerfil
        win = tk.Toplevel(self.app)
        VistaPerfil(win, self.app, self.app.usuario_actual, self.controlador)

    def cerrar_sesion(self) -> None:
        """Cierra la sesión actual y regresa a la pantalla de login."""
        self.app.mostrar_login()