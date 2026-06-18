import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import pandas as pd
import joblib
import json

modelo_path = 'modelo_renta_xgboost_final.pkl'
columnas_path = 'columnas_modelo.json'

try:
    modelo = joblib.load(modelo_path)
    with open(columnas_path, 'r') as f:
        columnas_modelo = json.load(f)
except Exception as e:
    print(f"Asegúrate de tener el modelo y el JSON. Error: {e}")

def predecir_renta(datos):
    entrada = pd.DataFrame([datos])
    entrada = entrada.reindex(columns=columnas_modelo, fill_value=0)
    pred_log = modelo.predict(entrada)
    return np.expm1(pred_log)[0]

root = tk.Tk()
root.title("Predicción de Renta")
root.geometry("480x730")
root.resizable(False, False)

color_fondo = "#F4F6F9"
root.configure(bg=color_fondo)

fuente_normal = ("Helvetica", 10)
fuente_titulo = ("Helvetica", 11, "bold")

m2_terreno_var = tk.DoubleVar(value=65)
m2_construido_var = tk.DoubleVar(value=65)
banos_var = tk.IntVar(value=2)
medios_banos_var = tk.IntVar(value=0)
estacionamientos_var = tk.IntVar(value=0)
antiguedad_var = tk.IntVar(value=5)

alberca_var = tk.BooleanVar(value=False)
cocina_var = tk.BooleanVar(value=True)
amueblado_var = tk.BooleanVar(value=False)
elevador_var = tk.BooleanVar(value=True)
cuarto_servicio_var = tk.BooleanVar(value=True)
depto_var = tk.BooleanVar(value=True)

latitud_var = tk.DoubleVar(value=19.4055)
longitud_var = tk.DoubleVar(value=-99.1848)

resultado_var = tk.StringVar(value="El resultado aparecerá aquí")

def crear_entrada(parent, texto, variable):
    fila = tk.Frame(parent, bg=color_fondo)
    fila.pack(fill="x", pady=4, padx=5)
    
    lbl = ttk.Label(fila, text=texto, width=22, font=fuente_normal, background=color_fondo)
    lbl.pack(side="left")
    
    ent = ttk.Entry(fila, textvariable=variable, width=15, justify="right", font=fuente_normal)
    ent.pack(side="right")
    return ent

frame_numericos = tk.LabelFrame(root, text=" Características Numéricas ", font=fuente_titulo, bg=color_fondo, padx=15, pady=10)
frame_numericos.pack(fill="x", padx=20, pady=10)

crear_entrada(frame_numericos, "m² Terreno:", m2_terreno_var)
crear_entrada(frame_numericos, "m² Construido:", m2_construido_var)
crear_entrada(frame_numericos, "Baños:", banos_var)
crear_entrada(frame_numericos, "Medios Baños:", medios_banos_var)
crear_entrada(frame_numericos, "Estacionamientos:", estacionamientos_var)
crear_entrada(frame_numericos, "Antigüedad (años):", antiguedad_var)

frame_amenidades = tk.LabelFrame(root, text=" Amenidades ", font=fuente_titulo, bg=color_fondo, padx=15, pady=10)
frame_amenidades.pack(fill="x", padx=20, pady=10)

amenidades = [
    ("Alberca", alberca_var),
    ("Cocina integral", cocina_var),
    ("Amueblado", amueblado_var),
    ("Elevador", elevador_var),
    ("Cuarto de servicio", cuarto_servicio_var),
    ("¿Es departamento?", depto_var)
]

frame_grid = tk.Frame(frame_amenidades, bg=color_fondo)
frame_grid.pack(fill="x")

for i, (texto, var) in enumerate(amenidades):
    s = ttk.Style()
    s.configure("TCheckbutton", background=color_fondo)
    cb = ttk.Checkbutton(frame_grid, text=texto, variable=var, style="TCheckbutton")
    cb.grid(row=i//2, column=i%2, sticky="w", padx=10, pady=5)

frame_grid.grid_columnconfigure(0, weight=1)
frame_grid.grid_columnconfigure(1, weight=1)

frame_ubicacion = tk.LabelFrame(root, text=" Ubicación ", font=fuente_titulo, bg=color_fondo, padx=15, pady=10)
frame_ubicacion.pack(fill="x", padx=20, pady=10)

crear_entrada(frame_ubicacion, "Latitud:", latitud_var)
crear_entrada(frame_ubicacion, "Longitud:", longitud_var)

frame_resultado = tk.Frame(root, bg=color_fondo)
frame_resultado.pack(fill="both", expand=True, padx=20, pady=5)

def limpiar_datos():
    m2_terreno_var.set(0.0)
    m2_construido_var.set(0.0)
    banos_var.set(0)
    medios_banos_var.set(0)
    estacionamientos_var.set(0)
    antiguedad_var.set(0)
    
    alberca_var.set(False)
    cocina_var.set(False)
    amueblado_var.set(False)
    elevador_var.set(False)
    cuarto_servicio_var.set(False)
    depto_var.set(False)
    
    latitud_var.set(0.0)
    longitud_var.set(0.0)
    resultado_var.set("El resultado aparecerá aquí")

def realizar_prediccion():
    try:
        terreno = m2_terreno_var.get()
        construido = m2_construido_var.get()
        banos = banos_var.get()
        medios_banos = medios_banos_var.get()
        estacionamientos = estacionamientos_var.get()
        antiguedad = antiguedad_var.get()
        latitud = latitud_var.get()
        longitud = longitud_var.get()

        if terreno < 0 or construido < 0:
            messagebox.showwarning("Dato inválido", "Los metros cuadrados no pueden ser negativos.")
            return
        if banos < 0 or medios_banos < 0 or estacionamientos < 0 or antiguedad < 0:
            messagebox.showwarning("Dato inválido", "Revisa los campos. No puedes tener cantidades negativas en baños, estacionamientos o antigüedad.")
            return
        
        datos = {
            'm2_terreno': terreno,
            'm2_construido': construido,
            'banos': banos,
            'medios_banos': medios_banos,
            'estacionamientos': estacionamientos,
            'antiguedad': antiguedad,
            'amen_Alberca': 1 if alberca_var.get() else 0,
            'amen_Cocina integral': 1 if cocina_var.get() else 0,
            'amen_Amueblado': 1 if amueblado_var.get() else 0,
            'amen_Elevador': 1 if elevador_var.get() else 0,
            'amen_Cuartos de servicio': 1 if cuarto_servicio_var.get() else 0,
            'tipo_propiedad_departamento': 1 if depto_var.get() else 0,
            'latitud': latitud,
            'longitud': longitud
        }
        renta = predecir_renta(datos)
        resultado_var.set(f"Renta estimada:\n${renta:,.2f} MXN")

    except tk.TclError:
        messagebox.showwarning("Formato incorrecto", "Por favor, asegúrate de ingresar solo números válidos y no dejar campos vacíos.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error inesperado al predecir:\n{str(e)}")

frame_botones = tk.Frame(frame_resultado, bg=color_fondo)
frame_botones.pack(pady=5)

btn_limpiar = tk.Button(frame_botones, text="LIMPIAR", command=limpiar_datos,
                        bg="#6C757D", fg="white", font=("Helvetica", 11, "bold"), 
                        relief="flat", cursor="hand2", padx=15, pady=8)
btn_limpiar.pack(side="left", padx=10)

btn_predecir = tk.Button(frame_botones, text="PREDECIR RENTA", command=realizar_prediccion,
                            bg="#007BFF", fg="white", font=("Helvetica", 11, "bold"), 
                            relief="flat", cursor="hand2", padx=15, pady=8)
btn_predecir.pack(side="right", padx=10)

lbl_resultado = tk.Label(frame_resultado, textvariable=resultado_var, font=("Helvetica", 16, "bold"), 
                            bg=color_fondo, fg="#2E4053")
lbl_resultado.pack(pady=15)

root.mainloop()