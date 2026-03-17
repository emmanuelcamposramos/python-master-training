import flet as ft
import json
import os
import re
import sys

# --- UTILIDADES DE RUTA Y DATOS ---

def obtener_ruta_json():
    """Busca temas.json en todas las ubicaciones posibles de Android/Desktop."""
    nombre_archivo = "temas.json"
    posibles_rutas = [
        # Ruta 1: Carpeta assets relativa al script (Estándar Flet)
        os.path.join(os.path.dirname(__file__), "assets", nombre_archivo),
        # Ruta 2: Carpeta assets en el directorio de trabajo
        os.path.join("assets", nombre_archivo),
        # Ruta 3: Directorio raíz (por si acaso)
        nombre_archivo,
        # Ruta 4: Directorio temporal de extracción en Android
        os.path.join(getattr(sys, '_MEIPASS', os.getcwd()), "assets", nombre_archivo)
    ]
    
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            return ruta
    return None

def normalizar_codigo(codigo: str) -> str:
    """Limpia el código para comparar sin que afecten espacios o comentarios."""
    codigo = re.sub(r'#.*', '', codigo)
    codigo = codigo.replace("\n", " ").replace("\t", " ")
    return " ".join(codigo.split()).strip()

# --- CONFIGURACIÓN ESTÉTICA (COLORES PYTHON) ---
PY_BLUE = "#3776AB"
PY_YELLOW = "#FFD43B"
BG_DARK = "#0A0A0A"
GLASS_COLOR = "0x1AFFFFFF" # Un poco más visible para el modo oscuro

def main(page: ft.Page):
    page.title = "Python Master Training"
    page.bgcolor = BG_DARK
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    
    # Datos y Estado
    temas_data = []
    state = {"score": 0, "categoria": None, "tema": None}

    # --- COMPONENTES VISUALES ---
    def GlassContainer(content, on_click=None, padding=15, expand=False, height=None):
        return ft.Container(
            content=content,
            padding=padding,
            on_click=on_click,
            bgcolor=GLASS_COLOR,
            border=ft.border.all(1, f"{PY_BLUE}44"),
            border_radius=15,
            blur=ft.Blur(15, 15, ft.BlurStyle.INNER),
            expand=expand,
            height=height,
            animate=ft.animation.Animation(300, ft.AnimationCurve.DECELERATE)
        )

    # --- PANTALLAS ---
    def pantalla_inicio(e=None):
        page.clean()
        
        # Header
        page.add(
            ft.Row([
                ft.Text("PTM", size=32, weight="bold", color=PY_BLUE),
                ft.Text(f"Score: {state['score'] John}", id="score_text", size=18, color=PY_YELLOW, weight="bold"),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

        if not temas_data:
            page.add(
                ft.Container(
                    content=ft.Text("No se encontró temas.json en assets/", color=ft.colors.RED_400, size=16),
                    alignment=ft.alignment.center, expand=True
                )
            )
            page.update()
            return

        # Grid de Categorías (Imagen 2 del boceto)
        categorias = sorted(list(set([t["categoria"] for t in temas_data])))
        grid = ft.GridView(expand=True, runs_count=2, spacing=15, run_spacing=15)
        
        for cat in categorias:
            grid.controls.append(
                GlassContainer(
                    content=ft.Container(
                        content=ft.Text(cat.upper(), weight="bold", size=16),
                        alignment=ft.alignment.center
                    ),
                    on_click=lambda e, c=cat: pantalla_ejercicios(c)
                )
            )
        
        page.add(grid)
        
        # Botones inferiores
        page.add(
            ft.Row([
                GlassContainer(ft.Text("RESET SCORE"), on_click=reset_score),
                GlassContainer(ft.Text("SALIR"), on_click=lambda _: page.window_close())
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
        )
        page.update()

    def pantalla_ejercicios(categoria):
        state["categoria"] = categoria
        page.clean()
        
        page.add(ft.Text(f"CATEGORÍA: {categoria}", size=22, color=PY_BLUE, weight="bold"))
        
        lista = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10, expand=True)
        items = [t for t in temas_data if t["categoria"] == categoria]
        
        for ex in items:
            lista.controls.append(
                GlassContainer(
                    content=ft.Row([
                        ft.Icon(ft.icons.CODE, color=PY_YELLOW),
                        ft.Text(ex["titulo"], size=16, weight="w500")
                    ]),
                    on_click=lambda e, t=ex: pantalla_practica(t),
                    height=70
                )
            )
        
        page.add(lista)
        page.add(ft.Row([GlassContainer(ft.Text("VOLVER"), on_click=pantalla_inicio)], alignment=ft.MainAxisAlignment.END))
        page.update()

    def pantalla_practica(tema):
        state["tema"] = tema
        page.clean()
        
        input_codigo = ft.TextField(
            label="Escribe el código aquí",
            multiline=True,
            min_lines=6,
            bgcolor=ft.colors.BLACK26,
            border_color=PY_BLUE,
            focused_border_color=PY_YELLOW,
            text_size=14,
            text_style=ft.TextStyle(font_family="monospace")
        )

        page.add(
            ft.Text(tema["titulo"], size=20, color=PY_BLUE, weight="bold"),
            ft.Text("Referencia:", color=PY_YELLOW, size=14),
            GlassContainer(
                content=ft.Text(tema["codigo"], font_family="monospace", size=13, color=ft.colors.GREY_300),
                padding=12
            ),
            input_codigo,
            ft.Row([
                GlassContainer(ft.Text("VERIFICAR", weight="bold"), on_click=lambda e: verificar(input_codigo.value)),
                GlassContainer(ft.Text("VOLVER"), on_click=lambda e: pantalla_ejercicios(state["categoria"])),
            ], spacing=15, alignment=ft.MainAxisAlignment.CENTER)
        )
        page.update()

    def verificar(valor):
        esperado = normalizar_codigo(state["tema"]["codigo"])
        entrada = normalizar_codigo(valor)
        
        if entrada == esperado:
            state["score"] += 10
            page.snack_bar = ft.SnackBar(ft.Text("¡Excelente! +10 puntos"), bgcolor=ft.colors.GREEN_700)
            page.snack_bar.open = True
            pantalla_inicio()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Hay un error en el código, revisa espacios o símbolos"), bgcolor=ft.colors.RED_700)
            page.snack_bar.open = True
            page.update()

    def reset_score(e):
        state["score"] = 0
        pantalla_inicio()

    # --- LÓGICA DE CARGA INICIAL ---
    
    # 1. Cargar datos
    ruta = obtener_ruta_json()
    if ruta:
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                temas_data = json.load(f)
        except:
            pass

    # 2. Iniciar app
    pantalla_inicio()

# Ejecución
if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
    
