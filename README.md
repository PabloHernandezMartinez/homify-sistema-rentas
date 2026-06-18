# HOMIFY - Sistema de Gestion de Rentas y Prediccion de Precios

Aplicacion de escritorio para la gestion de rentas inmobiliarias, desarrollada con el
patron MVC e interfaz grafica en Tkinter. Incluye un modelo de Machine Learning
(XGBoost) que predice el precio de renta mensual de una propiedad a partir de sus
caracteristicas y ubicacion.

## Estructura del repositorio

.
├── homify/                        # Aplicacion principal
│   ├── controlador/
│   │   ├── controlador_admin.py
│   │   ├── controlador_arrendador.py
│   │   ├── controlador_auth.py
│   │   └── controlador_cliente.py
│   ├── datos/                     # Carpeta para BD y credenciales (generados)
│   ├── modelo/
│   │   ├── casa.py
│   │   ├── departamento.py
│   │   ├── enums.py
│   │   ├── gestordb.py
│   │   ├── inmuebles.py
│   │   ├── renta.py
│   │   └── usuario.py
│   ├── vista/
│   │   ├── vista_admin.py
│   │   ├── vista_arrendador.py
│   │   ├── vista_cliente.py
│   │   ├── vista_detalle_propiedad.py
│   │   ├── vista_login.py
│   │   └── vista_perfil.py
│   ├── main.py                    # Punto de entrada de la aplicacion
│   └── poblar.py                  # Genera datos de prueba
│
├── ML/                            # Modelo de Machine Learning
│   ├── columnas_modelo.json
│   ├── EDA.ipynb
│   ├── ETL.ipynb
│   ├── geolocalizacion.ipynb
│   ├── interfaz_prediccion.py
│   ├── modelado_final.ipynb
│   ├── modelado_justificacion.ipynb
│   ├── modelo_renta_xgboost_final.pkl
│   └── rent_features.csv
│
├── .gitignore
├── requirements.txt
└── README.md


## Requisitos previos

- Python 3.8 o superior.
- Tkinter (viene con la mayoria de instalaciones de Python; en Linux instalar
  python3-tk si no esta presente).


## Instalacion rapida (entorno virtual)

Abre una terminal en la raiz del proyecto clonado y ejecuta:

  # Crear entorno virtual
  python -m venv env

  # Activarlo (Windows)
  env\Scripts\activate

  # Activarlo (Linux/macOS)
  source env/bin/activate

  # Instalar todas las dependencias exactas
  pip install -r requirements.txt

  # Generar la base de datos de prueba
  cd homify
  python poblar.py

  # Ejecutar la aplicacion
  python main.py


El comando `pip install -r requirements.txt` instala automaticamente todas las
librerias necesarias con sus versiones correctas (bcrypt, pandas, xgboost, etc.).
No se requiere instalar nada manualmente.

La primera ejecucion de `poblar.py` crea:
- datos/sistema.db
- datos/usuarios_credenciales.txt (contrasenas en texto plano, solo para pruebas)

Usa esas credenciales para iniciar sesion. El administrador por defecto es:
  email: admin@homify.mx
  password: Admin123!


## Roles y funcionalidades principales

### Cliente
- Explorar inmuebles disponibles con filtros (tipo, precio, recamaras).
- Ver detalle de una propiedad.
- Rentar una propiedad (por dias o meses).
- Historial de rentas propias, cancelar una renta activa.
- Editar perfil y cambiar contrasena.
- Eliminar cuenta (si no tiene rentas activas).

### Arrendador
- Ver todas sus propiedades, publicar una nueva (casa o departamento).
- Editar o dar de baja/reactivar propiedades.
- Ver las rentas de sus inmuebles, finalizar o cancelar rentas.
- Dashboard con metricas de ingresos y grafico de barras.
- Gestionar su perfil.

### Administrador
- Listar todos los usuarios (filtrar por estado y rol).
- Suspender, activar o eliminar usuarios.
- Auditar todos los inmuebles, cambiar disponibilidad o precio.
- Ver y gestionar todas las rentas (finalizar o cancelar).
- Exportar todos los inmuebles a un archivo CSV.
- Editar su perfil.


## Modelo de Machine Learning (carpeta ML)

### Flujo de trabajo (simulado)

1. El administrador exporta los inmuebles desde la aplicacion (CSV).
2. El notebook `ETL.ipynb` limpia caracteres extranos y unifica direcciones.
   (No se ejecuta sobre `rent_features.csv` porque ya esta limpio.)
3. `geolocalizacion.ipynb` anade latitud y longitud usando las direcciones.
   Requiere direcciones reales; con los datos ficticios de prueba no funciona.
4. `EDA.ipynb` toma `rent_features.csv`, explora los datos y elimina outliers.
5. `modelado_justificacion.ipynb` compara modelos y elige XGBoost con
   hiperparametros optimos.
6. `modelado_final.ipynb` entrena XGBoost, evalua metricas (R², MAE, RMSE, MAPE)
   y guarda `modelo_renta_xgboost_final.pkl` y `columnas_modelo.json`.
7. `interfaz_prediccion.py` es una aplicacion independiente con Tkinter que usa
   el modelo entrenado para predecir el precio de renta de una propiedad.

   Para usarla:
     cd ML
     python interfaz_prediccion.py

   Introduce las caracteristicas de la propiedad y obtendras el precio estimado.


## Archivos importantes

- `.gitignore`: evita subir la base de datos, credenciales y archivos temporales.
- `requirements.txt`: lista de librerias con versiones exactas. Si necesitas
  regenerarlo, activa el entorno virtual y ejecuta `pip freeze > requirements.txt`.


## Clonacion y primer uso (resumen)

git clone https://github.com/PabloHernandezMartinez/homify-sistema-rentas.git
cd homify-sistema-rentas
python -m venv env
# (activar el entorno segun tu sistema)
pip install -r requirements.txt
cd homify
python poblar_db.py
python main.py


## Creditos

Proyecto desarrollado como parte de la materia Desarrollo de Aplicaciones para Análisis de Datos.
Estudiantes: 
	Delgado Ramírez Leonardo.
	Hernández Martínez Pablo.
Profesor: Alejandro López
Escuela: Escuela Superior de Cómputo. [ESCOM]