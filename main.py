import flet as ft
import json
import re
import time
import threading
import os

# ── Paleta Liquid Glass ──────────────────────────────────────────────────────
C = {
    "bg":          "#F5F5F7",
    "glass":       "#FFFFFF",
    "accent":      "#0071E3",
    "text_main":   "#1D1D1F",
    "text_sec":    "#86868B",
    "success":     "#34C759",
    "danger":      "#FF3B30",
    "border":      "#D2D2D7",
    "warning":     "#FF9500",
}

# ── Utilidades ───────────────────────────────────────────────────────────────
def normalizar_codigo(codigo: str) -> str:
    codigo = re.sub(r'#.*', '', codigo)
    codigo = codigo.replace('\n', ' ').replace('\t', ' ')
    return ' '.join(codigo.split()).strip()

def cargar_temas() -> list:
    """Carga temas.json desde assets/ o directorio actual."""
    rutas = [
        os.path.join(os.path.dirname(__file__), "assets", "temas.json"),
        os.path.join(os.path.dirname(__file__), "temas.json"),
        "assets/temas.json",
        "temas.json",
    ]
    for ruta in rutas:
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
    return []

# ── App ──────────────────────────────────────────────────────────────────────
def main(page: ft.Page):
    page.title = "Python Master Training"
    page.bgcolor = C["bg"]
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    page.fonts = {"mono": "Courier New"}

    # ── Estado ───────────────────────────────────────────────────────────────
    state = {
        "score":        0,
        "temas":        cargar_temas(),
        "tema_actual":  0,
        "nivel_actual": 1,
    }

    # ── Helpers de UI ────────────────────────────────────────────────────────
    def chip_nivel(nivel):
        labels = {1: "Fase 1 · COPIAR", 2: "Fase 2 · COMPLETAR", 3: "Fase 3 · MEMORIZAR"}
        return ft.Container(
            content=ft.Text(labels[nivel], color="white", size=12, weight=ft.FontWeight.BOLD),
            bgcolor=C["warning"],
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=14, vertical=6),
        )

    def score_badge():
        return ft.Container(
            content=ft.Text(f"Score: {state['score']}", color=C["accent"],
                            size=14, weight=ft.FontWeight.BOLD),
            bgcolor=C["glass"],
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            border=ft.border.all(1, C["border"]),
        )

    def card(content, padding=20):
        return ft.Container(
            content=content,
            bgcolor=C["glass"],
            border_radius=16,
            border=ft.border.all(1, C["border"]),
            padding=padding,
            margin=ft.margin.symmetric(horizontal=16, vertical=6),
        )

    def btn_primary(text, on_click, color=None):
        return ft.ElevatedButton(
            text=text,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor=color or C["success"],
                color="white",
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.padding.symmetric(horizontal=32, vertical=16),
                text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
            ),
        )

    def btn_text(text, on_click, color=None):
        return ft.TextButton(
            text=text,
            on_click=on_click,
            style=ft.ButtonStyle(
                color=color or C["accent"],
                text_style=ft.TextStyle(size=14, weight=ft.FontWeight.BOLD),
            ),
        )

    # ── Pantalla: INICIO ─────────────────────────────────────────────────────
    def mostrar_inicio():
        temas = state["temas"]
        categorias = list(dict.fromkeys([t.get("categoria", "General") for t in temas]))

        def reiniciar_score(e):
            def confirmar(e2):
                if e2.data == "true":
                    state["score"] = 0
                    mostrar_inicio()
                dlg.open = False
                page.update()

            dlg = ft.AlertDialog(
                title=ft.Text("Reiniciar Score"),
                content=ft.Text("¿Deseas reiniciar tu score a 0?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: close_dlg()),
                    ft.TextButton("Reiniciar", on_click=lambda e: (
                        setattr(state, '__dummy__', None) or
                        do_reset()
                    )),
                ],
            )

            def close_dlg():
                dlg.open = False
                page.update()

            def do_reset():
                state["score"] = 0
                dlg.open = False
                mostrar_inicio()

            dlg.actions = [
                ft.TextButton("Cancelar", on_click=lambda e: close_dlg()),
                ft.TextButton("Reiniciar", on_click=lambda e: do_reset()),
            ]
            page.dialog = dlg
            dlg.open = True
            page.update()

        # Grid de categorías
        def cat_button(cat):
            count = len([t for t in temas if t.get("categoria") == cat])

            def ir(e):
                mostrar_categoria(cat)

            return ft.Container(
                content=ft.Column([
                    ft.Text(cat, size=15, weight=ft.FontWeight.BOLD,
                            color=C["text_main"], text_align=ft.TextAlign.CENTER),
                    ft.Text(f"{count} temas", size=12, color=C["text_sec"],
                            text_align=ft.TextAlign.CENTER),
                ], alignment=ft.MainAxisAlignment.CENTER,
                   horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                bgcolor=C["glass"],
                border_radius=16,
                border=ft.border.all(1, C["border"]),
                padding=20,
                ink=True,
                on_click=ir,
                expand=True,
            )

        rows = []
        for i in range(0, len(categorias), 2):
            pair = categorias[i:i+2]
            row_controls = [cat_button(c) for c in pair]
            if len(row_controls) == 1:
                row_controls.append(ft.Container(expand=True))  # placeholder
            rows.append(ft.Row(row_controls, spacing=12))

        grid = ft.Column(rows, spacing=12)

        page.controls.clear()
        page.add(
            ft.Container(
                content=ft.Column([
                    # Header
                    ft.Container(
                        content=ft.Row([
                            ft.Text("Python Master", size=28, weight=ft.FontWeight.BOLD,
                                    color=C["text_main"]),
                            score_badge(),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=ft.padding.only(left=16, right=16, top=24, bottom=8),
                    ),
                    ft.Container(
                        ft.Text("Explorar Categorías", size=16, color=C["text_sec"]),
                        padding=ft.padding.only(left=16, bottom=16),
                    ),
                    # Grid
                    ft.Container(grid, padding=ft.padding.symmetric(horizontal=16)),
                    # Footer
                    ft.Container(
                        content=ft.Row([
                            btn_text("Reiniciar Score", reiniciar_score, C["text_sec"]),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        padding=ft.padding.symmetric(vertical=24),
                    ),
                ], spacing=0),
                bgcolor=C["bg"],
                expand=True,
            )
        )
        page.update()

    # ── Pantalla: CATEGORÍA ──────────────────────────────────────────────────
    def mostrar_categoria(categoria):
        temas = state["temas"]
        items = [(i, t) for i, t in enumerate(temas) if t.get("categoria") == categoria]

        def item_row(idx, tema):
            def estudiar(e):
                state["tema_actual"] = idx
                state["nivel_actual"] = 1
                cargar_fase()

            return ft.Container(
                content=ft.Row([
                    ft.Text(tema["titulo"], size=13, weight=ft.FontWeight.W_500,
                            color=C["text_main"], expand=True),
                    ft.ElevatedButton(
                        "Estudiar",
                        on_click=estudiar,
                        style=ft.ButtonStyle(
                            bgcolor=C["accent"], color="white",
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=ft.padding.symmetric(horizontal=20, vertical=10),
                        ),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=C["glass"],
                border_radius=14,
                border=ft.border.all(1, C["border"]),
                padding=ft.padding.symmetric(horizontal=16, vertical=14),
                margin=ft.margin.symmetric(horizontal=16, vertical=5),
            )

        page.controls.clear()
        page.add(
            ft.Container(
                content=ft.Column([
                    # Header
                    ft.Container(
                        content=ft.Row([
                            btn_text("← Volver", lambda e: mostrar_inicio()),
                            score_badge(),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=ft.padding.only(left=8, right=16, top=20, bottom=8),
                    ),
                    ft.Container(
                        ft.Text(categoria, size=26, weight=ft.FontWeight.BOLD,
                                color=C["text_main"]),
                        padding=ft.padding.only(left=16, bottom=12),
                    ),
                    # Lista
                    ft.Column([item_row(i, t) for i, t in items], spacing=0),
                    ft.Container(height=24),
                ], spacing=0),
                bgcolor=C["bg"],
                expand=True,
            )
        )
        page.update()

    # ── Pantalla: FASE ───────────────────────────────────────────────────────
    def cargar_fase():
        tema = state["temas"][state["tema_actual"]]
        nivel = state["nivel_actual"]

        # Texto de referencia según nivel
        if nivel == 1:
            ref_text = tema.get("explicacion", "")
            ref_label = "REFERENCIA:"
        elif nivel == 2:
            ref_text = tema.get("plantilla", "")
            ref_label = "PLANTILLA:"
        else:
            ref_text = tema.get("codigo", "")
            ref_label = "MEMORIZA (4 seg):"

        txt_ref = ft.TextField(
            value=ref_text,
            read_only=True,
            multiline=True,
            min_lines=5,
            max_lines=10,
            text_style=ft.TextStyle(font_family="mono", size=13, color=C["text_main"]),
            bgcolor="#F9F9FB",
            border_radius=10,
            border_color=C["border"],
            filled=True,
            expand=True,
        )

        txt_input = ft.TextField(
            hint_text="Escribe tu código aquí...",
            multiline=True,
            min_lines=7,
            max_lines=14,
            text_style=ft.TextStyle(font_family="mono", size=13, color=C["text_main"]),
            bgcolor="white",
            border_radius=10,
            border_color=C["accent"],
            focused_border_color=C["accent"],
            filled=True,
            expand=True,
        )

        feedback_ref = ft.Ref[ft.Text]()

        def validar(e):
            entrada = txt_input.value or ""
            esperado = tema.get("codigo", "")
            if normalizar_codigo(entrada) == normalizar_codigo(esperado):
                state["score"] += 100
                if state["nivel_actual"] < 3:
                    state["nivel_actual"] += 1
                    cargar_fase()
                else:
                    # Mostrar dialogo de logro
                    def cerrar_logro(e):
                        dlg.open = False
                        page.update()
                        mostrar_inicio()

                    dlg = ft.AlertDialog(
                        title=ft.Row([
                            ft.Icon(ft.Icons.EMOJI_EVENTS, color="#FFD700", size=28),
                            ft.Text(" ¡Logro Desbloqueado!", weight=ft.FontWeight.BOLD),
                        ]),
                        content=ft.Text(f"Dominaste:\n{tema['titulo']}",
                                        color=C["text_main"]),
                        actions=[ft.TextButton("¡Genial!", on_click=cerrar_logro)],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    page.dialog = dlg
                    dlg.open = True
                    page.update()
            else:
                state["score"] = max(0, state["score"] - 20)
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("❌ La lógica no coincide. ¡Inténtalo de nuevo!",
                                    color="white"),
                    bgcolor=C["danger"],
                    duration=2500,
                )
                page.snack_bar.open = True
                page.update()

        # Construir UI
        ref_card = card(
            ft.Column([
                ft.Text(ref_label, size=11, weight=ft.FontWeight.BOLD,
                        color=C["text_sec"]),
                txt_ref,
            ], spacing=8)
        )

        input_card = card(
            ft.Column([
                ft.Text("TU CÓDIGO:", size=11, weight=ft.FontWeight.BOLD,
                        color=C["text_sec"]),
                txt_input,
            ], spacing=8)
        )

        page.controls.clear()
        page.add(
            ft.Container(
                content=ft.Column([
                    # Header
                    ft.Container(
                        content=ft.Row([
                            btn_text("← Cancelar", lambda e: mostrar_inicio(), C["danger"]),
                            chip_nivel(nivel),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=ft.padding.only(left=8, right=16, top=20, bottom=4),
                    ),
                    ft.Container(
                        content=ft.Row([
                            ft.Expanded(
                                ft.Text(tema["titulo"], size=18, weight=ft.FontWeight.BOLD,
                                        color=C["text_main"])
                            ),
                            score_badge(),
                        ]),
                        padding=ft.padding.only(left=16, right=16, bottom=12),
                    ),
                    # Referencia
                    ref_card,
                    # Input
                    input_card,
                    # Botón verificar
                    ft.Container(
                        content=ft.Row([
                            btn_primary("✓  VERIFICAR", validar),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        padding=ft.padding.symmetric(vertical=20),
                    ),
                    ft.Container(height=16),
                ], spacing=0),
                bgcolor=C["bg"],
                expand=True,
            )
        )
        page.update()

        # Modo memoria: ocultar referencia después de 4 segundos
        if nivel == 3:
            def ocultar_ref():
                time.sleep(4)
                txt_ref.value = "[ MODO MEMORIA: El código se ocultó — ¡ahora escríbelo de memoria! ]"
                txt_ref.color = C["warning"]
                page.update()
            threading.Thread(target=ocultar_ref, daemon=True).start()

    # ── Iniciar ──────────────────────────────────────────────────────────────
    mostrar_inicio()


ft.app(target=main, assets_dir="assets")
