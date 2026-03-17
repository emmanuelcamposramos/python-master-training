import flet as ft
import json
import os
import re
import sys

# --- UTILIDADES DE RUTA ---
def obtener_ruta_assets(nombre_archivo):
    """Obtiene la ruta correcta del asset tanto en local como en el APK."""
    # En Android, los archivos externos se extraen a menudo en base_dir
    # sys._MEIPASS es para PyInstaller, pero Flet usa una estructura similar en APK
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    ruta_completa = os.path.join(base_dir, "assets", nombre_archivo)
    
    # Intento 2: Buscar en la carpeta assets relativa a la ejecución
    if not os.path.exists(ruta_completa):
        ruta_completa = os.path.join("assets", nombre_archivo)
        
    return ruta_completa

def normalizar_codigo(codigo: str) -> str:
    codigo = re.sub(r'#.*', '', codigo)
    codigo = codigo.replace("\n", " ").replace("\t", " ")
    return " ".join(codigo.split()).strip()

# --- CONFIGURACIÓN ESTÉTICA ---
PY_BLUE = "#3776AB"
PY_YELLOW = "#FFD43B"
BG_DARK = "#0A0A0A"
GLASS_COLOR = "0x15FFFFFF" 

def main(page: ft.Page):
    page.title = "Python Master Training"
    page.bgcolor = BG_DARK
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    
    # Variable para guardar los datos
    temas_data = []
    
    # Estado de la app
    state = {"score": 0, "categoria": None, "tema": None}

    # --- COMPONENTES DE ESTILO ---
    def GlassContainer(content, on_click=None, padding=15, expand=False, height=None):
        return ft.Container(
            content=content,
            padding=padding,
            on_click=on_click,
            bgcolor=GLASS_COLOR,
            border=ft.border.all(1, f"{PY_BLUE}55"),
            border_radius=15,
            blur=ft.Blur(10, 10, ft.BlurStyle.INNER),
            expand=expand,
            height=height
        )

    # --- NAVEGACIÓN ---
    def pantalla_inicio(e=None):
        page.controls.clear()
        
        # Header (Score y Título)
        page.add(
            ft.Row([
                ft.Text("PTM", size=32, weight="bold", color=PY_BLUE),
                ft.Text(f"Score: {state['score']}", size=16, color=PY_YELLOW),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

        # Verificar si hay datos
        if not temas_data:
            page.add(ft.Text("No se encontraron temas. Verifica temas.json", color=ft.colors.RED, text_align=ft.TextAlign.CENTER))
            page.update()
            return

        # Grid de Categorías (Imagen 2)
        categorias = sorted(list(set([t["categoria"] for t in temas_data])))
        grid = ft.GridView(expand=True, runs_count=2, spacing=15, run_spacing=15)
        
        for cat in categorias:
            grid.controls.append(
                GlassContainer(
                    content=ft.Container(
                        content=ft.Text(cat.upper(), weight="bold", text_align=ft.TextAlign.CENTER),
                        alignment=ft.alignment.center # Centrar texto en el grid
                    ),
                    on_click=lambda e, c=cat: pantalla_ejercicios(c)
                )
            )
        
        page.add(grid)

        # Botones Inferiores
        page.add(
            ft.Row([
                GlassContainer(ft.Text("RESET SCORE"), on_click=reset_score),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        )
        page.update()

    # (El resto de las funciones de navegación se mantienen igual, solo cambia temas a temas_data)
    def pantalla_ejercicios(categoria):
        state["categoria"] = categoria
        page.controls.clear()
        page.add(ft.Text(f"PTM - {categoria}", size=24, color=PY_BLUE, weight="bold"))
        lista_ejercicios = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10, expand=True)
        ejercicios_filtrados = [t for t in temas_data if t["categoria"] == categoria]
        for ex in ejercicios_filtrados:
            lista_ejercicios.controls.append(
                GlassContainer(
                    content=ft.Row([ft.Text(ex["titulo"], expand=True)], alignment=ft.MainAxisAlignment.START),
                    on_click=lambda e, tema=ex: pantalla_practica(tema),
                    height=60 # Altura fija para la lista como en el boceto
                )
            )
        page.add(GlassContainer(content=lista_ejercicios, expand=True))
        page.add(ft.Row([GlassContainer(ft.Text("VOLVER"), on_click=pantalla_inicio)], alignment=ft.MainAxisAlignment.END))
        page.update()

    def pantalla_practica(tema):
        state["tema"] = tema
        page.controls.clear()
        input_codigo = ft.TextField(
            label="Your Code",
            multiline=True,
            min_lines=5,
            bgcolor=ft.colors.BLACK12,
            border_color=PY_YELLOW,
            text_size=14
        )
        page.add(
            ft.Text("PTM", size=24, color=PY_BLUE, weight="bold"),
            ft.Text("Code Example", color=PY_YELLOW),
            GlassContainer(content=ft.Text(tema["codigo"], font_family="monospace", size=13), padding=10),
            input_codigo,
            ft.Row([
                GlassContainer(ft.Text("VERIFY"), on_click=lambda e: verificar(input_codigo.value)),
                GlassContainer(ft.Text("VOLVER"), on_click=lambda e: pantalla_ejercicios(state["categoria"])),
            ], spacing=10)
        )
        page.update()

    def verificar(valor):
        esperado = normalizar_codigo(state["tema"]["codigo"])
        entrada = normalizar_codigo(valor)
        if entrada == esperado:
            state["score"] += 10
            pantalla_inicio()

    def reset_score(e):
        state["score"] = 0
        pantalla_inicio()

    # --- INICIO DE LA APLICACIÓN (CORRECCIÓN DE CARGA) ---
    # 1. Mostrar pantalla de carga
    page.add(ft.Container(content=ft.ProgressRing(color=PY_BLUE), alignment=ft.alignment.center, expand=True))
    page.update()

    # 2. Cargar datos con la ruta corregida
    ruta_json = obtener_ruta_assets("temas.json")
    try:
        if os.path.exists(ruta_json):
            with open(ruta_json, "r", encoding="utf-8") as f:
                temas_data = json.load(f)
        else:
            # Si aún no lo encuentra, mostramos error en pantalla
            print(f"Error fatal: No se encontró {ruta_json}")
    except Exception as e:
        print(f"Error leyendo JSON: {e}")

    # 3. Lanzar la pantalla principal
    pantalla_inicio()

ft.app(target=main) # assets_dir ya no es estrictamente necesario si usamos rutas absolutas
                    
