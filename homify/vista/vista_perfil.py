import tkinter as tk
from tkinter import messagebox, ttk
import re
from typing import Any, Dict

class VistaPerfil:
    """
    Ventana de edición de perfil de usuario y cambio de contraseña.
    Se adapta a cualquier rol mediante el controlador inyectado.
    """

    def __init__(self, parent: tk.Toplevel, app: Any, usuario_actual: Dict[str, Any], controlador: Any) -> None:
        """
        Inicializa la vista de perfil.

        Args:
            parent: Ventana contenedora (Toplevel).
            app: Instancia principal de la aplicación.
            usuario_actual: Diccionario con los datos del usuario autenticado.
            controlador: Controlador del rol correspondiente (Cliente, Arrendador, Admin).
        """
        self.parent = parent
        self.app = app
        self.usuario = usuario_actual
        self.controlador = controlador

        self.parent.title("Mi Perfil")
        self.parent.geometry("500x550")
        self.parent.resizable(False, False)

        exito, datos = self.controlador.obtener_perfil(self.usuario["id_usuario"])
        if not exito:
            messagebox.showerror("Error", datos)
            self.parent.destroy()
            return
        self.datos_originales = datos

        tk.Label(self.parent, text="Editar Perfil", font=("Arial", 14, "bold")).pack(pady=10)

        frame_form = tk.Frame(self.parent)
        frame_form.pack(padx=20, pady=10, fill="both", expand=True)

        campos = [
            ("ID", "id_usuario", None, True),
            ("Nombre", "nombre", None, False),
            ("Apellido", "apellido", None, False),
            ("Fecha Nacimiento (AAAA-MM-DD)", "fecha_nacimiento", None, False),
            ("Género", "genero", ["masculino", "femenino", "otro"], False),
            ("Email", "email", None, False),
            ("Teléfono (XX-XXXX-XXXX)", "telefono", None, False)
        ]

        self.entries: Dict[str, Any] = {}
        for label, key, values, readonly in campos:
            tk.Label(frame_form, text=label).pack(anchor="w", pady=(10, 0))
            if values:
                var = tk.StringVar(value=self.datos_originales.get(key, ""))
                combo = ttk.Combobox(frame_form, textvariable=var, values=values, state="readonly")
                combo.pack(fill="x")
                self.entries[key] = var
            else:
                ent = tk.Entry(frame_form)
                ent.insert(0, self.datos_originales.get(key, ""))
                if readonly:
                    ent.config(state="readonly")
                ent.pack(fill="x")
                self.entries[key] = ent

        btn_frame = tk.Frame(self.parent)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Guardar Cambios", bg="#2ecc71", fg="white", command=self.guardar_cambios).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cambiar Contraseña", bg="#3498db", fg="white", command=self.abrir_cambiar_password).pack(side="left", padx=10)
        if self.usuario.get("rol") != "admin":
            tk.Button(btn_frame, text="Eliminar mi cuenta", bg="#e74c3c", fg="white", command=self.eliminar_cuenta).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Cancelar", command=self.parent.destroy).pack(side="left", padx=10)

    def guardar_cambios(self) -> None:
        """Recolecta datos del formulario, los valida y solicita actualización al controlador."""
        datos: Dict[str, str] = {}
        for key, widget in self.entries.items():
            if isinstance(widget, tk.StringVar):
                valor = widget.get()
            else:
                valor = widget.get()
            datos[key] = valor

        if not datos["email"] or "@" not in datos["email"]:
            messagebox.showerror("Error", "Debe ingresar un email válido.")
            return

        telefono = datos.get("telefono", "")
        if telefono and not re.match(r'^\d{2}-\d{4}-\d{4}$', telefono):
            messagebox.showerror("Error", "El teléfono debe tener el formato XX-XXXX-XXXX.")
            return

        fecha_nac = datos.get("fecha_nacimiento", "")
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', fecha_nac):
            messagebox.showerror("Error", "La fecha de nacimiento debe tener el formato AAAA-MM-DD.")
            return

        exito, msg = self.controlador.actualizar_perfil(
            self.usuario["id_usuario"],
            datos["nombre"],
            datos["apellido"],
            fecha_nac,
            datos["genero"],
            datos["email"],
            telefono
        )

        if exito:
            exito2, datos_actualizados = self.controlador.obtener_perfil(self.usuario["id_usuario"])
            if exito2:
                self.app.usuario_actual.update(datos_actualizados)
            messagebox.showinfo("Éxito", msg)
            self.parent.destroy()
        else:
            messagebox.showerror("Error", msg)

    def abrir_cambiar_password(self) -> None:
        """Abre una ventana secundaria para cambiar la contraseña."""
        win = tk.Toplevel(self.parent)
        win.title("Cambiar Contraseña")
        win.geometry("400x350")
        win.resizable(False, False)

        tk.Label(win, text="Contraseña actual:").pack(pady=5)
        ent_actual = tk.Entry(win, show="*")
        ent_actual.pack()

        tk.Label(win, text="Nueva contraseña:").pack(pady=(10, 0))
        ent_nueva = tk.Entry(win, show="*")
        ent_nueva.pack()

        tk.Label(win, text="Confirmar nueva:").pack(pady=(10, 0))
        ent_conf = tk.Entry(win, show="*")
        ent_conf.pack()

        requisitos = "Mín. 8 caracteres, 1 mayúscula, 1 minúscula, 1 número y 1 especial (!@#$...)"
        tk.Label(win, text=requisitos, font=("Helvetica", 8), fg="gray", wraplength=350).pack(pady=(10, 5))

        def cambiar() -> None:
            """Envía la solicitud de cambio de contraseña al controlador."""
            actual = ent_actual.get()
            nueva = ent_nueva.get()
            conf = ent_conf.get()
            exito, msg = self.controlador.cambiar_password(
                self.usuario["id_usuario"], actual, nueva, conf
            )
            if exito:
                messagebox.showinfo("Éxito", msg)
                win.destroy()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(win, text="Actualizar", command=cambiar, bg="#2ecc71", fg="white").pack(pady=20)

    def eliminar_cuenta(self) -> None:
        """Solicita confirmación y procede a eliminar la cuenta del usuario."""
        if not messagebox.askyesno("Confirmar eliminación",
                                    "¿Estás seguro de eliminar tu cuenta?\n"
                                    "No podrás acceder nuevamente con este correo.\n"
                                    "Tus datos personales serán anonimizados."):
            return
        exito, msg = self.controlador.eliminar_mi_cuenta(self.usuario["id_usuario"])
        if exito:
            messagebox.showinfo("Cuenta eliminada", msg)
            self.parent.destroy()
            self.app.mostrar_login()
        else:
            messagebox.showerror("Error", msg)