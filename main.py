import json
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.properties import NumericProperty

# --- CONFIGURACIÓN ESTÉTICA ---
PY_BLUE = "#3776AB"
PY_YELLOW = "#FFD43B"
BG_DARK = "#0A0A0A"
GLASS_COLOR = [1, 1, 1, 0.08] 
GLASS_BORDER = [0.21, 0.46, 0.67, 0.5] 

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
                font_size: '32sp'
                bold: True
                color: get_color_from_hex("{PY_BLUE}")
                pos_hint: {{'center_x': 0.5, 'center_y': 0.5}}
            Label:
                id: score_label
                text: "Score: " + str(app.score)
                font_size: '14sp'
                color: get_color_from_hex("{PY_YELLOW}")
                pos_hint: {{'right': 1, 'center_y': 0.5}}

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
                on_release: app.stop()

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
            font_size: '22sp'
            color: get_color_from_hex("{PY_BLUE}")

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

        BoxLayout:
            orientation: 'vertical'
            Label:
                text: "Code Example"
                size_hint_y: None
                height: '30dp'
                color: get_color_from_hex("{PY_YELLOW}")
            TextInput:
                id
