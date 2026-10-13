import math
import os
import tkinter as tk
from tkinter import messagebox, ttk

# Detección y soporte de Pillow para cargar o regenerar los gráficos de Rayo McQueen
try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageTk
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False

# Rutas de recursos dentro del directorio del programa
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONDO_PATH = os.path.join(BASE_DIR, "fondo_mcqueen.png")
MCQUEEN_PATH = os.path.join(BASE_DIR, "mcqueen.png")


def generar_fondo_mcqueen():
    """
    Genera el fondo temático de Rayo McQueen en alta resolución
    si no existe previamente en la carpeta del programa.
    """
    if not PIL_DISPONIBLE:
        return None

    w, h = 480, 700
    base = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    draw = ImageDraw.Draw(base)

    # 1. Degradado estilo carrocería de carreras (Carmesí oscuro a Rojo Rayo a Asfalto)
    for y in range(h):
        t = y / h
        if t < 0.30:
            sub_t = t / 0.30
            r = int(150 + (225 - 150) * sub_t)
            g = int(0 + 10 * sub_t)
            b = int(12 + 18 * sub_t)
        elif t < 0.60:
            sub_t = (t - 0.30) / 0.30
            r = int(225 + (90 - 225) * sub_t)
            g = int(10 + 10 * sub_t)
            b = int(30 + 5 * sub_t)
        else:
            sub_t = (t - 0.60) / 0.40
            r = int(90 + (22 - 90) * sub_t)
            g = int(20 + (20 - 20) * sub_t)
            b = int(35 + (25 - 35) * sub_t)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # 2. Líneas diagonales de velocidad
    stripe_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(stripe_layer)
    for i in range(-120, w + 220, 42):
        sdraw.polygon([
            (i, 0), (i + 14, 0), (i - 75, h), (i - 89, h)
        ], fill=(255, 215, 0, 16))
    base = Image.alpha_composite(base, stripe_layer)

    # 3. Franjas a cuadros de meta (Checkered Flag) en la parte superior e inferior
    cw, ch = 16, 12
    draw = ImageDraw.Draw(base)
    for y_start, rows in [(0, 2), (h - 24, 2)]:
        for r_idx in range(rows):
            y1 = y_start + r_idx * ch
            y2 = y1 + ch
            for col in range(0, w + cw, cw):
                fill_col = (255, 255, 255, 235) if ((col // cw) + r_idx) % 2 == 0 else (15, 15, 15, 235)
                draw.rectangle([col, y1, col + cw, y2], fill=fill_col)

    # 4. Rayo amarillo brillante detrás de McQueen
    bolt_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(bolt_layer)
    bolt_pts = [
        (w - 35, 26), (w - 135, 115), (w - 95, 115),
        (w - 200, 205), (w - 80, 130), (w - 115, 130), (w - 25, 26)
    ]
    bdraw.polygon(bolt_pts, fill=(255, 215, 0, 225))
    bdraw.polygon(bolt_pts, outline=(255, 90, 0, 255), width=2)

    # Rayo lateral izquierdo menor
    bolt2_pts = [
        (40, 35), (95, 95), (75, 95),
        (140, 160), (60, 105), (80, 105), (30, 35)
    ]
    bdraw.polygon(bolt2_pts, fill=(255, 200, 0, 140))
    base = Image.alpha_composite(base, bolt_layer)

    # 5. Rayo McQueen con sombra suave
    if os.path.exists(MCQUEEN_PATH):
        try:
            mc = Image.open(MCQUEEN_PATH).convert("RGBA")
            w_target = 265
            h_target = int(mc.height * (w_target / mc.width))
            mc_res = mc.resize((w_target, h_target), Image.LANCZOS)

            shadow = Image.new("RGBA", (w_target + 40, h_target + 40), (0, 0, 0, 0))
            s_draw = ImageDraw.Draw(shadow)
            s_draw.ellipse([20, h_target - 8, w_target + 20, h_target + 24], fill=(0, 0, 0, 190))
            shadow = shadow.filter(ImageFilter.GaussianBlur(12))

            pos_x = (w - w_target) // 2
            pos_y = 36
            base.paste(shadow, (pos_x - 20, pos_y - 20), shadow)
            base.paste(mc_res, (pos_x, pos_y), mc_res)
        except Exception:
            pass

    try:
        base.save(FONDO_PATH)
        return FONDO_PATH
    except Exception:
        return None


class CalculadoraApp:
    """
    Aplicación de calculadora gráfica interactiva con la temática de Rayo McQueen #95.
    Permite operar con números enteros y decimales en 5 operaciones matemáticas,
    con diseño de panel de telemetría de carreras y fondo ilustrado de Rayo McQueen.
    """

    OPCIONES_OPERACIONES = [
        "Sumar",
        "Restar",
        "Multiplicar",
        "Dividir",
        "Potencia"
    ]

    ANCHO_VENTANA = 480
    ALTO_VENTANA = 700

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("⚡ Calculadora Rayo McQueen #95 ⚡")
        self.root.geometry(f"{self.ANCHO_VENTANA}x{self.ALTO_VENTANA}")
        self.root.resizable(False, False)
        self.root.configure(bg="#990000")

        # Mantener referencia de la imagen de fondo en memoria para evitar el recolector de basura
        self.bg_photo = None

        # Centrar la ventana en la pantalla del usuario
        self._centrar_ventana(self.ANCHO_VENTANA, self.ALTO_VENTANA)

        # Configurar estilos de ttk
        self._configurar_estilos()

        # Construir interfaz gráfica con el fondo temático
        self._crear_interfaz()

    def _centrar_ventana(self, ancho: int, alto: int):
        """Calcula y establece la posición para centrar la ventana en el monitor."""
        self.root.update_idletasks()
        pantalla_ancho = self.root.winfo_screenwidth()
        pantalla_alto = self.root.winfo_screenheight()
        pos_x = (pantalla_ancho // 2) - (ancho // 2)
        pos_y = (pantalla_alto // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")

    def _configurar_estilos(self):
        """Define la apariencia visual de los widgets ttk con la estética NASCAR."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Estilo del Combobox
        self.style.configure(
            "TCombobox",
            padding=6,
            font=("Segoe UI", 10, "bold"),
            fieldbackground="#ffffff",
            background="#ffd000"
        )

        # Estilo de campos de texto
        self.style.configure(
            "TEntry",
            padding=6,
            font=("Segoe UI", 11)
        )

    def _crear_interfaz(self):
        """Crea el fondo ilustrado y organiza todos los widgets de la calculadora."""
        # 1. Canvas principal que contiene el fondo
        self.canvas = tk.Canvas(
            self.root,
            width=self.ANCHO_VENTANA,
            height=self.ALTO_VENTANA,
            highlightthickness=0,
            bg="#990000"
        )
        self.canvas.pack(fill="both", expand=True)

        # 2. Cargar imagen de fondo si está disponible
        fondo_cargado = False
        if not os.path.exists(FONDO_PATH) and PIL_DISPONIBLE:
            generar_fondo_mcqueen()

        if PIL_DISPONIBLE and os.path.exists(FONDO_PATH):
            try:
                img_pil = Image.open(FONDO_PATH)
                if img_pil.size != (self.ANCHO_VENTANA, self.ALTO_VENTANA):
                    img_pil = img_pil.resize((self.ANCHO_VENTANA, self.ALTO_VENTANA), Image.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(img_pil)
                self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
                fondo_cargado = True
            except Exception:
                fondo_cargado = False

        # Si no hay imagen disponible, dibujamos un fondo nativo vectorial de carreras
        if not fondo_cargado:
            self._dibujar_fondo_vectorial()

        # 3. Títulos y marcas de Rayo McQueen
        self.canvas.create_text(
            self.ANCHO_VENTANA // 2,
            195,
            text="⚡ RAYO McQUEEN #95 ⚡",
            font=("Impact", 22),
            fill="#FFD000"
        )
        self.canvas.create_text(
            self.ANCHO_VENTANA // 2,
            222,
            text="«¡Ka-Chow!» ⚡ Copa Pistón",
            font=("Segoe UI", 10, "bold italic"),
            fill="#FFFFFF"
        )

        # 4. Tarjeta del panel de instrumentos (estilo consola de carreras en fibra de carbono/asfalto)
        tarjeta = tk.Frame(
            self.canvas,
            bg="#18181b",
            bd=2,
            relief="solid",
            highlightthickness=1,
            highlightbackground="#FFD000",
            padx=20,
            pady=16
        )
        # Posicionamos la tarjeta en el centro de la pantalla
        self.canvas.create_window(
            self.ANCHO_VENTANA // 2,
            445,
            window=tarjeta,
            width=420
        )

        # Primer número
        lbl_num1 = tk.Label(
            tarjeta,
            text="⚡ Primer número:",
            font=("Segoe UI", 10, "bold"),
            bg="#18181b",
            fg="#FFD000",
            anchor="w"
        )
        lbl_num1.pack(fill="x", pady=(0, 2))

        self.entry_num1 = ttk.Entry(tarjeta, font=("Segoe UI", 11))
        self.entry_num1.pack(fill="x", pady=(0, 10), ipady=3)
        self.entry_num1.focus_set()

        # Operación matemática (ttk.Combobox)
        lbl_op = tk.Label(
            tarjeta,
            text="🏁 Operación (Copa Pistón):",
            font=("Segoe UI", 10, "bold"),
            bg="#18181b",
            fg="#FFD000",
            anchor="w"
        )
        lbl_op.pack(fill="x", pady=(0, 2))

        self.combo_operacion = ttk.Combobox(
            tarjeta,
            values=self.OPCIONES_OPERACIONES,
            state="readonly",
            font=("Segoe UI", 10, "bold")
        )
        self.combo_operacion.current(0)  # Por defecto "Sumar"
        self.combo_operacion.pack(fill="x", pady=(0, 10), ipady=2)

        # Segundo número
        lbl_num2 = tk.Label(
            tarjeta,
            text="⚡ Segundo número:",
            font=("Segoe UI", 10, "bold"),
            bg="#18181b",
            fg="#FFD000",
            anchor="w"
        )
        lbl_num2.pack(fill="x", pady=(0, 2))

        self.entry_num2 = ttk.Entry(tarjeta, font=("Segoe UI", 11))
        self.entry_num2.pack(fill="x", pady=(0, 14), ipady=3)

        # Botones de Acción (Acelerar / Calcular y Pits / Borrar)
        marco_botones = tk.Frame(tarjeta, bg="#18181b")
        marco_botones.pack(fill="x", pady=(0, 10))
        marco_botones.columnconfigure(0, weight=1)
        marco_botones.columnconfigure(1, weight=1)

        # Botón ¡Acelerar! (Calcular) - Rojo fuego McQueen
        btn_calcular = tk.Button(
            marco_botones,
            text="⚡ ¡ACELERAR! ⚡",
            command=self.calcular,
            font=("Segoe UI", 10, "bold"),
            bg="#DC2626",
            fg="#FFFFFF",
            activebackground="#B91C1C",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            pady=8
        )
        btn_calcular.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        # Botón Pits (Borrar) - Asfalto de pista
        btn_borrar = tk.Button(
            marco_botones,
            text="🔄 PITS (Borrar)",
            command=self.borrar,
            font=("Segoe UI", 10, "bold"),
            bg="#27272A",
            fg="#E4E4E7",
            activebackground="#3F3F46",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            pady=8
        )
        btn_borrar.grid(row=0, column=1, padx=(6, 0), sticky="ew")

        # Pantalla digital de telemetría para el Resultado
        self.marco_resultado = tk.Frame(
            tarjeta,
            bg="#09090B",
            bd=1,
            relief="solid",
            highlightthickness=1,
            highlightbackground="#F59E0B",
            padx=12,
            pady=10
        )
        self.marco_resultado.pack(fill="x", pady=(4, 0))

        self.lbl_resultado_texto = tk.Label(
            self.marco_resultado,
            text="Resultado: ⚡ ¡Ka-Chow! ⚡",
            font=("Segoe UI", 12, "bold"),
            bg="#09090B",
            fg="#FFD000",
            wraplength=370
        )
        self.lbl_resultado_texto.pack()

        # Permitir calcular al presionar Enter en el teclado
        self.root.bind("<Return>", lambda event: self.calcular())

    def _dibujar_fondo_vectorial(self):
        """Dibuja elementos gráficos temáticos si la imagen de fondo no está disponible."""
        # Rayo decorativo en Canvas
        self.canvas.create_polygon(
            445, 26, 345, 115, 385, 115, 280, 205, 400, 130, 365, 130, 455, 26,
            fill="#FFD000", outline="#FF6A00", width=2
        )
        # Líneas de bandera a cuadros
        cw = 16
        for col in range(0, self.ANCHO_VENTANA + cw, cw):
            color = "#FFFFFF" if (col // cw) % 2 == 0 else "#111111"
            self.canvas.create_rectangle(col, 0, col + cw, 18, fill=color, outline="")
            self.canvas.create_rectangle(col, self.ALTO_VENTANA - 18, col + cw, self.ALTO_VENTANA, fill=color, outline="")

    def _parsear_numero(self, texto: str, nombre_campo: str) -> float:
        """
        Valida y convierte el texto a float. Admite formatos con punto o coma.
        Lanza ValueError si el valor no es un número válido.
        """
        texto_limpio = texto.strip().replace(",", ".")
        if not texto_limpio:
            raise ValueError(f"El campo '{nombre_campo}' no puede estar vacío.")

        try:
            return float(texto_limpio)
        except ValueError:
            raise ValueError(f"El valor '{texto.strip()}' en '{nombre_campo}' no es un número válido.")

    def calcular(self):
        """
        Valida las entradas, realiza la operación matemática seleccionada
        y actualiza la pantalla de telemetría de resultado con estilo Ka-Chow.
        """
        # 1. Validación de entradas numéricas
        try:
            num1 = self._parsear_numero(self.entry_num1.get(), "Primer número")
            num2 = self._parsear_numero(self.entry_num2.get(), "Segundo número")
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e), parent=self.root)
            return

        operacion = self.combo_operacion.get()

        # 2. Ejecución de la operación seleccionada
        try:
            if operacion == "Sumar":
                resultado = num1 + num2
                simbolo = "+"
            elif operacion == "Restar":
                resultado = num1 - num2
                simbolo = "-"
            elif operacion == "Multiplicar":
                resultado = num1 * num2
                simbolo = "×"
            elif operacion == "Dividir":
                if num2 == 0:
                    messagebox.showerror(
                        "Error en la Pista",
                        "¡Alerta en pits! No es posible dividir entre cero. Introduce un divisor diferente.",
                        parent=self.root
                    )
                    return
                resultado = num1 / num2
                simbolo = "÷"
            elif operacion == "Potencia":
                try:
                    resultado = num1 ** num2
                except OverflowError:
                    messagebox.showerror(
                        "Motor sobrecalentado",
                        "El resultado de la potencia sobrepasa la velocidad máxima permitida (demasiado grande).",
                        parent=self.root
                    )
                    return
                simbolo = "^"
            else:
                messagebox.showerror("Error", "Operación no reconocida.", parent=self.root)
                return

            # Formateo limpio de enteros vs decimales (ej. 4.0 -> 4)
            res_str = f"{resultado:g}"
            num1_str = f"{num1:g}"
            num2_str = f"{num2:g}"

            # Actualizar telemetría de resultado en pantalla con estilo Rayo McQueen
            self.lbl_resultado_texto.config(
                text=f"{num1_str} {simbolo} {num2_str} = {res_str}  ⚡ ¡Ka-Chow!",
                fg="#FFD000"
            )

        except Exception as error_inesperado:
            messagebox.showerror(
                "Error en pits",
                f"Ocurrió un problema inesperado: {error_inesperado}",
                parent=self.root
            )

    def borrar(self):
        """
        Limpia los campos de entrada, restablece la operación por defecto
        y borra el texto del resultado.
        """
        self.entry_num1.delete(0, tk.END)
        self.entry_num2.delete(0, tk.END)
        self.combo_operacion.current(0)  # Restablecer a 'Sumar'
        self.lbl_resultado_texto.config(text="Resultado: ⚡ ¡Ka-Chow! ⚡", fg="#FFD000")
        self.entry_num1.focus_set()


def main():
    root = tk.Tk()
    app = CalculadoraApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
