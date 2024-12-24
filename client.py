import requests
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView

SERVER_URL = "https://files-toc.onrender.com"
nickname = "Гость"

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation="vertical", spacing=20, padding=20)
        layout.add_widget(MDLabel(text="Добро пожаловать в чат!", halign="center"))
        layout.add_widget(MDRaisedButton(text="Создать новый чат", on_release=self.go_to_create_chat))
        layout.add_widget(MDRaisedButton(text="Найти существующий чат", on_release=self.go_to_find_chat))
        layout.add_widget(MDRaisedButton(text="Установить ник", on_release=self.set_nickname))
        self.add_widget(layout)

    def go_to_create_chat(self, *args):
        self.manager.current = "create_chat"

    def go_to_find_chat(self, *args):
        self.manager.current = "find_chat"

    def set_nickname(self, *args):
        self.manager.current = "nickname"

class CreateChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_id_label = MDLabel(text="Нажмите 'Создать чат', чтобы начать.", halign="center")
        self.enter_chat_button = MDRaisedButton(text="Перейти в чат", on_release=self.go_to_chat, disabled=True)
        layout = MDBoxLayout(orientation="vertical", spacing=20, padding=20)
        layout.add_widget(self.chat_id_label)
        layout.add_widget(MDRaisedButton(text="Создать чат", on_release=self.create_chat))
        layout.add_widget(self.enter_chat_button)
        layout.add_widget(MDRaisedButton(text="Назад", on_release=self.go_back))
        self.add_widget(layout)

    def create_chat(self, *args):
        response = requests.post(f"{SERVER_URL}/create_chat")
        chat_id = response.json().get("chat_id")
        self.manager.get_screen("chat").chat_id = chat_id
        self.chat_id_label.text = f"Ваш ID чата: {chat_id}"
        self.enter_chat_button.disabled = False

    def go_to_chat(self, *args):
        self.manager.current = "chat"

    def go_back(self, *args):
        self.manager.current = "main"

class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_id = None
        layout = MDBoxLayout(orientation="vertical", spacing=20, padding=20)
        self.chat_output = ScrollView(size_hint=(1, 0.6))
        self.chat_history = MDLabel(size_hint_y=None, halign="left", text="История чата появится здесь")
        self.chat_output.add_widget(self.chat_history)
        self.message_input = MDTextField(hint_text="Введите сообщение")
        layout.add_widget(self.chat_output)
        layout.add_widget(self.message_input)
        layout.add_widget(MDRaisedButton(text="Отправить", on_release=self.send_message))
        layout.add_widget(MDRaisedButton(text="Назад", on_release=self.go_back))
        self.add_widget(layout)

    def load_chat(self):
        response = requests.get(f"{SERVER_URL}/get_chat", params={"chat_id": self.chat_id})
        if response.status_code == 200:
            messages = response.json().get("messages", [])
            self.chat_history.text = "\n".join(messages)
        else:
            self.chat_history.text = "Чат не найден."

    def send_message(self, *args):
        message = self.message_input.text
        if self.chat_id and message:
            requests.post(f"{SERVER_URL}/send_message", json={
                "chat_id": self.chat_id,
                "nickname": nickname,
                "message": message
            })
            self.chat_history.text += f"\n{nickname}: {message}"
        self.message_input.text = ""

    def go_back(self, *args):
        self.manager.current = "main"

class FindChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_id_input = MDTextField(hint_text="Введите ID чата")
        layout = MDBoxLayout(orientation="vertical", spacing=20, padding=20)
        layout.add_widget(self.chat_id_input)
        layout.add_widget(MDRaisedButton(text="Найти чат", on_release=self.find_chat))
        layout.add_widget(MDRaisedButton(text="Назад", on_release=self.go_back))
        self.add_widget(layout)

    def find_chat(self, *args):
        self.manager.get_screen("chat").chat_id = self.chat_id_input.text
        self.manager.get_screen("chat").load_chat()
        self.manager.current = "chat"

class NicknameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nickname_input = MDTextField(hint_text="Введите ваш ник")
        layout = MDBoxLayout(orientation="vertical", spacing=20, padding=20)
        layout.add_widget(self.nickname_input)
        layout.add_widget(MDRaisedButton(text="Сохранить", on_release=self.save_nickname))
        layout.add_widget(MDRaisedButton(text="Назад", on_release=self.go_back))
        self.add_widget(layout)

    def save_nickname(self, *args):
        global nickname
        nickname = self.nickname_input.text
        self.manager.current = "main"

    def go_back(self, *args):
        self.manager.current = "main"

class ChatApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(CreateChatScreen(name="create_chat"))
        sm.add_widget(ChatScreen(name="chat"))
        sm.add_widget(FindChatScreen(name="find_chat"))
        sm.add_widget(NicknameScreen(name="nickname"))
        return sm

if __name__ == "__main__":
    ChatApp().run()
