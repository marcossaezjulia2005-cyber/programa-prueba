import tkinter as tk
from tkinter import messagebox, ttk


class CalculadoraApp:
    """
    Aplicación de calculadora gráfica interactiva construida con Tkinter.
    Permite operar con números enteros y decimales en 5 operaciones distintas,
    con validación de errores y diseño limpio y centrado.
    """

    OPCIONES_OPERACIONES = [
        "Sumar",
        "Restar",
        "Multiplicar",
        "Dividir",
        "Potencia"
    ]

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Calculadora Interactiva")
        self.root.geometry("440x520")
        self.root.minsize(400, 480)
        self.root.configure(bg="#f4f6f9")

        # Centrar la ventana en la pantalla del usuario
        self._centrar_ventana(440, 520)

        # Configurar estilos de ttk
        self._configurar_estilos()

        # Construir los elementos de la interfaz gráfica
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
        """Define la apariencia visual de los widgets ttk."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Estilo del Combobox
        self.style.configure(
            "TCombobox",
            padding=6,
            font=("Segoe UI", 11)
        )

    def _crear_interfaz(self):
        """Crea y organiza todos los widgets de la interfaz gráfica."""
        # Contenedor principal con margen
        contenedor = tk.Frame(self.root, bg="#f4f6f9", padx=25, pady=25)
        contenedor.pack(expand=True, fill="both")

        # Encabezado
        lbl_titulo = tk.Label(
            contenedor,
            text="Calculadora",
            font=("Segoe UI", 20, "bold"),
            bg="#f4f6f9",
            fg="#1a202c"
        )
        lbl_titulo.pack(pady=(0, 5))

        lbl_subtitulo = tk.Label(
            contenedor,
            text="Selecciona una operación e ingresa los valores",
            font=("Segoe UI", 10),
            bg="#f4f6f9",
            fg="#718096"
        )
        lbl_subtitulo.pack(pady=(0, 20))

        # Tarjeta blanca para el formulario
        tarjeta = tk.Frame(
            contenedor,
            bg="#ffffff",
            bd=1,
            relief="solid",
            highlightthickness=0,
            padx=20,
            pady=20
        )
        tarjeta.pack(fill="x")
        tarjeta.config(highlightbackground="#e2e8f0")

        # Grid dentro de la tarjeta
        tarjeta.columnconfigure(0, weight=1)

        # 1. Primer número
        lbl_num1 = tk.Label(
            tarjeta,
            text="Primer número:",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#2d3748",
            anchor="w"
        )
        lbl_num1.pack(fill="x", pady=(0, 4))

        self.entry_num1 = ttk.Entry(tarjeta, font=("Segoe UI", 11))
        self.entry_num1.pack(fill="x", pady=(0, 14), ipady=3)
        self.entry_num1.focus_set()

        # 2. Operación (ttk.Combobox con exactamente 5 opciones)
        lbl_op = tk.Label(
            tarjeta,
            text="Operación:",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#2d3748",
            anchor="w"
        )
        lbl_op.pack(fill="x", pady=(0, 4))

        self.combo_operacion = ttk.Combobox(
            tarjeta,
            values=self.OPCIONES_OPERACIONES,
            state="readonly",
            font=("Segoe UI", 10)
        )
        self.combo_operacion.current(0)  # Por defecto "Sumar"
        self.combo_operacion.pack(fill="x", pady=(0, 14), ipady=2)

        # 3. Segundo número
        lbl_num2 = tk.Label(
            tarjeta,
            text="Segundo número:",
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            fg="#2d3748",
            anchor="w"
        )
        lbl_num2.pack(fill="x", pady=(0, 4))

        self.entry_num2 = ttk.Entry(tarjeta, font=("Segoe UI", 11))
        self.entry_num2.pack(fill="x", pady=(0, 16), ipady=3)

        # Botones de Acción (Calcular y Borrar)
        marco_botones = tk.Frame(tarjeta, bg="#ffffff")
        marco_botones.pack(fill="x", pady=(5, 5))
        marco_botones.columnconfigure(0, weight=1)
        marco_botones.columnconfigure(1, weight=1)

        # 4. Botón Calcular
        btn_calcular = tk.Button(
            marco_botones,
            text="Calcular",
            command=self.calcular,
            font=("Segoe UI", 11, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            pady=8
        )
        btn_calcular.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        # 5. Botón Borrar
        btn_borrar = tk.Button(
            marco_botones,
            text="Borrar",
            command=self.borrar,
            font=("Segoe UI", 11, "bold"),
            bg="#e2e8f0",
            fg="#334155",
            activebackground="#cbd5e1",
            activeforeground="#1e293b",
            relief="flat",
            cursor="hand2",
            pady=8
        )
        btn_borrar.grid(row=0, column=1, padx=(6, 0), sticky="ew")

        # Área visible para el Resultado
        self.marco_resultado = tk.Frame(
            contenedor,
            bg="#e0f2fe",
            bd=1,
            relief="solid",
            padx=15,
            pady=12
        )
        self.marco_resultado.pack(fill="x", pady=(18, 0))

        self.lbl_resultado_texto = tk.Label(
            self.marco_resultado,
            text="Resultado: —",
            font=("Segoe UI", 13, "bold"),
            bg="#e0f2fe",
            fg="#0369a1",
            wraplength=380
        )
        self.lbl_resultado_texto.pack()

        # Permitir calcular al presionar Enter en el teclado
        self.root.bind("<Return>", lambda event: self.calcular())

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
        y actualiza la etiqueta de resultado.
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
                        "Error matemático",
                        "No es posible dividir entre cero. Introduce un divisor diferente.",
                        parent=self.root
                    )
                    return
                resultado = num1 / num2
                simbolo = "÷"
            elif operacion == "Potencia":
                # Control de operaciones complejas o números excesivamente grandes
                try:
                    resultado = num1 ** num2
                except OverflowError:
                    messagebox.showerror(
                        "Error de desbordamiento",
                        "El resultado de la potencia es demasiado grande para representarse.",
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

            # Actualizar etiqueta en pantalla
            self.lbl_resultado_texto.config(
                text=f"{num1_str} {simbolo} {num2_str} = {res_str}",
                fg="#0369a1"
            )

        except Exception as error_inesperado:
            messagebox.showerror(
                "Error en la operación",
                f"Ocurrió un error inesperado: {error_inesperado}",
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
        self.lbl_resultado_texto.config(text="Resultado: —", fg="#0369a1")
        self.entry_num1.focus_set()


def main():
    root = tk.Tk()
    app = CalculadoraApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

