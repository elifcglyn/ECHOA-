
# Kredi Sistemi ile LLM Sohbet Uygulaması
#BU BİR EKİP ÇALIŞMASIDIR
## Proje Açıklaması
Bu proje, kullanıcıların kayıt olup giriş yapabildiği, kredi bakiyesini kullanarak sohbet edebildiği ve farklı LLM modelleri arasından seçim yapabildiği bir mobil sohbet uygulamasıdır. Kullanıcılar belirli bir kredi karşılığında mesaj gönderebilir ve ek kredi satın alabilir.

## Özellikler
- **Kullanıcı Kimlik Doğrulama & Profil Yönetimi**
  - Güvenli kayıt ve giriş işlemleri (Firebase, Supabase veya özel bir backend ile)
  - Kullanıcı profili ve kredi bakiyesi yönetimi
  
- **Sohbet Arayüzü & Çoklu LLM Seçimi**
  - Sezgisel sohbet arayüzü (mesaj balonları, avatarlar, zaman damgaları vb.)
  - Kullanıcıların birden fazla LLM sağlayıcısından seçim yapabilmesi
  - Gerçek zamanlı geri bildirim ve animasyonlar
  
- **LLM API Entegrasyonu**
  - OpenAI gibi sağlayıcılarla entegrasyon
  - Dinamik API çağrıları ve hata yönetimi
  - Gelecekte daha fazla LLM eklenmesine uygun yapı

- **Kredi Sistemi & Ödeme Entegrasyonu**
  - Mesaj başına kredi düşüşü
  - Kredi satın alma (gerçek ödeme veya simüle edilmiş sistem)
  - İşlem kayıtları ve kullanıcıya geri bildirim

## Kullanılan Teknolojiler
- **Frontend:** Kivy
- **Backend:** Firebase, Supabase veya özel bir REST API
- **Veritabanı:** Firestore, PostgreSQL, MongoDB
- **LLM Entegrasyonu:** OpenAI API, diğer LLM sağlayıcıları






