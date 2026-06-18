import os
import random
import bcrypt
import datetime
from typing import List
from modelo.gestordb import GestorDB

# -----------------------------------------------------------------------------
# Configuración de cantidades
# -----------------------------------------------------------------------------
NUM_ARRENDADORES = 20
NUM_CLIENTES = 30
NUM_INMUEBLES = 50
NUM_RENTAS = 40

# Datos base para generación aleatoria
NOMBRES_MASC = ["Carlos", "Miguel", "Jorge", "Fernando", "Ricardo", "Luis", "Raúl", "Andrés", "Diego", "Antonio"]
NOMBRES_FEM = ["Ana", "Sofía", "Elena", "Lucía", "Teresa", "Gabriela", "Patricia", "María", "Laura", "Valentina"]
NOMBRES_OTRO = ["Alex", "Sam", "René", "Cris", "Dani"]

APELLIDOS = ["López", "Martínez", "García", "Rodríguez", "Pérez", "Sánchez", "Gómez", "Díaz", "Torres", "Flores",
                "Ramírez", "Cruz", "Vargas", "Reyes", "Morales", "Ortega", "Castillo", "Fernández"]

CIUDADES = [
    "Ciudad de México", "Guadalajara", "Monterrey", "Puebla", "Querétaro", "Mérida", "Cancún", "Tijuana",
    "León", "San Luis Potosí", "Aguascalientes", "Morelia", "Veracruz", "Oaxaca", "Chihuahua"
]


def generar_telefono() -> str:
    """Genera un número telefónico con formato 55-XXXX-XXXX."""
    return f"55-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"


def generar_password() -> str:
    """
    Genera una contraseña que cumple las reglas del sistema:
    mínimo 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial.
    """
    base = random.choice(["Mx", "Hom", "Ren", "Pro", "Cas"])
    nums = str(random.randint(10, 99))
    especial = random.choice(["!", "@", "#", "$", "%", "&", "*"])
    return base + nums + especial + random.choice(["a", "b", "c", "d", "e"])


def generar_fecha_nacimiento() -> str:
    """Genera una fecha de nacimiento entre 25 y 60 años atrás en formato ISO."""
    años = random.randint(25, 60)
    return (datetime.date.today() - datetime.timedelta(days=años * 365)).isoformat()


def generar_email(nombre: str, apellido: str, sufijo: str = "") -> str:
    """
    Construye un email a partir del nombre y apellido, con sufijo opcional,
    bajo el dominio homify.mx.
    """
    base = f"{nombre.lower()}.{apellido.lower()}"
    if sufijo:
        base += f".{sufijo}"
    return f"{base}@homify.mx"


def generar_direccion() -> str:
    """Genera una dirección ficticia compuesta por calle, número, colonia y ciudad."""
    calle = random.choice(["Av.", "Calle", "Priv.", "Blvd."])
    nombre = random.choice(["Hidalgo", "Juárez", "Zaragoza", "Morelos", "Madero", "Reforma", "Universidad", "Acueducto"])
    numero = random.randint(100, 999)
    colonia = random.choice(["Centro", "Norte", "Sur", "Lomas", "Florida", "Vista Hermosa", "Olivos", "Pedregal"])
    ciudad = random.choice(CIUDADES)
    return f"{calle} {nombre} #{numero}, Col. {colonia}, {ciudad}"


def poblar_sistema() -> None:
    """
    Puebla la base de datos con datos de ejemplo: administrador, arrendadores,
    clientes, inmuebles y rentas. Al final genera un archivo con las credenciales.
    """
    ruta_db = os.path.join("datos", "sistema.db")
    ruta_credenciales = os.path.join("datos", "usuarios_credenciales.txt")

    if os.path.exists(ruta_db):
        os.remove(ruta_db)
        print("[CLEAN] Base de datos anterior eliminada.")

    gestor = GestorDB(ruta_db)

    credenciales: List[List[str]] = []  # [id, nombre completo, email, contraseña plana, rol]

    # -----------------------------------------------------------------
    # 1. Administrador
    # -----------------------------------------------------------------
    admin_password = "Admin123!"
    admin_hash = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt()).decode()
    datos_admin = {
        "id_usuario": "ADM-0001",
        "nombre": "Administrador",
        "apellido": "General",
        "fecha_nacimiento": "1985-04-15",
        "genero": "masculino",
        "email": "admin@homify.mx",
        "telefono": "55-0000-0001",
        "password": admin_hash,
        "fecha_registro": datetime.date.today().isoformat(),
        "estado": "activo",
        "rol": "admin"
    }
    gestor.registrar_usuario(datos_admin)
    credenciales.append(["ADM-0001", "Administrador General", "admin@homify.mx", admin_password, "admin"])
    print("[OK] Administrador creado.")

    # -----------------------------------------------------------------
    # 2. Arrendadores
    # -----------------------------------------------------------------
    arrendadores_ids: List[str] = []
    for i in range(1, NUM_ARRENDADORES + 1):
        id_usuario = f"ARR-{1000 + i}"
        genero_str = random.choice(["masculino", "femenino", "otro"])
        if genero_str == "masculino":
            nombre = random.choice(NOMBRES_MASC)
        elif genero_str == "femenino":
            nombre = random.choice(NOMBRES_FEM)
        else:
            nombre = random.choice(NOMBRES_OTRO)
        apellido = random.choice(APELLIDOS)
        email = generar_email(nombre, apellido, str(i))
        telefono = generar_telefono()
        password_plano = generar_password()
        password_hash = bcrypt.hashpw(password_plano.encode(), bcrypt.gensalt()).decode()

        datos = {
            "id_usuario": id_usuario,
            "nombre": nombre,
            "apellido": apellido,
            "fecha_nacimiento": generar_fecha_nacimiento(),
            "genero": genero_str,
            "email": email,
            "telefono": telefono,
            "password": password_hash,
            "fecha_registro": "2026-01-15",
            "estado": "activo",
            "rol": "arrendador"
        }
        gestor.registrar_usuario(datos)
        arrendadores_ids.append(id_usuario)
        credenciales.append([id_usuario, f"{nombre} {apellido}", email, password_plano, "arrendador"])
    print(f"[OK] {len(arrendadores_ids)} arrendadores creados.")

    # -----------------------------------------------------------------
    # 3. Clientes
    # -----------------------------------------------------------------
    clientes_ids: List[str] = []
    for i in range(1, NUM_CLIENTES + 1):
        id_usuario = f"CLI-{2000 + i}"
        genero_str = random.choice(["masculino", "femenino", "otro"])
        if genero_str == "masculino":
            nombre = random.choice(NOMBRES_MASC)
        elif genero_str == "femenino":
            nombre = random.choice(NOMBRES_FEM)
        else:
            nombre = random.choice(NOMBRES_OTRO)
        apellido = random.choice(APELLIDOS)
        email = generar_email(nombre, apellido, str(i))
        telefono = generar_telefono()
        password_plano = generar_password()
        password_hash = bcrypt.hashpw(password_plano.encode(), bcrypt.gensalt()).decode()

        datos = {
            "id_usuario": id_usuario,
            "nombre": nombre,
            "apellido": apellido,
            "fecha_nacimiento": generar_fecha_nacimiento(),
            "genero": genero_str,
            "email": email,
            "telefono": telefono,
            "password": password_hash,
            "fecha_registro": "2026-02-01",
            "estado": "activo",
            "rol": "cliente"
        }
        gestor.registrar_usuario(datos)
        clientes_ids.append(id_usuario)
        credenciales.append([id_usuario, f"{nombre} {apellido}", email, password_plano, "cliente"])
    print(f"[OK] {len(clientes_ids)} clientes creados.")

    # -----------------------------------------------------------------
    # 4. Inmuebles
    # -----------------------------------------------------------------
    inmuebles_ids: List[str] = []
    for i in range(NUM_INMUEBLES):
        id_inmueble = f"INM-{3000 + i}"
        if i < len(arrendadores_ids) * 2:
            id_arrendador = random.choice(arrendadores_ids[:10])
        else:
            id_arrendador = random.choice(arrendadores_ids)

        tipo = random.choice(["casa", "departamento"])
        precio = random.randint(5000, 30000)
        m2_const = random.randint(50, 300)
        recamaras = random.randint(1, 5)
        banos = random.randint(1, 3)
        medios_banos = random.randint(0, 1)
        estacionamientos = random.randint(0, 3)
        antiguedad = random.randint(0, 40)
        alberca = random.choice([0, 1])
        amueblado = random.choice([0, 1])
        cocina = random.choice([0, 1])
        cuarto_serv = random.choice([0, 1])
        seguridad = random.choice([0, 1])

        datos: dict = {
            "id_inmueble": id_inmueble,
            "id_arrendador": id_arrendador,
            "titulo": f"{'Casa' if tipo == 'casa' else 'Departamento'} en {random.choice(['zona residencial', 'zona céntrica', 'fraccionamiento privado'])}",
            "descripcion": f"Excelente propiedad con {banos} baños y {recamaras} recámaras.",
            "direccion": generar_direccion(),
            "precio_renta": precio,
            "m2_construccion": m2_const,
            "recamaras": recamaras,
            "banos": banos,
            "medios_banos": medios_banos,
            "estacionamientos": estacionamientos,
            "antiguedad": antiguedad,
            "alberca": alberca,
            "amueblado": amueblado,
            "cocina_integral": cocina,
            "cuarto_servicio": cuarto_serv,
            "seguridad": seguridad,
            "fecha_publicacion": datetime.date.today().isoformat(),
            "tipo_inmueble": tipo,
            "esta_disponible": 1
        }

        if tipo == "casa":
            datos["m2_terreno"] = random.randint(80, 500)
            datos["patio"] = random.choice([0, 1])
        else:
            datos["elevador"] = random.choice([0, 1])

        gestor.registrar_inmueble(datos)
        inmuebles_ids.append(id_inmueble)
    print(f"[OK] {len(inmuebles_ids)} inmuebles creados.")

    # -----------------------------------------------------------------
    # 5. Rentas
    # -----------------------------------------------------------------
    rentas_creadas = 0
    hoy = datetime.date.today()
    for _ in range(NUM_RENTAS * 2):
        if rentas_creadas >= NUM_RENTAS:
            break

        id_cliente = random.choice(clientes_ids)
        id_inmueble = random.choice(inmuebles_ids)

        detalle = gestor.consultar_detalle_inmueble(id_inmueble)
        if not detalle or not detalle.get("disponible"):
            continue

        fecha_inicio = hoy - datetime.timedelta(days=random.randint(0, 365))
        meses = random.randint(1, 12)
        fecha_fin = fecha_inicio + datetime.timedelta(days=30 * meses)

        if gestor.hay_solapamiento(id_inmueble, fecha_inicio.isoformat(), fecha_fin.isoformat()):
            continue

        if fecha_fin < hoy:
            estado = random.choice(["finalizada", "cancelada"])
        else:
            estado = "activa"

        precio_mensual = detalle["precio_renta"]
        total = precio_mensual * meses
        deposito = precio_mensual
        metodo = random.choice(["efectivo", "transferencia", "tarjeta"])
        id_renta = f"RNT-{4000 + rentas_creadas}"

        fecha_fin_real = None
        motivo_cancel = None
        if estado == "cancelada":
            fecha_fin_real = (fecha_inicio + datetime.timedelta(days=random.randint(5, meses * 15))).isoformat()
            motivo_cancel = random.choice(["No cumplió expectativas", "Problemas personales", "Inmueble en mal estado"])

        datos_renta = {
            "id_renta": id_renta,
            "id_cliente": id_cliente,
            "id_inmueble": id_inmueble,
            "id_arrendador": detalle["id_arrendador"],
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "precio_mensual": precio_mensual,
            "total": total,
            "deposito": deposito,
            "metodo_pago": metodo,
            "estado": estado,
            "fecha_fin_real": fecha_fin_real,
            "motivo_cancelacion": motivo_cancel
        }
        if gestor.registrar_renta(datos_renta):
            if estado == "activa":
                gestor.cambiar_disponibilidad_inmueble(id_inmueble, 0)
            rentas_creadas += 1

    print(f"[OK] {rentas_creadas} rentas creadas.")

    # -----------------------------------------------------------------
    # 6. Exportar credenciales
    # -----------------------------------------------------------------
    with open(ruta_credenciales, "w", encoding="utf-8") as f:
        f.write("ID,Nombre Completo,Email,Contraseña,Rol\n")
        for cred in credenciales:
            f.write(",".join(cred) + "\n")
    print(f"[ARCHIVO] Credenciales guardadas en '{ruta_credenciales}'.")
    print("\n[FINALIZADO] Poblamiento completo.")


if __name__ == "__main__":
    poblar_sistema()