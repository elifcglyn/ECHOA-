from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle
from datetime import datetime
from kivy.uix.modalview import ModalView
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
from kivy.uix.button import Button
import openai
from kivy.clock import mainthread
from openai import OpenAI

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
            if self.parent:
                self.parent.remove_widget(self)
            return True
        return super().on_touch_down(touch)

    def close_menu(self, *args):
        if self.parent:
            self.parent.remove_widget(self)

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
    current_model = StringProperty("GPT-3.5")
    credits = NumericProperty(100)  # Başlangıç kredisi
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # OpenAI istemcisini oluştur
        self.client = OpenAI(
            api_key="sk-..."  # OpenAI API anahtarınızı buraya yazın
        )
        
        # Sohbet geçmişi için liste
        self.messages = [
            {"role": "system", "content": "Sen yardımcı bir AI asistanısın. Türkçe konuşuyorsun."}
        ]
        
        # Önceden tanımlanmış yanıtlar
        self.quick_responses = {
            "merhaba": "Merhaba! Size nasıl yardımcı olabilirim?",
            "selam": "Selam! Bugün size nasıl yardımcı olabilirim?",
            "nasılsın": "İyiyim, teşekkür ederim! Siz nasılsınız?",
            "teşekkürler": "Rica ederim! Başka bir konuda yardıma ihtiyacınız var mı?",
            "görüşürüz": "Görüşmek üzere! İyi günler dilerim.",
            "yardım": """Size şu konularda yardımcı olabilirim:
- Sorularınızı yanıtlama
- Kod yazma ve düzeltme
- Metin düzenleme ve yazma
- Matematik problemleri çözme
- Genel bilgi ve tavsiye verme""",
            "ne yapabilirsin": """Yapabileceklerimden bazıları:
1. Programlama ve kodlama yardımı
2. Matematik ve fen soruları
3. Metin yazma ve düzenleme
4. Araştırma ve analiz
5. Yaratıcı yazım ve beyin fırtınası
6. Dil öğrenme desteği
7. Genel bilgi ve tavsiyeler""",
        }
        
        # Model başına kredi maliyeti
        self.model_costs = {
            "GPT-3.5": 1,    # Her mesaj 1 kredi
            "GPT-4": 5,      # Her mesaj 5 kredi
            "Claude": 3,      # Her mesaj 3 kredi
            "ECHO Basic": 0   # Ücretsiz
        }

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
            self.remove_widget(self.nav_drawer)
        else:
            self.add_widget(self.nav_drawer)

    def on_leave(self):
        # Ekrandan çıkarken menüyü kapat
        if self.nav_drawer and self.nav_drawer.parent:
            self.remove_widget(self.nav_drawer)

    def send_message(self):
        message = self.ids.message_input.text.strip()
        if message:
            # Kullanıcı mesajını ekrana ekle
            self.add_message(message, True)
            self.ids.message_input.text = ''
            
            # Mesajı geçmişe ekle
            self.messages.append({"role": "user", "content": message})
            
            # Yazıyor... göster
            self.show_typing()
            
            # AI yanıtını al
            Clock.schedule_once(lambda dt: self.get_ai_response(), 1)

    def show_typing(self):
        typing_bubble = MessageBubble(text="Yazıyor...", is_user=False)
        self.ids.chat_history.add_widget(typing_bubble)
        self.typing_bubble = typing_bubble
        self.scroll_to_bottom()

    def get_ai_response(self):
        try:
            # Kredi kontrolü
            cost = self.model_costs.get(self.current_model, 1)
            if self.credits < cost:
                if hasattr(self, 'typing_bubble'):
                    self.ids.chat_history.remove_widget(self.typing_bubble)
                self.add_message("Üzgünüm, yeterli krediniz kalmadı. Lütfen kredi yükleyin.", False)
                return

            # Hızlı yanıtlar için kredi düşülmez
            user_message = self.messages[-1]["content"].lower()
            for key, response in self.quick_responses.items():
                if key in user_message:
                    if hasattr(self, 'typing_bubble'):
                        self.ids.chat_history.remove_widget(self.typing_bubble)
                    self.add_message(response, False)
                    return

            # API çağrısı
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=self.messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                # API çağrısı başarılıysa krediyi düş
                self.credits -= cost
                
                # Kullanılan krediyi göster
                self.add_message(f"💰 {cost} kredi kullanıldı. Kalan: {self.credits}", False)
                
                # Yanıtı göster
                if hasattr(self, 'typing_bubble'):
                    self.ids.chat_history.remove_widget(self.typing_bubble)
                ai_message = response.choices[0].message.content
                self.messages.append({"role": "assistant", "content": ai_message})
                self.add_message(ai_message, False)
                
                # Kredi uyarısı
                if self.credits < 10:
                    self.add_message(f"⚠️ Uyarı: Sadece {self.credits} krediniz kaldı!", False)
                
            except Exception as e:
                raise e

        except Exception as e:
            if hasattr(self, 'typing_bubble'):
                self.ids.chat_history.remove_widget(self.typing_bubble)
            error_msg = f"API Hatası: {str(e)}"
            print(error_msg)
            self.add_message("Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.", False)

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
        # Mesaj listesini sıfırla
        self.messages = [
            {"role": "system", "content": "Sen yardımcı bir AI asistanısın. Türkçe konuşuyorsun."}
        ]
        # Yeni sohbet başlangıç mesajı
        welcome_msg = f"Yeni sohbet başlatıldı. Size nasıl yardımcı olabilirim?"
        Clock.schedule_once(lambda dt: self.add_message(welcome_msg, False), 0.5)

    def change_model(self, model_name):
        self.current_model = model_name
        cost = self.model_costs.get(model_name, 1)
        self.add_message(f"Model değiştirildi: {model_name} (Her mesaj {cost} kredi)", False)

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

class CreditScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.credits = 0
    
    def buy_credits(self, amount):
        # Burada ödeme işlemi yapılacak
        self.show_payment_modal(amount)
    
    def show_payment_modal(self, amount):
        payment_modal = PaymentModal(amount=amount)
        payment_modal.open()

class PaymentModal(ModalView):
    def __init__(self, amount, **kwargs):
        super().__init__(**kwargs)
        self.amount = amount
        self.size_hint = (0.8, 0.6)
        self.background_color = (0.16, 0.2, 0.38, 0.97)

    def process_payment(self, card_number, expiry, cvv):
        # Burada gerçek ödeme işlemi yapılacak
        if len(card_number) == 16 and len(expiry) == 5 and len(cvv) == 3:
            # Başarılı ödeme simülasyonu
            chat_screen = App.get_running_app().root.get_screen('chat')
            chat_screen.add_message(f"{self.amount} kredi başarıyla yüklendi!", False)
            self.dismiss()
            App.get_running_app().root.current = 'chat'

class EchoAIApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(ChatScreen(name='chat'))
        sm.add_widget(SignUpScreen(name='signup'))
        sm.add_widget(ForgotPasswordScreen(name='forgot'))
        sm.add_widget(EditProfileScreen(name='edit_profile'))
        sm.add_widget(CreditScreen(name='credit'))  # Yeni ekran
        return sm

if __name__ == '__main__':
    EchoAIApp().run() 