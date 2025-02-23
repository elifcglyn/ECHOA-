from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle
from datetime import datetime
from kivy.uix.modalview import ModalView
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
from kivy.uix.button import Button

# Kivy dosyasını yükle
Builder.load_file('echoai.kv')

# Koyu mavi tema için pencere arka planını ayarla
Window.clearcolor = (0.23, 0.28, 0.56, 1)  # RGB for #3B4990

class MessageBubble(BoxLayout):
    def __init__(self, text="", is_user=True, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(80)  # Yüksekliği artırdık
        self.padding = [dp(10), dp(5)]
        self.spacing = dp(5)
        
        # Mesaj içeriği için container
        content = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50)
        )
        
        # Mesaj metni
        self.label = Label(
            text=text,
            color=(1, 1, 1, 1),
            size_hint_x=1,
            text_size=(None, None),
            halign='right' if is_user else 'left',
            valign='middle',
            padding=[dp(15), dp(10)]
        )
        
        # Mesaj baloncuğu arka planı
        with content.canvas.before:
            Color(*(0.16, 0.2, 0.38, 1) if is_user else (0.3, 0.35, 0.5, 1))
            self.rect = RoundedRectangle(radius=[dp(15)])
        
        content.bind(pos=self.update_rect, size=self.update_rect)
        content.add_widget(self.label)
        
        # Zaman etiketi
        time_label = Label(
            text=datetime.now().strftime('%H:%M'),
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=dp(20),
            font_size=dp(12),
            halign='right' if is_user else 'left'
        )
        
        self.add_widget(content)
        self.add_widget(time_label)
        
        # Hizalama
        self.pos_hint = {'right': 0.98} if is_user else {'x': 0.02}
        self.size_hint_x = 0.7

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class WelcomeScreen(Screen):
    pass

class LoginScreen(Screen):
    def do_login(self, email, password):
        if email.strip() and password.strip():
            self.manager.current = 'chat'
            # Hoş geldin mesajını göster
            chat_screen = self.manager.get_screen('chat')
            chat_screen.user_email = email.strip()
            
    def go_to_signup(self):
        self.manager.current = 'signup'
    
    def go_to_forgot_password(self):
        self.manager.current = 'forgot'

class EditProfileScreen(Screen):
    user_email = StringProperty("")
    
    def on_enter(self):
        # Kullanıcı bilgilerini yükle
        chat_screen = App.get_running_app().root.get_screen('chat')
        self.user_email = chat_screen.user_email
        
    def save_profile(self, name, email):
        if name.strip() and email.strip():
            # Profil bilgilerini güncelle
            chat_screen = App.get_running_app().root.get_screen('chat')
            chat_screen.user_email = email
            self.manager.current = 'chat'

class NavigationDrawer(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.8, 1)
        self.pos_hint = {'x': 0}
        self.background_color = (0.16, 0.2, 0.38, 0.97)
        self.auto_dismiss = True
        self.is_dark_mode = True

    def on_touch_down(self, touch):
        # Menü dışına tıklandığında kapat
        if not self.collide_point(*touch.pos):
            self.dismiss()
            return True
        return super().on_touch_down(touch)

    def close_menu(self, *args):
        self.dismiss()

    def new_chat(self):
        chat_screen = App.get_running_app().root.get_screen('chat')
        chat_screen.clear_and_start_new_chat()
        self.dismiss()

    def edit_profile(self):
        app = App.get_running_app()
        app.root.current = 'edit_profile'
        self.dismiss()

    def change_model(self):
        chat_screen = App.get_running_app().root.get_screen('chat')
        # Model değiştirme işlemi
        models = ['GPT-3.5', 'GPT-4', 'Claude', 'ECHO Basic']
        current_index = 0
        next_index = (current_index + 1) % len(models)
        chat_screen.current_model = models[next_index]
        chat_screen.add_message(f"Model değiştirildi: {models[next_index]}", False)
        self.dismiss()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        app = App.get_running_app()
        chat_screen = app.root.get_screen('chat')
        
        if self.is_dark_mode:
            Window.clearcolor = (0.23, 0.28, 0.56, 1)  # Koyu tema
            chat_screen.add_message("Koyu tema aktif", False)
        else:
            Window.clearcolor = (0.9, 0.9, 1, 1)  # Açık tema
            chat_screen.add_message("Açık tema aktif", False)
        
        self.dismiss()

    def logout(self):
        app = App.get_running_app()
        chat_screen = app.root.get_screen('chat')
        # Sohbet geçmişini temizle
        chat_screen.ids.chat_history.clear_widgets()
        # Kullanıcı bilgilerini sıfırla
        chat_screen.user_email = ""
        # Welcome ekranına dön
        app.root.current = 'welcome'
        self.dismiss()

class ChatScreen(Screen):
    chat_history = ObjectProperty(None)
    message_input = ObjectProperty(None)
    user_email = StringProperty("")
    nav_drawer = None
    current_model = StringProperty("ECHO Basic")

    def on_enter(self):
        # Yeni bir NavigationDrawer oluştur
        self.nav_drawer = NavigationDrawer()
        user_name = self.user_email.split('@')[0]
        welcome_msg = f"Merhaba {user_name}! Size nasıl yardımcı olabilirim?"
        Clock.schedule_once(lambda dt: self.add_message(welcome_msg, False), 1)

    def toggle_nav_drawer(self):
        # Eğer nav_drawer yoksa oluştur
        if not self.nav_drawer:
            self.nav_drawer = NavigationDrawer()
        
        # Eğer menü açıksa kapat, kapalıysa aç
        if self.nav_drawer.parent:
            self.nav_drawer.dismiss()
        else:
            self.add_widget(self.nav_drawer)

    def send_message(self):
        message = self.ids.message_input.text.strip()
        if message:
            self.add_message(message, True)
            self.ids.message_input.text = ''
            Clock.schedule_once(lambda dt: self.ai_response(message), 1)

    def add_message(self, text, is_user=True):
        bubble = MessageBubble(text=text, is_user=is_user)
        self.ids.chat_history.add_widget(bubble)
        Clock.schedule_once(lambda dt: self.scroll_to_bottom())

    def scroll_to_bottom(self):
        scroll_view = self.ids.chat_scroll
        scroll_view.scroll_y = 0

    def clear_and_start_new_chat(self):
        # Sohbet geçmişini temizle
        self.ids.chat_history.clear_widgets()
        # Yeni sohbet başlangıç mesajı
        welcome_msg = f"Yeni sohbet başlatıldı. Size nasıl yardımcı olabilirim?"
        Clock.schedule_once(lambda dt: self.add_message(welcome_msg, False), 0.5)

    def ai_response(self, user_message):
        model_prefix = f"[{self.current_model}] "
        responses = {
            "merhaba": "Merhaba! Nasıl yardımcı olabilirim?",
            "nasılsın": "İyiyim, teşekkür ederim! Size nasıl yardımcı olabilirim?",
            "görüşürüz": "Görüşmek üzere! İyi günler!",
            "selam": "Selam! Bugün size nasıl yardımcı olabilirim?",
            "teşekkür": "Rica ederim! Başka bir konuda yardıma ihtiyacınız var mı?",
            "yardım": "Size hangi konuda yardımcı olabilirim?",
            "ne yapabilirsin": "Size çeşitli konularda yardımcı olabilirim:\n- Sorularınızı yanıtlayabilirim\n- Bilgi verebilirim\n- Önerilerde bulunabilirim",
            "kimsin": f"Ben ECHO AI ({self.current_model}), size yardımcı olmak için tasarlanmış bir yapay zeka asistanıyım.",
            "model": f"Şu anda {self.current_model} modelini kullanıyorum.",
        }
        
        response = "Anlıyorum. Size başka nasıl yardımcı olabilirim?"
        for key in responses:
            if key in user_message.lower():
                response = responses[key]
                break
                
        self.add_message(model_prefix + response, False)

class SignUpScreen(Screen):
    def do_signup(self, email, password, confirm_password):
        if email.strip() and password.strip():
            if password != confirm_password:
                return  # Şifreler eşleşmiyor
            # Başarılı kayıt sonrası login ekranına dön
            self.manager.current = 'login'

class ForgotPasswordScreen(Screen):
    def reset_password(self, email):
        if email.strip():
            # Şifre sıfırlama emaili gönderildi varsayalım
            self.manager.current = 'login'

class EchoAIApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(ChatScreen(name='chat'))
        sm.add_widget(SignUpScreen(name='signup'))
        sm.add_widget(ForgotPasswordScreen(name='forgot'))
        sm.add_widget(EditProfileScreen(name='edit_profile'))
        return sm

if __name__ == '__main__':
    EchoAIApp().run() 