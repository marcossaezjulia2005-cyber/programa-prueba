import tkinter as tk
from tkinter import messagebox


def mostrar_mensaje(label_resultado):
    """
    Función que se ejecuta al presionar el botón de la bandera.
    Actualiza la etiqueta con el mensaje y muestra un messagebox emergente.
    """
    mensaje = "ARRIBA ESPAÑA"
    
    # 1. Mostrar en etiqueta destacada en la ventana
    label_resultado.config(text=f"¡{mensaje}!", fg="#c60b1e")
    
    # 2. Mostrar cuadro de diálogo emergente
    messagebox.showinfo(title="España", message=mensaje)


def centrar_ventana(ventana, ancho, alto):
    """Calcula la posición centrada en la pantalla según la resolución del monitor."""
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    pos_x = (pantalla_ancho // 2) - (ancho // 2)
    pos_y = (pantalla_alto // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")


def crear_boton_bandera(parent, comando):
    """
    Crea un botón personalizado tipo tarjeta usando tk.Canvas donde se
    dibuja directamente la bandera de España con sus proporciones oficiales
    (rojo 1/4, amarillo 2/4, rojo 1/4) y el texto integrado 'Apriétame'.
    """
    ancho_btn = 260
    alto_btn = 120
    
    # Colores oficiales de la bandera de España
    color_rojo = "#c60b1e"
    color_amarillo = "#ffc400"
    color_borde = "#8a0815"
    
    # Canvas interactivo que actúa como botón
    canvas_boton = tk.Canvas(
        parent,
        width=ancho_btn,
        height=alto_btn,
        bd=0,
        highlightthickness=3,
        highlightbackground=color_borde,
        relief="raised",
        cursor="hand2"
    )

    # Franjas: 1:2:1 (superior 30px, central 60px, inferior 30px)
    h_rojo = alto_btn // 4          # 30 px
    h_amarillo = alto_btn - h_rojo   # 90 px

    # Franja superior roja
    canvas_boton.create_rectangle(
        0, 0, ancho_btn, h_rojo,
        fill=color_rojo, outline=""
    )

    # Franja central amarilla (el doble de ancho que las rojas)
    canvas_boton.create_rectangle(
        0, h_rojo, ancho_btn, h_amarillo,
        fill=color_amarillo, outline=""
    )

    # Franja inferior roja
    canvas_boton.create_rectangle(
        0, h_amarillo, ancho_btn, alto_btn,
        fill=color_rojo, outline=""
    )

    # Sombra del texto para mayor contraste y legibilidad
    canvas_boton.create_text(
        (ancho_btn // 2) + 1, (alto_btn // 2) + 1,
        text="Apriétame",
        font=("Arial", 18, "bold"),
        fill="#5a3d00"
    )

    # Texto integrado en el botón
    canvas_boton.create_text(
        ancho_btn // 2, alto_btn // 2,
        text="Apriétame",
        font=("Arial", 18, "bold"),
        fill="#8a0815"
    )

    # Efecto visual al hacer clic (presionado)
    def al_presionar(event):
        canvas_boton.config(relief="sunken")

    # Efecto al soltar y ejecución del evento
    def al_soltar(event):
        canvas_boton.config(relief="raised")
        # Verificar que el cursor se haya soltado dentro del botón
        if 0 <= event.x <= ancho_btn and 0 <= event.y <= alto_btn:
            comando()

    # Vinculación de eventos de clic
    canvas_boton.bind("<Button-1>", al_presionar)
    canvas_boton.bind("<ButtonRelease-1>", al_soltar)

    return canvas_boton


def main():
    # 1. Ventana principal
    ventana = tk.Tk()
    ventana.title("Aplicación España")
    ventana.configure(bg="#f4f5f7")  # Fondo limpio y neutro
    ventana.resizable(False, False)

    # Centrado en pantalla (420x350)
    centrar_ventana(ventana, 420, 350)

    # Contenedor central
    marco_principal = tk.Frame(ventana, bg="#f4f5f7", padx=20, pady=25)
    marco_principal.pack(expand=True, fill="both")

    # Subtítulo explicativo
    label_instruccion = tk.Label(
        marco_principal,
        text="Haz clic en la bandera para continuar",
        font=("Segoe UI", 11),
        bg="#f4f5f7",
        fg="#555555"
    )
    label_instruccion.pack(pady=(0, 15))

    # 3. Etiqueta para mostrar el mensaje tras la interacción
    label_resultado = tk.Label(
        marco_principal,
        text="",
        font=("Segoe UI", 18, "bold"),
        bg="#f4f5f7"
    )

    # 2. Botón principal con la bandera de España dibujada directamente
    boton_bandera = crear_boton_bandera(
        marco_principal,
        comando=lambda: mostrar_mensaje(label_resultado)
    )
    boton_bandera.pack(pady=10)

    # Colocar la etiqueta de resultado debajo del botón
    label_resultado.pack(pady=(20, 5))

    # Bucle principal de la GUI
    ventana.mainloop()


if __name__ == "__main__":
    main()
