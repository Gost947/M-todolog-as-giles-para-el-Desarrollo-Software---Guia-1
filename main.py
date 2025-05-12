import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random

class Tablero:
    def __init__(self):
        self.filas = 4
        self.columnas = 4
        self.tablero = [[0 for _ in range(4)] for _ in range(4)]
        self.huecos = 0
        self.generar_solucion_valida()

    def generar_solucion_valida(self):
        """Genera una solución válida de Sudoku 4x4"""
        numeros = [1, 2, 3, 4]
        random.shuffle(numeros)

        # Patrón base para Sudoku 4x4
        self.tablero[0] = numeros.copy()
        self.tablero[1] = numeros[2:] + numeros[:2]
        self.tablero[2] = [numeros[1], numeros[0], numeros[3], numeros[2]]
        self.tablero[3] = [numeros[3], numeros[2], numeros[1], numeros[0]]

        if not self.validar_solucion():
            self.generar_solucion_valida()

    def validar_solucion(self):
        """Valida que la solución cumpla todas las reglas"""
        for i in range(4):
            if len(set(self.tablero[i])) != 4:
                return False
            if len(set(self.tablero[j][i] for j in range(4))) != 4:
                return False

        regiones = [(0, 0), (0, 2), (2, 0), (2, 2)]
        for fi, ci in regiones:
            region = []
            for i in range(fi, fi + 2):
                for j in range(ci, ci + 2):
                    region.append(self.tablero[i][j])
            if len(set(region)) != 4:
                return False
        return True

    def generar_tablero(self, dificultad):
        """Elimina celdas según la dificultad seleccionada"""
        self.huecos = 6 if dificultad == "Fácil" else 10
        celdas = [(i, j) for i in range(4) for j in range(4)]
        random.shuffle(celdas)

        for i, j in celdas[:self.huecos]:
            self.tablero[i][j] = 0

    def es_valido(self, fila, columna, numero):
        """Verifica si un número puede colocarse en una posición"""
        if numero in self.tablero[fila]:
            return False

        if numero in [self.tablero[i][columna] for i in range(4)]:
            return False

        region_fila = (fila // 2) * 2
        region_col = (columna // 2) * 2
        for i in range(region_fila, region_fila + 2):
            for j in range(region_col, region_col + 2):
                if self.tablero[i][j] == numero:
                    return False
        return True

    def esta_completo(self):
        return all(0 not in fila for fila in self.tablero)

    def es_solucion_correcta(self):
        """Verifica si el tablero actual es una solución válida"""
        if not self.esta_completo():
            return False
        return self.validar_solucion()

class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku 4x4")

        # Variables de juego
        self.jugador = self.obtener_nombre_jugador()
        if not self.jugador:
            self.root.destroy()
            return

        self.dificultad = self.seleccionar_dificultad()
        if not self.dificultad:
            self.root.destroy()
            return

        self.tablero_actual = 1
        self.tableros_totales = 4
        self.tableros_resueltos = 0
        self.puntos = 0
        self.bonificacion_continuidad = 0

        self.tablero = Tablero()
        self.estilo_visual = "numeros"

        # Configuración de UI
        self.configurar_ui()
        self.inicializar_tablero()

    def obtener_nombre_jugador(self):
        """Pide el nombre al jugador al inicio"""
        return simpledialog.askstring("Sudoku 4x4", "Ingresa tu nombre para comenzar:")

    def seleccionar_dificultad(self):
        """Muestra diálogo para seleccionar dificultad"""
        while True:
            dificultad = simpledialog.askstring("Dificultad",
                                              "Selecciona dificultad:\n(Fácil/Difícil)",
                                              initialvalue="Fácil")
            if dificultad in ["Fácil", "Difícil"]:
                return dificultad
            if dificultad is None:  # El usuario canceló
                return None
            messagebox.showerror("Error", "Por favor ingresa 'Fácil' o 'Difícil'")

    def configurar_ui(self):
        """Configura la interfaz gráfica"""
        # Frame superior
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=10)

        # Info jugador y dificultad
        info_text = f"Jugador: {self.jugador} | Dificultad: {self.dificultad}\nTablero: {self.tablero_actual}/{self.tableros_totales}"
        self.info_label = ttk.Label(self.control_frame, text=info_text, font=('Arial', 10))
        self.info_label.grid(row=0, column=0, columnspan=2, pady=5)

        # Selector de visualización
        ttk.Label(self.control_frame, text="Visualización:").grid(row=1, column=0, padx=5)
        self.visual_var = tk.StringVar(value="numeros")
        visualizaciones = ttk.Combobox(self.control_frame, textvariable=self.visual_var,
                                     values=["numeros", "letras", "simbolos"], state="readonly", width=8)
        visualizaciones.grid(row=1, column=1, padx=5)
        visualizaciones.bind("<<ComboboxSelected>>", self.cambiar_visualizacion)

        # Frame del tablero
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)
        self.celdas = [[None for _ in range(4)] for _ in range(4)]
        self.comboboxes = [[None for _ in range(4)] for _ in range(4)]
        self.valores_ingresados = [[None for _ in range(4)] for _ in range(4)]

        # Controles inferiores
        self.puntos_label = ttk.Label(self.root,
                                     text=f"Puntos: {self.puntos} | Bonificación: +{self.bonificacion_continuidad}",
                                     font=('Arial', 12))
        self.puntos_label.pack(pady=5)

        ttk.Button(self.root, text="Verificar Solución", command=self.verificar_tablero).pack(pady=5)

    def inicializar_tablero(self):
        """Prepara un nuevo tablero de juego"""
        self.tablero = Tablero()
        self.tablero.generar_tablero(self.dificultad)

        for i in range(4):
            for j in range(4):
                if self.celdas[i][j]:
                    self.celdas[i][j].destroy()
                if self.comboboxes[i][j]:
                    self.comboboxes[i][j].destroy()

                if self.tablero.tablero[i][j] != 0:
                    self.crear_celda_fija(i, j)
                else:
                    self.crear_celda_editable(i, j)

    def crear_celda_fija(self, fila, col):
        """Crea una celda no editable"""
        self.celdas[fila][col] = tk.Label(
            self.frame, text=self.formatear_numero(self.tablero.tablero[fila][col]),
            width=4, height=2, relief="groove", font=('Arial', 16), bg='white'
        )
        self.celdas[fila][col].grid(row=fila, column=col, padx=2, pady=2)
        self.valores_ingresados[fila][col] = self.tablero.tablero[fila][col]

    def crear_celda_editable(self, fila, col):
        """Crea una celda editable con combobox"""
        self.celdas[fila][col] = tk.Frame(self.frame, width=60, height=60)
        self.celdas[fila][col].grid(row=fila, column=col, padx=2, pady=2)
        self.celdas[fila][col].grid_propagate(False)

        self.comboboxes[fila][col] = ttk.Combobox(
            self.celdas[fila][col],
            values=self.obtener_todas_opciones(),
            state="readonly",
            width=3,
            font=('Arial', 12)
        )
        self.comboboxes[fila][col].pack(expand=True)
        self.comboboxes[fila][col].bind("<<ComboboxSelected>>",
            lambda e, f=fila, c=col: self.actualizar_valor(f, c))
        self.valores_ingresados[fila][col] = 0

    def actualizar_valor(self, fila, col):
        """Actualiza el valor seleccionado por el usuario"""
        valor = self.comboboxes[fila][col].get()

        if self.estilo_visual == "numeros":
            num = int(valor)
        elif self.estilo_visual == "letras":
            num = ord(valor) - 64
        else:
            num = ["♣", "♦", "♥", "♠"].index(valor) + 1

        self.valores_ingresados[fila][col] = num
        self.comboboxes[fila][col].config(style='Modificado.TCombobox')

    def verificar_tablero(self):
        """Verifica la solución y actualiza el juego"""
        # Copiar valores al tablero para validación
        for i in range(4):
            for j in range(4):
                if self.tablero.tablero[i][j] == 0:
                    self.tablero.tablero[i][j] = self.valores_ingresados[i][j]

        if self.tablero.es_solucion_correcta():
            self.manejar_solucion_correcta()
        else:
            self.manejar_solucion_incorrecta()

        self.pasar_al_siguiente_tablero()

    def manejar_solucion_correcta(self):
        """Calcula puntuación para solución correcta"""
        puntos_base = 10
        self.tableros_resueltos += 1

        # Calcular bonificación por continuidad (1, 2, 4, ...)
        if self.tableros_resueltos > 1:
            self.bonificacion_continuidad = 2 ** (self.tableros_resueltos - 2)
        else:
            self.bonificacion_continuidad = 0

        self.puntos += puntos_base + self.bonificacion_continuidad

        mensaje = f"¡Correcto!\nPuntos: +{puntos_base}"
        if self.bonificacion_continuidad > 0:
            mensaje += f" (Bonificación: +{self.bonificacion_continuidad})"
        messagebox.showinfo("¡Bien hecho!", mensaje)

    def manejar_solucion_incorrecta(self):
        """Reinicia contadores si la solución es incorrecta"""
        messagebox.showerror("Incorrecto", "Solución no válida. No se suman puntos.")
        self.tableros_resueltos = 0
        self.bonificacion_continuidad = 0

    def pasar_al_siguiente_tablero(self):
        """Prepara el siguiente tablero o finaliza el juego"""
        self.tablero_actual += 1
        self.actualizar_ui()

        if self.tablero_actual > self.tableros_totales:
            self.finalizar_juego()
        else:
            self.inicializar_tablero()

    def finalizar_juego(self):
        """Muestra resultados finales y guarda puntaje"""
        messagebox.showinfo("Juego Terminado",
                          f"¡Felicidades {self.jugador}!\nPuntuación final: {self.puntos}")
        self.guardar_puntaje()
        self.root.destroy()

    def guardar_puntaje(self):
        """Guarda el puntaje en archivo"""
        try:
            with open("puntajes.txt", "a") as f:
                f.write(f"{self.jugador}: {self.puntos}\n")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el puntaje: {str(e)}")

    def actualizar_ui(self):
        """Actualiza la información en la interfaz"""
        info_text = f"Jugador: {self.jugador} | Dificultad: {self.dificultad}\nTablero: {self.tablero_actual}/{self.tableros_totales}"
        self.info_label.config(text=info_text)
        self.puntos_label.config(text=f"Puntos: {self.puntos} | Bonificación: +{self.bonificacion_continuidad}")

    def cambiar_visualizacion(self, event=None):
        """Cambia el estilo de visualización"""
        nueva_visual = self.visual_var.get()
        if nueva_visual != self.estilo_visual:
            self.estilo_visual = nueva_visual
            self.inicializar_tablero()

    def obtener_todas_opciones(self):
        """Devuelve opciones según el estilo de visualización"""
        if self.estilo_visual == "numeros":
            return ["1", "2", "3", "4"]
        elif self.estilo_visual == "letras":
            return ["A", "B", "C", "D"]
        else:
            return ["♣", "♦", "♥", "♠"]

    def formatear_numero(self, num):
        """Formatea números según el estilo de visualización"""
        if self.estilo_visual == "numeros":
            return str(num)
        elif self.estilo_visual == "letras":
            return chr(64 + num)
        else:
            return ["♣", "♦", "♥", "♠"][num - 1]

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure('Modificado.TCombobox', foreground='blue')
    app = SudokuApp(root)
    root.mainloop()