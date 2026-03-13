import json
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty


# --------- PANTALLAS ---------

class CategoryScreen(Screen):
    pass


class TopicScreen(Screen):
    topics = ListProperty([])

    def load_topics(self, category):
        app = App.get_running_app()
        self.topics = app.data.get(category, [])
        self.ids.topic_list.clear_widgets()

        from kivy.uix.button import Button

        for topic in self.topics:
            btn = Button(
                text=topic["titulo"],
                size_hint_y=None,
                height=60
            )
            btn.bind(on_press=lambda x, t=topic: self.open_topic(t))
            self.ids.topic_list.add_widget(btn)

    def open_topic(self, topic):
        app = App.get_running_app()
        app.current_topic = topic
        app.root.current = "exercise"


class ExerciseScreen(Screen):

    question = StringProperty("")
    options = ListProperty([])

    def on_enter(self):
        app = App.get_running_app()
        self.exercises = app.current_topic.get("ejercicios", [])
        self.index = 0
        self.show_exercise()

    def show_exercise(self):

        if self.index >= len(self.exercises):
            self.question = "¡Terminaste este tema!"
            self.options = []
            return

        ex = self.exercises[self.index]

        self.question = ex["pregunta"]
        self.options = ex["opciones"]

    def answer(self, option):

        ex = self.exercises[self.index]

        app = App.get_running_app()

        if option == ex["respuesta"]:
            app.score += 10

        self.index += 1
        self.show_exercise()


# --------- APP ---------

class PythonMasterApp(App):

    score = 0
    current_topic = None

    def build(self):

        with open("temas.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)

        sm = ScreenManager()

        sm.add_widget(CategoryScreen(name="categories"))
        sm.add_widget(TopicScreen(name="topics"))
        sm.add_widget(ExerciseScreen(name="exercise"))

        return sm


if __name__ == "__main__":
    PythonMasterApp().run()
