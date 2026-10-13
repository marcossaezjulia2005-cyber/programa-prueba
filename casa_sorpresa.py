"""
=============================================================================
Aplicación Interactiva: La Casa Sorpresa Musical
=============================================================================
Descripción:
    Al hacer clic en el botón morado, se anima la apertura de las puertas
    de la casa en el Canvas y SUENA DIRECTAMENTE LA CANCIÓN en tu ordenador,
    sin necesidad de abrir navegadores externos.
    Incluye ecualizador gráfico animado, control de reproducción y pausa/stop.

Audio:
    cancion.wav (generado localmente)
=============================================================================
"""

import math
import os
import random
import sys
import tkinter as tk
from tkinter import messagebox
import winsound


# Ruta del archivo de audio local
RUTA_AUDIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cancion.wav")


class CasaSorpresaApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("La Casa Sorpresa Musical")
        self.root.geometry("620x740")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")

        # Centrar ventana
        self._centrar_ventana(620, 740)

        # Estados de animación y audio
        self.reproduciendo_audio = False
        self.puerta_abierta = False
        self.angulo_apertura = 0.0
        self.animando_puerta = False
        self.barras_ecualizador = [10] * 8  # Alturas para el ecualizador gráfico

        # Construir interfaz
        self._crear_interfaz()

        # Detener audio al cerrar ventana
        self.root.protocol("WM_DELETE_WINDOW", self._cerrar_aplicacion)

    def _centrar_ventana(self, ancho: int, alto: int):
        self.root.update_idletasks()
        pantalla_w = self.root.winfo_screenwidth()
        pantalla_h = self.root.winfo_screenheight()
        pos_x = (pantalla_w // 2) - (ancho // 2)
        pos_y = (pantalla_h // 2) - (alto // 2)
        self.root.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")

    def _crear_interfaz(self):
        # 1. Encabezado
        self.marco_top = tk.Frame(self.root, bg="#0f172a", pady=12)
        self.marco_top.pack(fill="x")

        lbl_titulo = tk.Label(
            self.marco_top,
            text="✨ La Casa del Ritmo ✨",
            font=("Segoe UI", 20, "bold"),
            bg="#0f172a",
            fg="#f8fafc"
        )
        lbl_titulo.pack()

        lbl_desc = tk.Label(
            self.marco_top,
            text="Abre las puertas para escuchar la música en directo",
            font=("Segoe UI", 11),
            bg="#0f172a",
            fg="#94a3b8"
        )
        lbl_desc.pack(pady=(2, 8))

        # 2. Marco con Botón Morado y controles
        self.marco_controles = tk.Frame(self.marco_top, bg="#0f172a")
        self.marco_controles.pack()

        # Botón Morado Principal
        self.btn_morado = tk.Button(
            self.marco_controles,
            text="🚪 Abrir la Casa y Escuchar Música",
            command=self.activar_casa,
            font=("Segoe UI", 12, "bold"),
            bg="#7c3aed",
            fg="#ffffff",
            activebackground="#6d28d9",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=20,
            pady=9,
            cursor="hand2"
        )
        self.btn_morado.pack(side="left", padx=5)

        # Efecto hover
        self.btn_morado.bind("<Enter>", lambda e: self.btn_morado.config(bg="#8b5cf6"))
        self.btn_morado.bind("<Leave>", lambda e: self.btn_morado.config(bg="#7c3aed"))

        # Botón Detener Música (inicialmente oculto o deshabilitado)
        self.btn_stop = tk.Button(
            self.marco_controles,
            text="⏹ Detener",
            command=self.detener_musica,
            font=("Segoe UI", 11, "bold"),
            bg="#ef4444",
            fg="#ffffff",
            activebackground="#dc2626",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=15,
            pady=9,
            cursor="hand2",
            state="disabled"
        )
        self.btn_stop.pack(side="left", padx=5)

        # 3. Canvas para dibujar la casa, puertas y ecualizador
        self.canvas_w = 540
        self.canvas_h = 440
        self.canvas = tk.Canvas(
            self.root,
            width=self.canvas_w,
            height=self.canvas_h,
            bg="#1e293b",
            highlightthickness=2,
            highlightbackground="#334155"
        )
        self.canvas.pack(pady=(5, 12))

        # Mensaje de bienvenida inicial
        self.dibujar_mensaje_espera()

        # Clic en el canvas
        self.canvas.bind("<Button-1>", self._click_canvas)

        # 4. Barra de estado inferior
        self.lbl_estado = tk.Label(
            self.root,
            text="Pulsa el botón morado para abrir la casa y escuchar la canción.",
            font=("Segoe UI", 10, "italic"),
            bg="#0f172a",
            fg="#cbd5e1"
        )
        self.lbl_estado.pack()

    def dibujar_mensaje_espera(self):
        """Pantalla inicial del canvas."""
        self.canvas.delete("all")
        cx = self.canvas_w // 2
        cy = self.canvas_h // 2
        self.canvas.create_text(
            cx, cy - 25,
            text="🏠",
            font=("Segoe UI Emoji", 58),
            fill="#a855f7"
        )
        self.canvas.create_text(
            cx, cy + 45,
            text="La casa está en silencio...\nPresiona el botón morado arriba",
            font=("Segoe UI", 13, "bold"),
            fill="#94a3b8",
            justify="center"
        )

    def activar_casa(self):
        """Abre la casa y reproduce la música."""
        if self.animando_puerta:
            return

        self.btn_morado.config(state="disabled", text="✨ Abriendo y Sonando ✨")
        self.lbl_estado.config(text="Abriendo las puertas y activando el sonido...", fg="#a855f7")
        self.animando_puerta = True
        self.angulo_apertura = 0.0

        # Iniciar animación de la puerta
        self._animar_apertura()

    def _animar_apertura(self):
        self.angulo_apertura += 0.06
        self.dibujar_casa_completa(self.angulo_apertura)

        if self.angulo_apertura < 1.0:
            self.root.after(30, self._animar_apertura)
        else:
            self.angulo_apertura = 1.0
            self.animando_puerta = False
            self.puerta_abierta = True
            self.btn_morado.config(state="normal", text="🔄 Reiniciar Canción")
            self.btn_stop.config(state="normal")
            self.lbl_estado.config(
                text="🎵 ¡Sonando en directo! (Puedes hacer clic en el altavoz dentro de la casa)",
                fg="#4ade80"
            )

            # Iniciar reproducción de audio local y el ecualizador visual
            self.reproducir_musica()

    def reproducir_musica(self):
        """Reproduce el archivo WAV en bucle asíncrono en segundo plano."""
        if not os.path.exists(RUTA_AUDIO):
            messagebox.showerror(
                "Archivo de audio no encontrado",
                f"No se ha encontrado el archivo:\n{RUTA_AUDIO}",
                parent=self.root
            )
            return

        try:
            # SND_ASYNC (asíncrono, no congela la UI) | SND_LOOP (reproduce en bucle)
            winsound.PlaySound(RUTA_AUDIO, winsound.SND_ASYNC | winsound.SND_LOOP)
            self.reproduciendo_audio = True
            self.btn_stop.config(state="normal")
            self._actualizar_ecualizador()
        except Exception as e:
            messagebox.showerror("Error de sonido", f"No se pudo reproducir el audio: {e}", parent=self.root)

    def detener_musica(self):
        """Detiene inmediatamente el audio."""
        winsound.PlaySound(None, winsound.SND_PURGE)
        self.reproduciendo_audio = False
        self.btn_stop.config(state="disabled")
        self.lbl_estado.config(text="Música en pausa. Pulsa el botón morado para volver a reproducir.", fg="#94a3b8")
        self.dibujar_casa_completa(1.0)

    def _actualizar_ecualizador(self):
        """Genera animación dinámica de barras de sonido al ritmo de la música."""
        if self.reproduciendo_audio and self.puerta_abierta:
            self.barras_ecualizador = [random.randint(8, 48) for _ in range(8)]
            self.dibujar_casa_completa(1.0)
            self.root.after(80, self._actualizar_ecualizador)

    def dibujar_casa_completa(self, factor_apertura: float):
        self.canvas.delete("all")

        cx = self.canvas_w // 2
        suelo_y = 400
        ancho_casa = 360
        alto_pared = 210
        base_x1 = cx - ancho_casa // 2
        base_x2 = cx + ancho_casa // 2
        pared_y_top = suelo_y - alto_pared

        # 1. Césped / Suelo
        self.canvas.create_rectangle(0, suelo_y, self.canvas_w, self.canvas_h, fill="#0f172a", outline="")
        self.canvas.create_line(0, suelo_y, self.canvas_w, suelo_y, fill="#334155", width=3)

        # 2. Chimenea
        ch_x = base_x2 - 70
        ch_y = pared_y_top - 90
        self.canvas.create_rectangle(ch_x, ch_y, ch_x + 35, pared_y_top, fill="#991b1b", outline="#7f1d1d", width=2)
        # Humo
        self.canvas.create_oval(ch_x + 8, ch_y - 18, ch_x + 26, ch_y - 4, fill="#64748b", outline="")

        # 3. Fachada de la casa
        self.canvas.create_rectangle(base_x1, pared_y_top, base_x2, suelo_y, fill="#e2e8f0", outline="#64748b", width=3)

        # 4. Tejado triangular
        puntas_techo = [
            cx, pared_y_top - 120,
            base_x1 - 25, pared_y_top,
            base_x2 + 25, pared_y_top
        ]
        self.canvas.create_polygon(puntas_techo, fill="#dc2626", outline="#991b1b", width=3)
        self.canvas.create_line(base_x1 - 25, pared_y_top, base_x2 + 25, pared_y_top, fill="#7f1d1d", width=4)

        # 5. Ventana superior
        v_cx = cx
        v_cy = pared_y_top - 45
        v_r = 22
        color_luz = "#fef08a" if self.reproduciendo_audio else "#94a3b8"
        self.canvas.create_oval(v_cx - v_r, v_cy - v_r, v_cx + v_r, v_cy + v_r, fill=color_luz, outline="#991b1b", width=3)
        self.canvas.create_line(v_cx - v_r, v_cy, v_cx + v_r, v_cy, fill="#991b1b", width=2)
        self.canvas.create_line(v_cx, v_cy - v_r, v_cx, v_cy + v_r, fill="#991b1b", width=2)

        # Notas musicales flotando del tejado si está sonando
        if self.reproduciendo_audio:
            self.canvas.create_text(base_x1 + 30, pared_y_top - 30, text="🎵", font=("Segoe UI Emoji", 20), fill="#a855f7")
            self.canvas.create_text(base_x2 - 20, pared_y_top - 50, text="🎶", font=("Segoe UI Emoji", 22), fill="#ec4899")

        # 6. Habitación interior
        puerta_w = 170
        puerta_h = 165
        p_x1 = cx - puerta_w // 2
        p_x2 = cx + puerta_w // 2
        p_y1 = suelo_y - puerta_h
        p_y2 = suelo_y

        self.canvas.create_rectangle(p_x1, p_y1, p_x2, p_y2, fill="#0b0f19", outline="#3b82f6", width=2)

        # --- INTERIOR: ALTAVOZ Y ECUALIZADOR ANIMADO ---
        if factor_apertura > 0.2:
            # Cabina musical / equipo de sonido
            eq_y_base = p_y2 - 25
            eq_x_inicio = p_x1 + 22
            ancho_barra = 12
            espacio_barra = 4

            # Dibujar barras del ecualizador
            for i, altura in enumerate(self.barras_ecualizador):
                bx = eq_x_inicio + i * (ancho_barra + espacio_barra)
                h = altura if self.reproduciendo_audio else 6
                # Degradado de color
                color_barra = "#ec4899" if i % 2 == 0 else "#a855f7"
                self.canvas.create_rectangle(
                    bx, eq_y_base - h, bx + ancho_barra, eq_y_base,
                    fill=color_barra, outline=""
                )

            # Icono altavoz central
            altavoz_y = p_y1 + 45
            self.canvas.create_text(
                cx, altavoz_y,
                text="🔊" if self.reproduciendo_audio else "🔈",
                font=("Segoe UI Emoji", 32)
            )
            texto_estado_musica = "EN DIRECTO" if self.reproduciendo_audio else "PAUSA"
            color_txt = "#4ade80" if self.reproduciendo_audio else "#94a3b8"
            self.canvas.create_text(
                cx, altavoz_y + 35,
                text=texto_estado_musica,
                font=("Segoe UI", 9, "bold"),
                fill=color_txt
            )

        # 7. Puertas animadas (plegado lateral)
        mitad_w = puerta_w // 2
        ancho_hoja = mitad_w * (1.0 - factor_apertura)
        color_puerta = "#78350f"
        color_marco = "#451a03"

        if ancho_hoja > 1:
            # Puerta izquierda
            self.canvas.create_rectangle(p_x1, p_y1, p_x1 + ancho_hoja, p_y2, fill=color_puerta, outline=color_marco, width=2)
            # Puerta derecha
            self.canvas.create_rectangle(p_x2 - ancho_hoja, p_y1, p_x2, p_y2, fill=color_puerta, outline=color_marco, width=2)

        # Marco de la puerta
        self.canvas.create_rectangle(p_x1, p_y1, p_x2, p_y2, fill="", outline="#475569", width=4)

    def _click_canvas(self, event):
        """Hacer clic dentro de la casa alterna entre pausar y reproducir."""
        if self.puerta_abierta:
            if self.reproduciendo_audio:
                self.detener_musica()
            else:
                self.reproducir_musica()

    def _cerrar_aplicacion(self):
        """Asegura que el sonido se apague al cerrar la ventana."""
        winsound.PlaySound(None, winsound.SND_PURGE)
        self.root.destroy()


def main():
    root = tk.Tk()
    app = CasaSorpresaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
