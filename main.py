import json
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

# --- CONFIGURACIÓN ESTÉTICA ---
# Paleta de colores basada en el icono de Python
PY_BLUE = "#3776AB"
PY_YELLOW = "#FFD43B"
BG_DARK = "#0A0A0A"
GLASS_COLOR = [1, 1, 1, 0.08] # Blanco muy transparente
GLASS_BORDER = [0.21, 0.46, 0.67, 0.5] # Azul Python semi-transparente

KV = f"""
<GlassButton@Button>:
    background_color: 0, 0, 0, 0
    font_size: '16sp'
    bold: True
    color: "#E0E0E0"
    canvas.before:
        Color:
            rgba: {GLASS_COLOR}
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [15,]
        Color:
            rgba: {GLASS_BORDER}
        Line:
            width: 1.2
            rounded_rectangle: (self.x, self.y, self.width, self.height, 15)

<MainScreen>:
    canvas.before:
        Color:
            rgb: get_color_from_hex("{BG_DARK}")
        Rectangle:
            pos: self.pos
            size: self.size
            
    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'

                RelativeLayout:
            size_hint_y: 0.1
            Label:
                text: "PTM"
                # ... (resto de las propiedades)
            Label:
                id: score_label  # <--- AGREGA ESTA LÍNEA
                text: "Score: " + str(app.score)
                font_size: '14sp'
                color: get_color_from_hex("#FFD43B")
                pos_hint: {'right': 1, 'center_y': 0.5}


        # Cuadrícula de Categorías (Imagen 2)
        ScrollView:
            GridLayout:
                id: categories_grid
                cols: 2
                spacing: '15dp'
                size_hint_y: None
                height: self.minimum_height
                padding: [0, 10]

        BoxLayout:
            size_hint_y: 0.1
            spacing: '10dp'
            GlassButton:
                text: "RESET SCORE"
                on_release: app.reset_score()
            GlassButton:
                text: "VOLVER"
                on_release: app.stop() # O salir de la app

<ExercisesScreen>:
    canvas.before:
        Color:
            rgb: get_color_from_hex("{BG_DARK}")
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'

        Label:
            size_hint_y: 0.1
            text: "PTM - " + root.category_name
            font_size: '24sp'
            color: get_color_from_hex("{PY_BLUE}")

        # Lista de Ejercicios (Imagen 1)
        ScrollView:
            canvas.before:
                Color:
                    rgba: {GLASS_COLOR}
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [20,]
            BoxLayout:
                id: exercises_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: '10dp'
                spacing: '10dp'

        GlassButton:
            size_hint: (0.4, 0.1)
            pos_hint: {{'right': 1}}
            text: "VOLVER"
            on_release: app.root.current = 'main'

<PracticeScreen>:
    canvas.before:
        Color:
            rgb: get_color_from_hex("{BG_DARK}")
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '20dp'

        Label:
            size_hint_y: 0.05
            text: "PTM"
            font_size: '24sp'
            color: get_color_from_hex("{PY_BLUE}")

        # Code Example Panel (Imagen 0)
        BoxLayout:
            orientation: 'vertical'
            Label:
                text: "Code Example"
                size_hint_y: None
                height: '30dp'
                halign: 'left'
            TextInput:
                id: code_example
                readonly: True
                background_color: 1, 1, 1, 0.05
                foreground_color: get_color_from_hex("#A9B7C6")
                font_name: 'Roboto' # Cambiar por fuente mono si tienes
                text: root.example_text

        # Copied Code Panel (Imagen 0)
        BoxLayout:
            orientation: 'vertical'
            Label:
                text: "Your Code"
                size_hint_y: None
                height: '30dp'
            TextInput:
                id: user_input
                background_color: 1, 1, 1, 0.1
                foreground_color: (1, 1, 1, 1)
                cursor_color: get_color_from_hex("{PY_YELLOW}")

        BoxLayout:
            size_hint_y: 0.15
            spacing: '15dp'
            GlassButton:
                text: "VERIFY"
                on_release: root.verify_code()
            GlassButton:
                text: "VOLVER"
                on_release: app.root.current = 'exercises'
"""

class MainScreen(Screen):
    def on_enter(self):
        self.ids.categories_grid.clear_widgets()
        # Generar botones desde temas.json
        for cat in app.temas_data.keys():
            btn = Builder.template('GlassButton', text=cat.upper())
            btn.bind(on_release=lambda instance, c=cat: self.go_to_category(c))
            self.ids.categories_grid.add_widget(btn)

    def go_to_category(self, category):
        app.root.get_screen('exercises').category_name = category
        app.root.current = 'exercises'

class ExercisesScreen(Screen):
    category_name = ""
    def on_enter(self):
        self.ids.exercises_list.clear_widgets()
        exercises = app.temas_data.get(self.category_name, [])
        for ex in exercises:
            btn = Builder.template('GlassButton', text=ex['titulo'])
            btn.size_hint_y = None
            btn.height = '60dp'
            btn.bind(on_release=lambda instance, e=ex: self.go_to_practice(e))
            self.ids.exercises_list.add_widget(btn)

    def go_to_practice(self, exercise):
        app.root.get_screen('practice').example_text = exercise['codigo']
        app.root.current = 'practice'

class PracticeScreen(Screen):
    example_text = ""
    def verify_code(self):
        # Lógica de verificación simple
        if self.ids.user_input.text.strip() == self.example_text.strip():
            app.score += 10
            app.root.current = 'main'

class PythonMasterApp(App):
    score = 0
    temas_data = {}

    def build(self):
        # Cargar datos
        try:
            with open('assets/temas.json', 'r', encoding='utf-8') as f:
                self.temas_data = json.load(f)
        except Exception as e:
            print(f"Error cargando JSON: {e}")

        Builder.load_string(KV)
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(ExercisesScreen(name='exercises'))
        sm.add_widget(PracticeScreen(name='practice'))
        return sm

        def reset_score(self):
        self.score = 0
        # Ahora que el ID existe, esto ya no lanzará el error
        self.root.get_screen('main').ids.score_label.text = "Score: 0"


if __name__ == '__main__':
    PythonMasterApp().run()
