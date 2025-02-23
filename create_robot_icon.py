from PIL import Image, ImageDraw
import os

# assets klasörünü oluştur (eğer yoksa)
if not os.path.exists('assets'):
    os.makedirs('assets')

# Yeni bir resim oluştur
size = (200, 200)
image = Image.new('RGBA', size, (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Robot başı
draw.ellipse([50, 30, 150, 130], fill='white')

# Robot gözleri
draw.ellipse([75, 60, 95, 80], fill='#3B4990')
draw.ellipse([105, 60, 125, 80], fill='#3B4990')

# Robot anteni
draw.rectangle([95, 10, 105, 30], fill='white')
draw.ellipse([90, 0, 110, 20], fill='white')

# Robot gövdesi
draw.rectangle([70, 130, 130, 170], fill='white')

# Kaydet
image.save('assets/robot.png')
print("Robot ikonu başarıyla oluşturuldu: assets/robot.png")