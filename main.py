import flet as ft
import json
import os
import re

# ─────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────

def normalizar_codigo(codigo: str) -> str:
    codigo = re.sub(r'#.*', '', codigo)
    codigo = codigo.replace("\n", " ").replace("\t", " ")
    return " ".join(codigo.split()).strip()


def cargar_temas():
    rutas = [
        "assets/temas.json",
        os.path.join(os.path.dirname(__file__), "assets", "temas.json"),
    ]

    for r in rutas:
        if os.path.exists(r):
            with open(r, "r", encoding="utf-8") as f:
                return json.load(f)

    print("No se encontró temas.json")
    return []


# ─────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────

def main(page: ft.Page):

    page.title = "Python Master Training"
    page.scroll = ft.ScrollMode.AUTO

    temas = cargar_temas()
    score = 0
    tema_actual = None
    fase = 1

    # ─────────────────────────────────────────
    # INICIO
    # ─────────────────────────────────────────

    def pantalla_inicio():

        categorias = sorted(list(set([t["categoria"] for t in temas])))

        page.controls.clear()

        page.add(
            ft.Text("Python Master Training", size=30, weight="bold"),
            ft.Text(f"Score: {score}", size=18),
            ft.Divider()
        )

        for cat in categorias:

            btn = ft.ElevatedButton(
                text=cat,
                on_click=lambda e, c=cat: pantalla_categoria(c)
            )

            page.add(btn)

        page.update()

    # ─────────────────────────────────────────
    # CATEGORIA
    # ─────────────────────────────────────────

    def pantalla_categoria(categoria):

        page.controls.clear()

        page.add(
            ft.Row([
                ft.TextButton("← Volver", on_click=lambda e: pantalla_inicio())
            ])
        )

        page.add(ft.Text(categoria, size=26, weight="bold"))

        for i, t in enumerate(temas):

            if t["categoria"] != categoria:
                continue

            btn = ft.ElevatedButton(
                text=t["titulo"],
                on_click=lambda e, idx=i: iniciar_ejercicio(idx)
            )

            page.add(btn)

        page.update()

    # ─────────────────────────────────────────
    # INICIAR EJERCICIO
    # ─────────────────────────────────────────

    def iniciar_ejercicio(idx):

        nonlocal tema_actual
        nonlocal fase

        tema_actual = temas[idx]
        fase = 1

        mostrar_fase()

    # ─────────────────────────────────────────
    # MOSTRAR FASE
    # ─────────────────────────────────────────

    def mostrar_fase():

        nonlocal fase
        nonlocal score

        page.controls.clear()

        if fase == 1:
            referencia = tema_actual["explicacion"]
            titulo = "FASE 1: COPIAR"

        elif fase == 2:
            referencia = tema_actual["plantilla"]
            titulo = "FASE 2: COMPLETAR"

        else:
            referencia = tema_actual["codigo"]
            titulo = "FASE 3: MEMORIZAR"

        input_codigo = ft.TextField(
            multiline=True,
            min_lines=10
        )

        ref = ft.TextField(
            value=referencia,
            multiline=True,
            read_only=True
        )

        def verificar(e):

            nonlocal fase
            nonlocal score

            entrada = normalizar_codigo(input_codigo.value)
            esperado = normalizar_codigo(tema_actual["codigo"])

            if entrada == esperado:

                score += 100

                if fase < 3:
                    fase += 1
                    mostrar_fase()
                else:
                    pantalla_inicio()

            else:

                score = max(0, score - 20)

                page.snack_bar = ft.SnackBar(
                    ft.Text("Código incorrecto")
                )

                page.snack_bar.open = True
                page.update()

        page.add(

            ft.Row([
                ft.TextButton("← Salir", on_click=lambda e: pantalla_inicio()),
                ft.Text(f"Score: {score}")
            ]),

            ft.Text(tema_actual["titulo"], size=22, weight="bold"),

            ft.Text(titulo, size=16),

            ref,

            ft.Text("Tu código:"),

            input_codigo,

            ft.ElevatedButton(
                "Verificar",
                on_click=verificar
            )

        )

        page.update()

    # ─────────────────────────────────────────

    pantalla_inicio()


ft.app(target=main, assets_dir="assets")
