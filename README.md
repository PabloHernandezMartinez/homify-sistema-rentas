# HOMIFY - Sistema de Gestión de Rentas y Predicción de Precios

Aplicación de escritorio para la gestión de rentas inmobiliarias, desarrollada con el
patrón MVC e interfaz gráfica en Tkinter. Incluye un modelo de Machine Learning
(XGBoost) que predice el precio de renta mensual de una propiedad a partir de sus
características y ubicación.

## Estructura del repositorio

.
├── homify/                        # Aplicación principal
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
│   │   ├── inmueble.py
│   │   ├── renta.py
│   │   └── usuario.py
│   ├── vista/
│   │   ├── vista_admin.py
│   │   ├── vista_arrendador.py
│   │   ├── vista_cliente.py
│   │   ├── vista_detalle_propiedad.py
│   │   ├── vista_login.py
│   │   └── vista_perfil.py
│   ├── main.py                    # Punto de entrada de la aplicación
│   └── poblar_db.py               # Genera datos de prueba
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
- Tkinter (viene con la mayoría de instalaciones de Python en Windows; en distribuciones 
Linux es necesario instalar el paquete python3-tk desde el gestor de paquetes si no está presente).


## Notas importantes de instalación y ejecución

NOTA PARA USUARIOS DE WINDOWS (Descarga vía ZIP):
Si descargas este repositorio como un archivo .zip en lugar de clonarlo con Git, asegúrate 
de extraerlo en una ruta corta (por ejemplo, C:\homify) y evita dejar la carpeta doblemente 
anidada. Las rutas demasiado largas en Windows rompen la creación del entorno virtual y la 
instalación de dependencias. Además, se recomienda fuertemente utilizar la consola tradicional 
(cmd) en lugar de PowerShell para evitar problemas con las políticas de ejecución de scripts 
al activar el entorno.


## Instalación y primer uso

Abre una terminal en la raíz del proyecto y ejecuta los siguientes comandos en orden para 
preparar el entorno, generar la base de datos e iniciar el sistema.

1. Clonar el repositorio (recomendado)
git clone https://github.com/PabloHernandezMartinez/homify-sistema-rentas.git
cd homify-sistema-rentas

2. Crear entorno virtual
python -m venv env

3. Activar el entorno virtual
En Windows (usar cmd):
env\Scripts\activate

En Linux/macOS:
source env/bin/activate

4. Instalar todas las dependencias exactas
pip install -r requirements.txt

# Si estás en Linux y el comando anterior falla por paquetes específicos de Windows,
# instala manualmente las dependencias principales:
# pip install bcrypt email-validator python-dateutil numpy pandas scikit-learn xgboost matplotlib seaborn geopy joblib jupyter

5. Generar la base de datos de prueba
cd homify
python poblar_db.py

6. Ejecutar la aplicación
python main.py

El comando pip install -r requirements.txt instala automáticamente todas las librerías necesarias
con sus versiones correctas (bcrypt, pandas, xgboost, etc.). No se requiere instalar nada manualmente.

La primera ejecución de poblar_db.py crea:
- datos/sistema.db
- datos/usuarios_credenciales.txt (contraseñas en texto plano, solo para pruebas)

Usa esas credenciales para iniciar sesión. El administrador por defecto es:
  Email: admin@homify.mx
  Password: Admin123!


## Roles y funcionalidades principales

### Cliente
- Explorar inmuebles disponibles con filtros (tipo, precio, recámaras).
- Ver detalle de una propiedad.
- Rentar una propiedad (por días o meses).
- Ver historial de rentas propias y cancelar una renta activa.
- Editar perfil y cambiar contraseña.
- Eliminar cuenta (si no tiene rentas activas).

### Arrendador
- Ver todas sus propiedades y publicar una nueva (casa o departamento).
- Editar, dar de baja o reactivar propiedades.
- Ver las rentas de sus inmuebles, finalizar o cancelar rentas.
- Acceder al dashboard con métricas de ingresos y gráfico de barras.
- Gestionar su perfil.

### Administrador
- Listar todos los usuarios (filtrar por estado y rol).
- Suspender, activar o eliminar usuarios.
- Auditar todos los inmuebles, cambiar disponibilidad o precio.
- Ver y gestionar todas las rentas (finalizar o cancelar).
- Exportar todos los inmuebles a un archivo CSV.
- Editar su perfil.


## Modelo de Machine Learning (carpeta ML)

### Flujo de trabajo

1. El administrador exporta los inmuebles desde la aplicación (CSV).
2. El notebook ETL.ipynb limpia caracteres extraños y unifica direcciones. 
(Debe usarse el dataset generado por la app Homify en el perfil de administrador 
para probarlo; no ejecutar sobre rent_features.csv porque ya está limpio).
3. geolocalizacion.ipynb añade latitud y longitud usando las direcciones. 
(Requiere direcciones reales; con los datos ficticios de prueba no funciona, 
su fin es ilustrar el flujo).
4. EDA.ipynb explora los datos y elimina outliers 
(Se puede utilizar 'rent_features.csv' para ver el flujo de EDA, 
pero el archivo ya esta limpio y es el que se usa en los demás notebooks).
5. modelado_justificacion.ipynb compara modelos y elige XGBoost con hiperparámetros óptimos.
6. modelado_final.ipynb entrena XGBoost, evalúa métricas (R², MAE, RMSE, MAPE) y guarda 
modelo_renta_xgboost_final.pkl y columnas_modelo.json.
7. interfaz_prediccion.py es una aplicación independiente con Tkinter que usa el 
modelo entrenado para predecir el precio de renta de una propiedad.

Para ejecutar la interfaz de predicción:
Asegúrate de tener el entorno virtual (env) activado (ya que requiere librerías como XGBoost y Pandas) y ejecuta:

cd ML
python interfaz_prediccion.py

Introduce las características de la propiedad y obtendrás el precio estimado.


## Archivos importantes

- .gitignore: evita subir la base de datos, credenciales y archivos temporales.
- requirements.txt: lista de librerías con versiones exactas. 
  Si necesitas regenerarlo, activa el entorno virtual y ejecuta pip freeze > requirements.txt.


## Créditos

Proyecto desarrollado como parte de la materia Desarrollo de Aplicaciones para Análisis de Datos.

Estudiantes: 
- Delgado Ramírez Leonardo
- Hernández Martínez Pablo

Profesor: Alejandro López
Escuela: Escuela Superior de Cómputo [ESCOM]