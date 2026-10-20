import tkinter as tk
from tkinter import messagebox

def convertir():
    try:
        # Obtener el valor ingresado
        valor_texto = entrada_valor.get().strip()
        if not valor_texto:
            messagebox.showwarning("Advertencia", "Por favor, introduce un valor.")
            return
            
        valor = float(valor_texto)
        origen = combo_origen.get()
        destino = combo_destino.get()
        
        # 1. Convertir todo primero a metros como unidad base
        if origen == "Milímetros":
            en_metros = valor / 1000.0
        elif origen == "Centímetros":
            en_metros = valor / 100.0
        else:  # Metros
            en_metros = valor
            
        # 2. Convertir de metros a la unidad de destino
        if destino == "Milímetros":
            resultado = en_metros * 1000.0
        elif destino == "Centímetros":
            resultado = en_metros * 100.0
        else:  # Metros
            resultado = en_metros
            
        # Mostrar el resultado
        etiqueta_resultado.config(text=f"Resultado: {resultado:g} {destino}")
        
    except ValueError:
        messagebox.showerror("Error", "Por favor, introduce un número válido.")

def limpiar():
    entrada_valor.delete(0, tk.END)
    combo_origen.set("Milímetros")
    combo_destino.set("Centímetros")
    etiqueta_resultado.config(text="Resultado: ")

# --- Configuración de la Ventana Principal ---
ventana = tk.Tk()
ventana.title("Conversor de Unidades")
ventana.geometry("360x320")
ventana.config(bg="#f4f4f9")
ventana.resizable(False, False)

# Estilos comunes
fuente_principal = ("Arial", 11)

# Título
titulo = tk.Label(ventana, text="Conversor de Longitud", font=("Arial", 14, "bold"), bg="#f4f4f9", fg="#333333")
titulo.pack(pady=15)

# Marco para el valor de entrada
marco_entrada = tk.Frame(ventana, bg="#f4f4f9")
marco_entrada.pack(pady=5)

tk.Label(marco_entrada, text="Valor:", font=fuente_principal, bg="#f4f4f9").pack(side=tk.LEFT, padx=5)
entrada_valor = tk.Entry(marco_entrada, font=fuente_principal, width=12)
entrada_valor.pack(side=tk.LEFT, padx=5)

# Marco para Origen y Destino
marco_selectores = tk.Frame(ventana, bg="#f4f4f9")
marco_selectores.pack(pady=10)

# Origen
tk.Label(marco_selectores, text="De:", font=fuente_principal, bg="#f4f4f9").grid(row=0, column=0, padx=5, sticky="w")
unidades = ["Milímetros", "Centímetros", "Metros"]
combo_origen = tk.StringVar(ventana)
combo_origen.set(unidades[0])
menu_origen = tk.OptionMenu(marco_selectores, combo_origen, *unidades)
menu_origen.config(font=fuente_principal, width=10)
menu_origen.grid(row=0, column=1, padx=5)

# Destino
tk.Label(marco_selectores, text="A:", font=fuente_principal, bg="#f4f4f9").grid(row=1, column=0, padx=5, sticky="w", pady=5)
combo_destino = tk.StringVar(ventana)
combo_destino.set(unidades[1])
menu_destino = tk.OptionMenu(marco_selectores, combo_destino, *unidades)
menu_destino.config(font=fuente_principal, width=10)
menu_destino.grid(row=1, column=1, padx=5, pady=5)

# Marco para los botones
marco_botones = tk.Frame(ventana, bg="#f4f4f9")
marco_botones.pack(pady=10)

btn_convertir = tk.Button(marco_botones, text="Convertir", font=fuente_principal, bg="#4CAF50", fg="white", width=9, command=convertir)
btn_convertir.pack(side=tk.LEFT, padx=5)

btn_limpiar = tk.Button(marco_botones, text="Limpiar", font=fuente_principal, bg="#f44336", fg="white", width=9, command=limpiar)
btn_limpiar.pack(side=tk.LEFT, padx=5)

# Etiqueta de Resultado
etiqueta_resultado = tk.Label(ventana, text="Resultado: ", font=("Arial", 12, "bold"), bg="#f4f4f9", fg="#2196F3")
etiqueta_resultado.pack(pady=15)

# Ejecutar la aplicación
ventana.mainloop()