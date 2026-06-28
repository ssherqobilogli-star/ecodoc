"""
EcoDoc - Ekologik chiqindi hujjatlarini avtomatlashtiruvchi bot
utils.py - Yordamchi funksiyalar va utility'lar

Bu modul quyidagilarni qiladi:
1. Fayllarni boshqarish (nusxa olish, o'chirish)
2. Matn formatlash
3. Vaqt va sana bilan ishlash
4. Logging yordamchilari
5. Xatoliklarni qayta ishlash
"""

import os
import shutil
from datetime import datetime, timedelta
from typing import Optional
import logging

from config import REPORTS_DIR, LOG_FILE

logger = logging.getLogger(__name__)


def ensure_directory(path: str):
    """
    Papka mavjudligini tekshirish, yo'q bo'lsa yaratish.

    Args:
        path: Papka yo'li
    """
    os.makedirs(path, exist_ok=True)


def clean_old_reports(days: int = 30):
    """
    Eski hisobot fayllarini tozalash.

    Args:
        days: Necha kundan eski fayllarni o'chirish (standart: 30 kun)
    """
    try:
        if not os.path.exists(REPORTS_DIR):
            return

        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0

        for filename in os.listdir(REPORTS_DIR):
            file_path = os.path.join(REPORTS_DIR, filename)

            if os.path.isfile(file_path):
                file_modified = datetime.fromtimestamp(os.path.getmtime(file_path))

                if file_modified < cutoff_date:
                    os.remove(file_path)
                    deleted_count += 1

        logger.info(f"🗑️ {deleted_count} ta eski fayl o'chirildi")

    except Exception as e:
        logger.error(f"❌ Eski fayllarni tozalashda xatolik: {e}")


def format_file_size(size_bytes: int) -> str:
    """
    Fayl hajmini inson o'qiy oladigan formatga o'tkazish.

    Args:
        size_bytes: Fayl hajmi baytlarda

    Returns:
        str: Formatlangan hajm (masalan: "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def get_file_info(file_path: str) -> Optional[dict]:
    """
    Fayl haqida ma'lumot olish.

    Args:
        file_path: Fayl yo'li

    Returns:
        dict: Fayl ma'lumotlari yoki None
    """
    try:
        if not os.path.exists(file_path):
            return None

        stat = os.stat(file_path)

        return {
            "name": os.path.basename(file_path),
            "path": file_path,
            "size": format_file_size(stat.st_size),
            "size_bytes": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).strftime("%d.%m.%Y %H:%M"),
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y %H:%M"),
            "extension": os.path.splitext(file_path)[1].lower()
        }

    except Exception as e:
        logger.error(f"❌ Fayl ma'lumotlarini olishda xatolik: {e}")
        return None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Matnni qisqartirish.

    Args:
        text: Asl matn
        max_length: Maksimal uzunlik
        suffix: Qo'shiladigan suffix

    Returns:
        str: Qisqartirilgan matn
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def escape_markdown(text: str) -> str:
    """
    Telegram Markdown uchun maxsus belgilarni qochirish.

    Args:
        text: Asl matn

    Returns:
        str: Xavfsiz matn
    """
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

    for char in escape_chars:
        text = text.replace(char, f'\\{char}')

    return text


def format_uzbek_phone(phone: str) -> str:
    """
    O'zbek telefon raqamini formatlash.

    Args:
        phone: Telefon raqami (+998XXXXXXXXX)

    Returns:
        str: Formatlangan raqam (+998 90 123 45 67)
    """
    phone = phone.replace(" ", "").replace("-", "")

    if phone.startswith("+998") and len(phone) == 13:
        return f"{phone[:4]} {phone[4:6]} {phone[6:9]} {phone[9:11]} {phone[11:]}"

    return phone


def format_german_phone(phone: str) -> str:
    """
    Nemis telefon raqamini formatlash.

    Args:
        phone: Telefon raqami

    Returns:
        str: Formatlangan raqam
    """
    phone = phone.replace(" ", "").replace("-", "")

    if phone.startswith("+49"):
        return f"{phone[:3]} {phone[3:5]} {phone[5:]}"

    return phone


def generate_report_filename(
    language: str,
    company_name: str,
    waste_type: str,
    report_date: str,
    extension: str = ".docx"
) -> str:
    """
    Hisobot fayli nomini yaratish.

    Args:
        language: Til kodi
        company_name: Korxona nomi
        waste_type: Chiqindi turi
        report_date: Hisobot sanasi
        extension: Fayl kengaytmasi

    Returns:
        str: Fayl nomi
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    lang_prefix = "UZ" if language == "uz" else "DE"

    # Xavfsiz fayl nomi
    safe_company = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_company = safe_company[:30].replace(" ", "_")

    safe_waste = "".join(c for c in waste_type if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_waste = safe_waste[:20].replace(" ", "_")

    return f"EcoDoc_{lang_prefix}_{safe_company}_{safe_waste}_{timestamp}{extension}"


def get_welcome_message(language: str = "uz") -> str:
    """
    Xush kelibsiz xabarini olish.

    Args:
        language: Til kodi

    Returns:
        str: Xush kelibsiz xabari
    """
    if language == "uz":
        return (
            "👋 *EcoDoc ga xush kelibsiz!*\n"
            "🏢 Bu bot ekologik chiqindi hujjatlarini AI yordamida avtomat yaratadi.\n"
            "*Imkoniyatlar:*"
            "• 🏢 Korxona ma'lumotlarini saqlash"
            "• 🤖 AI yordamida professional hisobot"
            "• 📄 Word (.docx) hujjat yaratish"
            "• 📁 Hisobotlar arxivi\n"
            "*Buyruqlar:*"
            "/start - Botni ishga tushirish"
            "/help - Yordam"
            "/language - Tilni o'zgartirish"
        )
    else:
        return (
            "👋 *Willkommen bei EcoDoc!*\n"
            "🏢 Dieser Bot erstellt automatisch ökologische Abfallberichte mit KI.\n"
            "*Funktionen:*"
            "• 🏢 Unternehmensdaten speichern"
            "• 🤖 Professioneller KI-Bericht"
            "• 📄 Word (.docx) Dokument erstellen"
            "• 📁 Berichtsarchiv\n"
            "*Befehle:*"
            "/start - Bot starten"
            "/help - Hilfe"
            "/language - Sprache ändern"
        )


def log_user_action(user_id: int, action: str, details: str = ""):
    """
    Foydalanuvchi harakatini log'ga yozish.

    Args:
        user_id: Foydalanuvchi IDsi
        action: Harakat nomi
        details: Qo'shimcha ma'lumot
    """
    logger.info(f"👤 User {user_id} | Action: {action} | {details}")


# Test uchun
if __name__ == "__main__":
    print("🧪 Utils testlari...")

    # Telefon formatlash
    print(f"📱 UZ: {format_uzbek_phone('+998901234567')}")
    print(f"📱 DE: {format_german_phone('+491701234567')}")

    # Fayl nomi
    print(f"📄 Filename: {generate_report_filename('uz', 'Test Korxona', 'Plastik', '15.06.2026')}")

    # Matn qisqartirish
    print(f"✂️ Truncate: {truncate_text('Bu juda uzun matn', 10)}")

    print("✅ Testlar tugadi!")
