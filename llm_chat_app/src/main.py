from kivy.animation import Animation
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
import os
from datetime import datetime
import random

# Demo yanıtlar
DEMO_RESPONSES = [
    "Merhaba! Size nasıl yardımcı olabilirim? 😊",
    "Bu konuda size yardımcı olmaktan mutluluk duyarım! 💡",
    "İlginç bir soru! Hemen düşüneyim... 🤔",
    "Harika bir gözlem! 🌟",
    "Bu konuda biraz daha detay verebilir misiniz? 🎯",
    "Anladım, devam edelim! ✨",
    "Size katılıyorum! 👍",
    "Bu konuda farklı bir bakış açısı sunayım... 🔍",
    "Güzel soru! 🎉",
    "Birlikte çözüm bulalım! 🤝"
]

class IconButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.color = get_color_from_hex('#FFFFFF')
        self.font_size = '24sp'
        self.size_hint = (None, None)
        self.size = (dp(40), dp(40))

class ChatBubble(BoxLayout):
    text = StringProperty()
    is_user = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = [20, 10]
        self.size_hint_y = None
        self.size_hint_x = 0.7
        self.pos_hint = {'right': 0.98} if self.is_user else {'x': 0.02}
        
        content_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[10, 5]
        )
        
        self.message_label = Label(
            text=self.text,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            text_size=(Window.width * 0.6, None),
            halign='left',
            valign='middle',
            markup=True,
            font_size='16sp',
        )
        self.message_label.bind(texture_size=self._update_message_height)
        
        time_label = Label(
            text=datetime.now().strftime('%H:%M'),
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=20,
            font_size='12sp'
        )
        
        content_box.add_widget(self.message_label)
        content_box.add_widget(time_label)
        content_box.height = self.message_label.height + time_label.height + 10
        
        self.add_widget(content_box)
        self.height = content_box.height + 20

    def _update_message_height(self, instance, value):
        instance.height = value[1]
        self.height = value[1] + 40

class MainScreenManager(ScreenManager):
    pass

class LoginScreen(Screen):
    def verify_credentials(self):
        username = self.ids.username_input.text
        password = self.ids.password_input.text
        
        if username and password:
            if username == "demo" and password == "demo":
                self.manager.current = 'chat'
            else:
                self.ids.error_label.text = "Hatalı kullanıcı adı veya şifre"
        else:
            self.ids.error_label.text = "Lütfen tüm alanları doldurun"

class ChatScreen(Screen):
    chat_history = []

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.add_message(
            "Merhaba! Ben Echo AI, size nasıl yardımcı olabilirim? 👋", False), 1)

    def add_message(self, text, is_user=True):
        chat_bubble = ChatBubble(text=text, is_user=is_user)
        self.ids.chat_container.add_widget(chat_bubble)
        self.chat_history.append((text, is_user))
        
        Clock.schedule_once(lambda dt: setattr(
            self.ids.chat_scroll, 'scroll_y', 0))

    def send_message(self):
        message = self.ids.message_input.text.strip()
        if message:
            self.add_message(message)
            self.ids.message_input.text = ""
            Clock.schedule_once(lambda dt: self.get_ai_response(message), 1)

    def get_ai_response(self, user_message):
        response = random.choice(DEMO_RESPONSES)
        self.add_message(response, False)

class ProfileScreen(Screen):
    def on_enter(self):
        pass

    def save_profile(self):
        pass

class ChatbotApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Darkblue"
        
        Window.size = (400, 700)
        
        Builder.load_file(os.path.join(os.path.dirname(__file__), 'chatbot.kv'))
        
        sm = MainScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(ChatScreen(name='chat'))
        sm.add_widget(ProfileScreen(name='profile'))
        
        return sm

    def show_menu(self, widget):
        buttons = [
            {
                "text": "Profil",
                "on_release": lambda x: self.menu_callback("profile"),
            },
            {
                "text": "Çıkış",
                "on_release": lambda x: self.menu_callback("logout"),
            }
        ]
        
        self.dialog = MDDialog(
            title="Menü",
            text="Lütfen bir seçenek seçin:",
            buttons=[
                Button(
                    text=item["text"],
                    on_release=item["on_release"],
                    background_color=(0, 0, 0, 0),
                    color=get_color_from_hex('#FFFFFF')
                ) for item in buttons
            ],
        )
        self.dialog.open()

    def menu_callback(self, option):
        self.dialog.dismiss()
        if option == "profile":
            self.root.current = 'profile'
        elif option == "logout":
            self.root.current = 'login'

if __name__ == '__main__':
    ChatbotApp().run()