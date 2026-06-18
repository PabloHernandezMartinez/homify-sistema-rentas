import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from typing import Any
from controlador.controlador_admin import ControladorAdmin

class VistaAdmin:
    """
    Panel de administración. Permite gestionar usuarios, inmuebles y rentas
    a través de un sistema de pestañas.
    """

    def __init__(self, parent: tk.Frame, app: Any) -> None:
        """
        Inicializa la vista de administración.

        Args:
            parent: Frame contenedor donde se despliega esta vista.
            app: Instancia principal de la aplicación.
        """
        self.parent = parent
        self.app = app
        self.controlador = ControladorAdmin()

        self.admin_actual = self.app.usuario_actual
        self.id_admin = self.admin_actual.get("id_usuario")

        frame_header = tk.Frame(parent)
        frame_header.pack(fill="x", padx=20, pady=10)

        nombre_mostrar = self.admin_actual.get("nombre_completo", "Admin")
        titulo = f"Panel de Administración | Admin: {nombre_mostrar}"
        tk.Label(frame_header, text=titulo, font=("Arial", 14, "bold")).pack(side="left")

        tk.Button(frame_header, text="Mi Perfil", bg="#2c3e50", fg="white",
                    command=self.abrir_perfil).pack(side="right", padx=5)
        tk.Button(frame_header, text="Cerrar Sesión", bg="#e74c3c", fg="white",
                    command=self.cerrar_sesion).pack(side="right", padx=5)

        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        self.tab_usuarios = ttk.Frame(self.notebook)
        self.tab_inmuebles = ttk.Frame(self.notebook)
        self.tab_rentas = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_usuarios, text="Gestión de Usuarios")
        self.notebook.add(self.tab_inmuebles, text="Inmuebles")
        self.notebook.add(self.tab_rentas, text="Rentas")

        self._construir_pestaña_usuarios()
        self._construir_pestaña_inmuebles()
        self._construir_pestaña_rentas()

        self.cargar_usuarios()
        self.cargar_inmuebles()
        self.cargar_rentas()

    def _construir_pestaña_usuarios(self) -> None:
        """Construye la interfaz de la pestaña de gestión de usuarios."""
        frame_filtros = tk.Frame(self.tab_usuarios)
        frame_filtros.pack(fill="x", pady=10, padx=10)

        tk.Label(frame_filtros, text="Buscar ID:").grid(row=0, column=0, padx=5)
        self.ent_buscar_usuario = tk.Entry(frame_filtros, width=20)
        self.ent_buscar_usuario.grid(row=0, column=1, padx=5)

        self.var_activos = tk.BooleanVar(value=True)
        self.var_suspendidos = tk.BooleanVar(value=False)
        self.var_eliminados = tk.BooleanVar(value=False)

        tk.Checkbutton(frame_filtros, text="Activos", variable=self.var_activos).grid(row=0, column=2, padx=5)
        tk.Checkbutton(frame_filtros, text="Suspendidos", variable=self.var_suspendidos).grid(row=0, column=3, padx=5)
        tk.Checkbutton(frame_filtros, text="Eliminados", variable=self.var_eliminados).grid(row=0, column=4, padx=5)

        tk.Label(frame_filtros, text="Rol:").grid(row=0, column=5, padx=5)
        self.cb_filtro_rol = ttk.Combobox(frame_filtros, values=["Todos", "cliente", "arrendador", "admin"],
                                            state="readonly", width=10)
        self.cb_filtro_rol.set("Todos")
        self.cb_filtro_rol.grid(row=0, column=6, padx=5)

        tk.Button(frame_filtros, text="Filtrar", bg="#3498db", fg="white",
                    command=self.cargar_usuarios).grid(row=0, column=7, padx=10)

        columnas = ("id", "nombre", "email", "rol", "estado")
        self.tree_usuarios = ttk.Treeview(self.tab_usuarios, columns=columnas, show="headings", height=15)
        self.tree_usuarios.heading("id", text="ID Usuario")
        self.tree_usuarios.heading("nombre", text="Nombre")
        self.tree_usuarios.heading("email", text="Email")
        self.tree_usuarios.heading("rol", text="Rol")
        self.tree_usuarios.heading("estado", text="Estado")
        self.tree_usuarios.column("id", width=100)
        self.tree_usuarios.column("rol", width=80)
        self.tree_usuarios.column("estado", width=80)
        self.tree_usuarios.pack(fill="both", expand=True, padx=10, pady=5)

        frame_acciones = tk.Frame(self.tab_usuarios)
        frame_acciones.pack(fill="x", pady=10, padx=10)
        tk.Button(frame_acciones, text="Suspender", bg="#f39c12", fg="white",
                    command=lambda: self.ejecutar_cambio_estado("suspendido")).pack(side="left", padx=5)
        tk.Button(frame_acciones, text="Reactivar", bg="#2ecc71", fg="white",
                    command=lambda: self.ejecutar_cambio_estado("activo")).pack(side="left", padx=5)
        tk.Button(frame_acciones, text="Eliminar", bg="#e74c3c", fg="white",
                    command=lambda: self.ejecutar_cambio_estado("eliminado")).pack(side="left", padx=5)

    def cargar_usuarios(self) -> None:
        """Carga los usuarios en el Treeview según los filtros activos."""
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)
        buscar_id = self.ent_buscar_usuario.get().strip() or None
        rol_sel = self.cb_filtro_rol.get()
        rol_filtro = None if rol_sel == "Todos" else rol_sel
        exito, resultado = self.controlador.obtener_usuarios(
            buscar_id=buscar_id,
            ver_activos=self.var_activos.get(),
            ver_suspendidos=self.var_suspendidos.get(),
            ver_eliminados=self.var_eliminados.get(),
            rol=rol_filtro
        )
        if exito:
            for u in resultado:
                self.tree_usuarios.insert("", "end", values=(
                    u.get("id_usuario"),
                    f"{u.get('nombre', '')} {u.get('apellido', '')}",
                    u.get("email"),
                    u.get("rol"),
                    u.get("estado")
                ))
        else:
            self.tree_usuarios.insert("", "end", values=("", resultado, "", "", ""))

    def ejecutar_cambio_estado(self, nuevo_estado: str) -> None:
        """Solicita confirmación y cambia el estado del usuario seleccionado."""
        seleccion = self.tree_usuarios.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un usuario.")
            return
        item = self.tree_usuarios.item(seleccion[0])
        id_objetivo = item["values"][0]
        if not id_objetivo:
            return
        confirmar = messagebox.askyesno("Confirmar", f"¿Cambiar estado a {nuevo_estado.upper()}?")
        if confirmar:
            exito, msg = self.controlador.cambiar_estado_usuario(id_objetivo, self.id_admin, nuevo_estado)
            if exito:
                messagebox.showinfo("Éxito", msg)
                self.cargar_usuarios()
            else:
                messagebox.showerror("Error", msg)

    def _construir_pestaña_inmuebles(self) -> None:
        """Construye la interfaz de la pestaña de auditoría de inmuebles."""
        frame_filtros = tk.Frame(self.tab_inmuebles)
        frame_filtros.pack(fill="x", pady=10, padx=10)
        tk.Label(frame_filtros, text="Buscar ID Inmueble:").pack(side="left", padx=5)
        self.ent_buscar_inmueble = tk.Entry(frame_filtros, width=20)
        self.ent_buscar_inmueble.pack(side="left", padx=5)
        tk.Label(frame_filtros, text="Buscar ID Arrendador:").pack(side="left", padx=(20,5))
        self.ent_id_arrendador = tk.Entry(frame_filtros, width=15)
        self.ent_id_arrendador.pack(side="left", padx=5)
        tk.Button(frame_filtros, text="Buscar / Refrescar", bg="#3498db", fg="white",
                    command=self.cargar_inmuebles).pack(side="left", padx=10)
        tk.Label(frame_filtros, text="Tipo:").pack(side="left", padx=(20, 5))
        self.cb_tipo_inmueble = ttk.Combobox(frame_filtros, values=["Todos", "casa", "departamento"],
                                                state="readonly", width=12)
        self.cb_tipo_inmueble.set("Todos")
        self.cb_tipo_inmueble.pack(side="left", padx=5)
        self.cb_tipo_inmueble.bind("<<ComboboxSelected>>", lambda e: self.cargar_inmuebles())
        tk.Label(frame_filtros, text="Estado:").pack(side="left", padx=(20,5))
        self.cb_estado_inmueble = ttk.Combobox(frame_filtros, values=["Todos","Disponible","Rentado"],
                                        state="readonly", width=12)
        self.cb_estado_inmueble.set("Todos")
        self.cb_estado_inmueble.pack(side="left", padx=5)
        self.cb_estado_inmueble.bind("<<ComboboxSelected>>", lambda e: self.cargar_inmuebles())

        columnas_inm = ("id", "titulo", "id_arrendador", "estado", "precio")
        self.tree_inmuebles = ttk.Treeview(self.tab_inmuebles, columns=columnas_inm, show="headings", height=12)
        self.tree_inmuebles.heading("id", text="ID Inmueble")
        self.tree_inmuebles.heading("titulo", text="Título")
        self.tree_inmuebles.heading("id_arrendador", text="ID Arrendador")
        self.tree_inmuebles.heading("estado", text="Estado")
        self.tree_inmuebles.heading("precio", text="Precio ($)")
        self.tree_inmuebles.pack(fill="both", expand=True, padx=10, pady=5)

        frame_acciones_inm = tk.Frame(self.tab_inmuebles)
        frame_acciones_inm.pack(fill="x", pady=5, padx=10)
        tk.Button(frame_acciones_inm, text="Cambiar Disponibilidad", bg="#f39c12", fg="white",
                    command=self.cambiar_disponibilidad).pack(side="left", padx=5)
        tk.Button(frame_acciones_inm, text="Actualizar Precio", bg="#2ecc71", fg="white",
                    command=self.actualizar_precio).pack(side="left", padx=5)
        tk.Button(frame_acciones_inm, text="Exportar CSV", bg="#9b59b6", fg="white",
                    command=self.exportar_csv).pack(side="left", padx=5)

    def cargar_inmuebles(self) -> None:
        """Carga los inmuebles en el Treeview según los filtros activos."""
        for item in self.tree_inmuebles.get_children():
            self.tree_inmuebles.delete(item)

        buscar_id = self.ent_buscar_inmueble.get().strip() or None
        tipo = self.cb_tipo_inmueble.get()
        tipo_filtro = None if tipo == "Todos" else tipo
        id_arrendador = self.ent_id_arrendador.get().strip() or None
        estado = self.cb_estado_inmueble.get()
        if estado == "Disponible":
            disponible = True
        elif estado == "Rentado":
            disponible = False
        else:
            disponible = None

        exito, resultado = self.controlador.auditar_inmuebles(
            buscar_id=buscar_id,
            tipo_inmueble=tipo_filtro,
            id_arrendador=id_arrendador,
            esta_disponible=disponible
        )

        if exito:
            for inm in resultado:
                estado_texto = "Disponible" if inm.get("esta_disponible") else "Rentado"
                precio = inm.get("precio_renta", 0)
                self.tree_inmuebles.insert("", "end", values=(
                    inm.get("id_inmueble"),
                    inm.get("titulo"),
                    inm.get("id_arrendador"),
                    estado_texto,
                    f"{float(precio):,.2f}"
                ))
        else:
            self.tree_inmuebles.insert("", "end", values=("", resultado, "", "", ""))

    def cambiar_disponibilidad(self) -> None:
        """Cambia la disponibilidad del inmueble seleccionado."""
        seleccion = self.tree_inmuebles.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un inmueble.")
            return
        item = self.tree_inmuebles.item(seleccion[0])
        id_inmueble = item["values"][0]
        estado_actual = item["values"][3]
        nuevo_estado = not (estado_actual == "Disponible")
        accion = "activar" if nuevo_estado else "desactivar"
        confirmar = messagebox.askyesno("Confirmar", f"¿Quieres {accion} este inmueble?")
        if confirmar:
            exito, msg = self.controlador.cambiar_disponibilidad_inmueble(id_inmueble, nuevo_estado)
            if exito:
                messagebox.showinfo("Éxito", msg)
                self.cargar_inmuebles()
            else:
                messagebox.showerror("Error", msg)

    def actualizar_precio(self) -> None:
        """Actualiza el precio del inmueble seleccionado."""
        seleccion = self.tree_inmuebles.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un inmueble.")
            return
        item = self.tree_inmuebles.item(seleccion[0])
        id_inmueble = item["values"][0]
        nuevo_precio = simpledialog.askstring("Actualizar precio", "Nuevo precio mensual:")
        if not nuevo_precio:
            return
        try:
            precio_float = float(nuevo_precio)
        except ValueError:
            messagebox.showerror("Error", "Ingresa un número válido.")
            return
        exito, msg = self.controlador.actualizar_precio_inmueble(id_inmueble, precio_float)
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.cargar_inmuebles()
        else:
            messagebox.showerror("Error", msg)

    def _construir_pestaña_rentas(self) -> None:
        """Construye la interfaz de la pestaña de rentas."""
        frame_filtros_rentas = tk.Frame(self.tab_rentas)
        frame_filtros_rentas.pack(fill="x", pady=10, padx=10)
        tk.Label(frame_filtros_rentas, text="ID Cliente:").pack(side="left")
        self.ent_id_cliente_renta = tk.Entry(frame_filtros_rentas, width=12)
        self.ent_id_cliente_renta.pack(side="left", padx=5)
        tk.Label(frame_filtros_rentas, text="ID Arrendador:").pack(side="left")
        self.ent_id_arrend_renta = tk.Entry(frame_filtros_rentas, width=12)
        self.ent_id_arrend_renta.pack(side="left", padx=5)
        tk.Label(frame_filtros_rentas, text="Estado:").pack(side="left")
        self.cb_estado_renta = ttk.Combobox(frame_filtros_rentas, values=["Todos","activa","finalizada","cancelada"],
                                            state="readonly", width=12)
        self.cb_estado_renta.set("Todos")
        self.cb_estado_renta.pack(side="left", padx=5)
        tk.Button(frame_filtros_rentas, text="Filtrar", bg="#3498db", fg="white",
                    command=self.cargar_rentas).pack(side="left", padx=10)

        frame_tabla = tk.Frame(self.tab_rentas)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=5)

        scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal")
        scroll_x.pack(side="bottom", fill="x")

        columnas_ren = ("id_renta", "id_cliente", "cliente", "id_arrendador", "propietario", "inmueble", "estado", "precio")
        
        self.tree_rentas = ttk.Treeview(
            frame_tabla, 
            columns=columnas_ren, 
            show="headings", 
            height=12, 
            xscrollcommand=scroll_x.set
        )
        
        scroll_x.config(command=self.tree_rentas.xview)

        self.tree_rentas.heading("id_renta", text="ID Renta")
        self.tree_rentas.heading("id_cliente", text="ID Cliente")
        self.tree_rentas.heading("cliente", text="Cliente")
        self.tree_rentas.heading("id_arrendador", text="ID Arrendador")
        self.tree_rentas.heading("propietario", text="Propietario")
        self.tree_rentas.heading("inmueble", text="Inmueble")
        self.tree_rentas.heading("estado", text="Estado")
        self.tree_rentas.heading("precio", text="Precio Mes")

        anchos_columnas = {
            "id_renta": 140, "id_cliente": 140, "cliente": 180, 
            "id_arrendador": 140, "propietario": 180, "inmueble": 200, 
            "estado": 140, "precio": 180
        }
        
        for col in columnas_ren:
            self.tree_rentas.column(col, width=anchos_columnas[col], minwidth=anchos_columnas[col], stretch=False)

        self.tree_rentas.pack(side="top", fill="both", expand=True)

        frame_acciones_ren = tk.Frame(self.tab_rentas)
        frame_acciones_ren.pack(fill="x", pady=5, padx=10)
        tk.Button(
            frame_acciones_ren, text="Finalizar Renta", bg="#2ecc71", fg="white",
            command=self.finalizar_renta_admin
        ).pack(side="left", padx=5)
        tk.Button(frame_acciones_ren, text="Cancelar Renta", bg="#e74c3c", fg="white",
                    command=self.cancelar_renta_admin).pack(side="left", padx=5)

    def cargar_rentas(self) -> None:
        """Carga todas las rentas en el Treeview."""
        for item in self.tree_rentas.get_children():
            self.tree_rentas.delete(item)
        id_cliente = self.ent_id_cliente_renta.get().strip() or None
        id_arrendador = self.ent_id_arrend_renta.get().strip() or None
        estado = self.cb_estado_renta.get()
        estado = None if estado == "Todos" else estado

        exito, resultado = self.controlador.obtener_todas_las_rentas(id_cliente, id_arrendador, estado)
        if exito:
            for r in resultado:
                self.tree_rentas.insert("", "end", values=(
                    r.get("id_renta"),
                    r.get("id_cliente", ""),
                    r.get("cliente"),
                    r.get("id_arrendador", ""),
                    r.get("propietario"),
                    r.get("inmueble"),
                    r.get("estado"),
                    f"${r.get('precio_mensual', 0):,.2f}"
                ))

    def finalizar_renta_admin(self) -> None:
        """Solicita una fecha y finaliza una renta activa desde el panel de administración."""
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
        exito, msg = self.controlador.finalizar_renta(id_renta, fecha.strip())
        if exito:
            messagebox.showinfo("Finalización exitosa", msg)
            self.cargar_rentas()
        else:
            messagebox.showerror("Error", msg)

    def cancelar_renta_admin(self) -> None:
        """Cancela una renta activa desde el panel de administración."""
        seleccion = self.tree_rentas.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona una renta.")
            return
        item = self.tree_rentas.item(seleccion[0])
        id_renta = item["values"][0]
        motivo = simpledialog.askstring("Motivo de cancelación", "Explica brevemente el motivo:")
        if not motivo or not motivo.strip():
            messagebox.showwarning("Motivo requerido", "Debes proporcionar un motivo.")
            return
        exito, msg = self.controlador.cancelar_renta(id_renta, motivo.strip())
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.cargar_rentas()
        else:
            messagebox.showerror("Error", msg)

    def exportar_csv(self) -> None:
        """
        Solicita al controlador los datos de inmuebles y los guarda como archivo CSV.

        Utiliza un diálogo para elegir la ubicación y escribe las columnas esperadas
        para el análisis posterior.
        """
        datos = self.controlador.exportar_inmuebles_csv()
        if not datos:
            messagebox.showinfo("Información", "No hay inmuebles para exportar.")
            return

        archivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivo CSV", "*.csv")],
            initialfile="inmuebles_exportados.csv"
        )
        if not archivo:
            return

        try:
            with open(archivo, "w", encoding="utf-8") as f:
                encabezados = [
                    "precio", "m2_terreno", "m2_construido", "banos", "medios_banos",
                    "estacionamientos", "antiguedad", "amen_Alberca", "amen_Cocina integral",
                    "amen_Amueblado", "amen_Elevador", "amen_Cuartos de servicio",
                    "tipo_propiedad_departamento", "tipo_propiedad_original", "direccion"
                ]
                f.write("\,".join(encabezados) + "\n")
                for fila in datos:
                    valores = [str(fila[col]) for col in encabezados]
                    f.write("\,".join(valores) + "\n")
            messagebox.showinfo("Éxito", f"Datos exportados a {archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}")

    def abrir_perfil(self) -> None:
        """Abre la ventana de edición de perfil del administrador."""
        from vista.vista_perfil import VistaPerfil
        win = tk.Toplevel(self.app)
        VistaPerfil(win, self.app, self.app.usuario_actual, self.controlador)

    def cerrar_sesion(self) -> None:
        """Cierra la sesión actual y regresa a la pantalla de login."""
        self.app.mostrar_login()