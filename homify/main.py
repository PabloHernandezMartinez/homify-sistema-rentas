import tkinter as tk
from typing import Any, Dict, Type
from vista.vista_login import VistaLogin

class AplicacionPrincipal(tk.Tk):
    """
    Ventana principal de la aplicación HOMIFY.
    Gestiona el cambio de vistas y la sesión del usuario autenticado.
    """

    def __init__(self) -> None:
        """Inicializa la ventana principal y carga la vista de login."""
        super().__init__()
        self.title("Homify - Gestión Inmobiliaria")
        self.geometry("900x600")

        self.usuario_actual: Dict[str, Any] = None

        self.contenedor = tk.Frame(self)
        self.contenedor.pack(fill="both", expand=True)

        self.mostrar_login()

    def mostrar_login(self) -> None:
        """Limpia el contenedor y muestra la pantalla de inicio de sesión."""
        self._limpiar_contenedor()
        VistaLogin(self.contenedor, self)

    def entrar_al_sistema(self, datos_usuario: Dict[str, Any]) -> None:
        """
        Redirige al usuario autenticado a la vista correspondiente según su rol.

        Args:
            datos_usuario: Diccionario con los datos del perfil del usuario.
        """
        self.usuario_actual = datos_usuario
        rol = datos_usuario.get("rol", "cliente")

        if rol == "cliente":
            from vista.vista_cliente import VistaCliente
            self.cambiar_vista(VistaCliente)
        elif rol == "arrendador":
            from vista.vista_arrendador import VistaArrendador
            self.cambiar_vista(VistaArrendador)
        elif rol == "admin":
            from vista.vista_admin import VistaAdmin
            self.cambiar_vista(VistaAdmin)
        else:
            print(f"Rol desconocido: {rol}")
            self.mostrar_login()

    def _limpiar_contenedor(self) -> None:
        """Elimina todos los widgets del contenedor principal."""
        for widget in self.contenedor.winfo_children():
            widget.destroy()

    def cambiar_vista(self, nueva_vista_class: Type[Any], *args: Any) -> None:
        """
        Reemplaza la vista actual por una nueva.

        Args:
            nueva_vista_class: Clase de la vista a instanciar.
            *args: Argumentos adicionales que recibe el constructor de la vista.
        """
        self._limpiar_contenedor()
        nueva_vista_class(self.contenedor, self, *args)


if __name__ == "__main__":
    app = AplicacionPrincipal()
    app.mainloop()