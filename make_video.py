from PIL import Image, ImageDraw, ImageFont
import os

AYATS = [
    ("بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ", "شروع اللہ کے نام سے جو بڑا مہربان نہایت رحم والا ہے"),
    ("الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ", "تمام تعریفیں اللہ ہی کے لیے ہیں جو تمام جہانوں کا پالنے والا ہے"),
    ("الرَّحْمَٰنِ الرَّحِيمِ", "بڑا مہربان نہایت رحم والا"),
    ("مَالِكِ يَوْمِ الدِّينِ", "بدلے کے دن کا مالک"),
    ("إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ", "ہم تیری ہی عبادت کرتے ہیں اور تجھ ہی سے مدد چاہتے ہیں"),
    ("اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ", "ہمیں سیدھا راستہ دکھا"),
    ("صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ", "ان لوگوں کا راستہ جن پر تو نے انعام کیا، نہ ان کا جن پر غضب ہوا اور نہ گمراہوں کا"),
]

W, H = 1080, 1920
os.makedirs("frames", exist_ok=True)

for i, (arabic, urdu) in enumerate(AYATS):
    img = Image.new("RGB", (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font_ar = ImageFont.truetype("NotoNaskhArabic-Bold.ttf", 80)
        font_ur = ImageFont.truetype("NotoNastaliqUrdu-Regular.ttf", 60)
    except:
        font_ar = ImageFont.load_default()
        font_ur = ImageFont.load_default()
    draw.text((W//2, H//2 - 200), arabic, fill=(255, 215, 0), font=font_ar, anchor="mm")
    draw.text((W//2, H//2 + 100), urdu, fill=(255, 255, 255), font=font_ur, anchor="mm")
    draw.text((W//2, H - 200), f"Surah Fatiha - Ayat {i+1}", fill=(255, 215, 0), font=font_ur, anchor="mm")
    img.save(f"frames/frame_{i}.png")
    print(f"Frame {i+1} ban gaya!")
print("Ho gaya!")
