import re
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any
from controlador.controlador_auth import ControladorAuth

class VistaLogin:
    """Vista de inicio de sesión y registro de nuevos usuarios."""

    def __init__(self, parent: tk.Widget, app: Any) -> None:
        self.parent = parent
        self.app = app
        self.controlador = ControladorAuth()

        tk.Label(parent, text="HOMIFY", font=("Helvetica", 24, "bold")).pack(pady=30)
        tk.Label(parent, text="Inicia sesión para continuar", font=("Helvetica", 10)).pack()

        tk.Label(parent, text="Email:").pack(pady=(20, 0))
        self.ent_email = tk.Entry(parent, width=30)
        self.ent_email.pack(pady=5)

        tk.Label(parent, text="Contraseña:").pack(pady=(10, 0))
        self.ent_pass = tk.Entry(parent, width=30, show="*")
        self.ent_pass.pack(pady=5)

        tk.Button(parent, text="Ingresar", bg="#2ecc71", fg="white", width=25,
                    command=self.ejecutar_login).pack(pady=30)

        tk.Label(parent, text="¿No tienes cuenta?").pack()
        btn_reg = tk.Label(parent, text="Regístrate aquí", fg="blue", cursor="hand2")
        btn_reg.pack()
        btn_reg.bind("<Button-1>", lambda e: self.abrir_ventana_registro())

    def ejecutar_login(self) -> None:
        """Obtiene credenciales y solicita autenticación al controlador."""
        email = self.ent_email.get()
        password = self.ent_pass.get()
        exito, resultado = self.controlador.login(email, password)
        if exito:
            messagebox.showinfo("Bienvenido", f"Hola {resultado['nombre_completo']}, bienvenido al sistema.")
            self.app.entrar_al_sistema(resultado)
        else:
            messagebox.showerror("Error", resultado)

    def abrir_ventana_registro(self) -> None:
        """Abre una ventana emergente con el formulario de registro."""
        self.win_reg = tk.Toplevel(self.app)
        self.win_reg.title("Nuevo Registro")
        self.win_reg.geometry("400x700")

        tk.Label(self.win_reg, text="Crea tu cuenta", font=("Helvetica", 14, "bold")).pack(pady=10)

        fields = [
            ("Nombre", "nombre", "ej. Juan"),
            ("Apellido", "apellido", "ej. Pérez"),
            ("Email", "email", "correo@ejemplo.com"),
            ("Teléfono", "telefono", "XX-XXXX-XXXX")
        ]
        self.reg_entries = {}

        for label, key, placeholder in fields:
            tk.Label(self.win_reg, text=label).pack()
            ent = tk.Entry(self.win_reg, width=30)
            ent.pack(pady=2)
            if placeholder:
                ent.insert(0, placeholder)
                ent.bind("<FocusIn>", lambda e, entry=ent, ph=placeholder: self._limpiar_placeholder(entry, ph))
                ent.bind("<FocusOut>", lambda e, entry=ent, ph=placeholder: self._restaurar_placeholder(entry, ph))
            self.reg_entries[key] = ent

        tk.Label(self.win_reg, text="Género").pack()
        self.cb_genero = ttk.Combobox(self.win_reg, values=["masculino", "femenino", "otro"], state="readonly")
        self.cb_genero.set("otro")
        self.cb_genero.pack(pady=2)

        tk.Label(self.win_reg, text="Fecha de Nacimiento (AAAA-MM-DD)").pack()
        self.ent_fecha_nac = tk.Entry(self.win_reg, width=30)
        self.ent_fecha_nac.insert(0, "AAAA-MM-DD")
        self.ent_fecha_nac.bind("<FocusIn>", lambda e: self._limpiar_placeholder(self.ent_fecha_nac, "AAAA-MM-DD"))
        self.ent_fecha_nac.bind("<FocusOut>", lambda e: self._restaurar_placeholder(self.ent_fecha_nac, "AAAA-MM-DD"))
        self.ent_fecha_nac.pack(pady=2)

        tk.Label(self.win_reg, text="Contraseña").pack()
        self.ent_reg_pass = tk.Entry(self.win_reg, width=30, show="*")
        self.ent_reg_pass.pack()

        requisitos = "Mín. 8 caracteres, 1 mayúscula, 1 minúscula, 1 número y 1 especial (!@#$...)"
        tk.Label(self.win_reg, text=requisitos, font=("Helvetica", 8), fg="gray").pack(pady=(0, 5))

        tk.Label(self.win_reg, text="Confirmar Contraseña").pack()
        self.ent_reg_conf = tk.Entry(self.win_reg, width=30, show="*")
        self.ent_reg_conf.pack()

        tk.Label(self.win_reg, text="Rol").pack()
        self.cb_rol = ttk.Combobox(self.win_reg, values=["cliente", "arrendador"], state="readonly")
        self.cb_rol.set("cliente")
        self.cb_rol.pack(pady=5)

        tk.Button(self.win_reg, text="Registrarme", bg="#3498db", fg="white",
                    command=self.ejecutar_registro).pack(pady=20)

    def _limpiar_placeholder(self, entry: tk.Entry, placeholder: str) -> None:
        """Limpia el placeholder si el texto actual coincide con él."""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)

    def _restaurar_placeholder(self, entry: tk.Entry, placeholder: str) -> None:
        """Restaura el placeholder si el campo está vacío."""
        if not entry.get():
            entry.insert(0, placeholder)

    def ejecutar_registro(self) -> None:
        """Recopila datos del formulario y solicita el registro al controlador."""
        datos = {k: v.get() for k, v in self.reg_entries.items()}
        fecha_nac = self.ent_fecha_nac.get().strip()
        if not fecha_nac or fecha_nac == "AAAA-MM-DD":
            messagebox.showerror("Error", "Debe ingresar una fecha de nacimiento válida.")
            return
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', fecha_nac):
            messagebox.showerror("Error", "La fecha de nacimiento debe tener el formato AAAA-MM-DD.")
            return

        telefono = datos.get('telefono', '').strip()
        if telefono and telefono != "XX-XXXX-XXXX":
            if not re.match(r'^\d{2}-\d{4}-\d{4}$', telefono):
                messagebox.showerror("Error", "El teléfono debe tener el formato XX-XXXX-XXXX (10 dígitos).")
                return

        genero = self.cb_genero.get()
        exito, msg = self.controlador.registrar(
            nombre=datos['nombre'],
            apellido=datos['apellido'],
            email=datos['email'],
            telefono=telefono,
            password=self.ent_reg_pass.get(),
            confirmar_password=self.ent_reg_conf.get(),
            genero=genero,
            fecha_nacimiento=fecha_nac,
            rol=self.cb_rol.get()
        )
        if exito:
            messagebox.showinfo("Éxito", msg)
            self.win_reg.destroy()
        else:
            messagebox.showerror("Error de Registro", msg)