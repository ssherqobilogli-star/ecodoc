"""
EcoDoc - Ekologik chiqindi hujjatlarini avtomatlashtiruvchi bot
config.py - Asosiy sozlamalar va konstantalar

Muallif: Sardor
Loyiha: EcoDoc (O'zbek + Nemis versiyalari)
Maqsad: Ausbildung portfolio (Kreislaufwirtschaft)
"""

import os
from dotenv import load_dotenv

# .env fayldan yashirin kalitlarni yuklash
# Bu fayl GitHub'ga yuklanmaydi (xavfsizlik uchun)
load_dotenv()

# ==========================================
# ASOSIY SOZLAMALAR
# ==========================================

# Telegram Bot Token (BotFather'dan olingan)
BOT_TOKEN = os.getenv("BOT_TOKEN", "SIZNING_BOT_TOKENINGIZ")

# Groq API kaliti (groq.com'dan olingan)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "SIZNING_GROQ_API_KALITINGIZ")

# Groq modeli (tez va aniq)
GROQ_MODEL = "llama-3.3-70b-versatile"

# Ma'lumotlar bazasi joylashuvi
DATABASE_PATH = "data/ecodoc.db"

# Hisobotlar saqlanadigan papka
REPORTS_DIR = "data/reports"

# ==========================================
# TILLAR SOZLAMALARI
# ==========================================

# Qo'llab-quvvatlanadigan tillar
LANGUAGES = {
    "uz": "O'zbekcha 🇺🇿",
    "de": "Deutsch 🇩🇪"
}

# Standart til
DEFAULT_LANGUAGE = "uz"

# ==========================================
# O'ZBEKISTON SOZLAMALARI
# ==========================================

UZ_CONFIG = {
    "country": "O'zbekiston",
    "currency": "UZS (so'm)",
    "date_format": "%d.%m.%Y",
    "phone_format": "+998 XX XXX XX XX",
    "laws": [
        "O'zbekiston Respublikasi ekologiya qonuni",
        "Chiqindilarni boshqarish to'g'risidagi qonun",
        "Atrof-muhitni muhofaza qilish qoidalar"
    ],
    "doc_title": "EKologik chiqindi hisoboti",
    "organization_label": "Tashkilot",
    "waste_type_label": "Chiqindi turi",
    "quantity_label": "Miqdori (kg)",
    "date_label": "Sana",
    "responsible_label": "Mas'ul shaxs",
    "signature_label": "Imzo"
}

# ==========================================
# GERMANIYA SOZLAMALARI (Ausbildung uchun)
# ==========================================

DE_CONFIG = {
    "country": "Deutschland",
    "currency": "EUR (€)",
    "date_format": "%d.%m.%Y",
    "phone_format": "+49 XXX XXXXXXX",
    # Nemis qonunlari - Kreislaufwirtschaft sohasi
    "laws": [
        "Kreislaufwirtschaftsgesetz (KrWG)",  # Qayta ishlash qonuni
        "Verpackungsgesetz (VerpackG)",       # Qadoqlash qonuni
        "Elektro- und Elektronikgerätegesetz (ElektroG)",  # Elektronika
        "Battery Act (BattG)",                # Batareya qonuni
        "Abfallverzeichnis-Verordnung (AVV)"  # Chiqindi ro'yxati
    ],
    "doc_title": "Abfallnachweis / Recycling-Dokumentation",
    "organization_label": "Betrieb / Unternehmen",
    "waste_type_label": "Abfallart",
    "quantity_label": "Menge (kg)",
    "date_label": "Datum",
    "responsible_label": "Verantwortliche Person",
    "signature_label": "Unterschrift",
    # Nemis chiqindi turlari (Kreislaufwirtschaft uchun)
    "waste_categories": [
        "Verpackungsabfälle (Kunststoff)",      # Plastik qadoq chiqindisi
        "Verpackungsabfälle (Papier/Karton)",   # Qog'oz qadoq
        "Verpackungsabfälle (Glas)",            # Shisha qadoq
        "Verpackungsabfälle (Metall)",          # Metal qadoq
        "Elektroaltgeräte",                      # Eski elektronika
        "Batterien und Akkumulatoren",           # Batareyalar
        "Altöl",                                 # Eski yog'
        "Altreifen",                             # Eski shinlar
        "Bauschutt",                             # Qurilish chiqindisi
        "Gewerbeabfälle (nicht gefährlich)",     # Xavfsiz sanoat chiqindisi
        "Gefährliche Abfälle"                    # Xavfli chiqindilar
    ]
}

# ==========================================
# XATOLIK XABARLARI
# ==========================================

ERROR_MESSAGES = {
    "uz": {
        "general_error": "❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.",
        "invalid_input": "⚠️ Noto'g'ri ma'lumot. Iltimos, qayta kiriting.",
        "api_error": "🤖 AI xizmatida muammo. Keyinroq urinib ko'ring.",
        "file_error": "📄 Fayl yaratishda xatolik.",
        "db_error": "💾 Ma'lumotlar bazasida xatolik."
    },
    "de": {
        "general_error": "❌ Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut.",
        "invalid_input": "⚠️ Ungültige Eingabe. Bitte erneut eingeben.",
        "api_error": "🤖 Problem mit dem KI-Dienst. Bitte später versuchen.",
        "file_error": "📄 Fehler beim Erstellen der Datei.",
        "db_error": "💾 Datenbankfehler."
    }
}

# ==========================================
# LOG SOZLAMALARI
# ==========================================

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "data/ecodoc.log"
