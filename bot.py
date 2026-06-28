"""
EcoDoc - Ekologik chiqindi hujjatlarini avtomatlashtiruvchi bot
bot.py - Telegram bot asosiy logikasi

Bu modul quyidagilarni qiladi:
1. Botni ishga tushirish va sozlash
2. Foydalanuvchi buyruqlarini qabul qilish
3. Dialog oqimini boshqarish (state machine)
4. Ma'lumotlarni qabul qilish va saqlash
5. Hisobot yaratish va yuborish
6. Til almashtirish (O'zbek/Nemis)

Ausbildung uchun: Professional bot arxitekturasi!
"""

import os
import logging
from typing import Dict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

from config import BOT_TOKEN, LANGUAGES, DEFAULT_LANGUAGE, UZ_CONFIG, DE_CONFIG
from database import (
    init_database, add_user, get_user,
    add_company, get_user_companies,
    add_waste_report, get_user_reports
)
from validators import (
    validate_all_company_data, validate_date,
    validate_quantity, validate_waste_type
)
from ai_generator import generate_waste_report
from report import create_word_report

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==========================================
# DIALOG HOLATLARI (Conversation States)
# ==========================================

# Asosiy holatlar
MENU, LANGUAGE_SELECT = range(2)

# Korxona qo'shish holatlari
COMPANY_NAME, COMPANY_ADDRESS, COMPANY_INN, COMPANY_PHONE, COMPANY_EMAIL, COMPANY_DIRECTOR, COMPANY_CONFIRM = range(2, 9)

# Hisobot yaratish holatlari
REPORT_SELECT_COMPANY, REPORT_WASTE_TYPE, REPORT_QUANTITY, REPORT_DATE, REPORT_DESCRIPTION, REPORT_CONFIRM, REPORT_GENERATE = range(9, 16)

# Sozlamalar holatlari
SETTINGS_LANGUAGE, SETTINGS_COMPANY = range(16, 18)

# ==========================================
# TUGMALAR (Keyboards)
# ==========================================

def get_main_menu_keyboard(language: str = "uz") -> InlineKeyboardMarkup:
    """
    Asosiy menyu tugmalarini yaratish.

    Args:
        language: Foydalanuvchi tili

    Returns:
        InlineKeyboardMarkup: Tugmalar
    """
    if language == "uz":
        buttons = [
            [InlineKeyboardButton("🏢 Yangi korxona qo'shish", callback_data="add_company")],
            [InlineKeyboardButton("📋 Hisobot yaratish", callback_data="create_report")],
            [InlineKeyboardButton("📁 Mening hisobotlarim", callback_data="my_reports")],
            [InlineKeyboardButton("⚙️ Sozlamalar", callback_data="settings")],
            [InlineKeyboardButton("❓ Yordam", callback_data="help")],
        ]
    else:  # Nemis
        buttons = [
            [InlineKeyboardButton("🏢 Neues Unternehmen", callback_data="add_company")],
            [InlineKeyboardButton("📋 Bericht erstellen", callback_data="create_report")],
            [InlineKeyboardButton("📁 Meine Berichte", callback_data="my_reports")],
            [InlineKeyboardButton("⚙️ Einstellungen", callback_data="settings")],
            [InlineKeyboardButton("❓ Hilfe", callback_data="help")],
        ]

    return InlineKeyboardMarkup(buttons)


def get_language_keyboard() -> InlineKeyboardMarkup:
    """
    Til tanlash tugmalarini yaratish.

    Returns:
        InlineKeyboardMarkup: Til tugmalari
    """
    buttons = [
        [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_cancel_keyboard(language: str = "uz") -> InlineKeyboardMarkup:
    """
    Bekor qilish tugmasini yaratish.

    Args:
        language: Foydalanuvchi tili

    Returns:
        InlineKeyboardMarkup: Bekor qilish tugmasi
    """
    text = "❌ Bekor qilish" if language == "uz" else "❌ Abbrechen"
    buttons = [[InlineKeyboardButton(text, callback_data="cancel")]]
    return InlineKeyboardMarkup(buttons)


# ==========================================
# START VA TIL TANLASH
# ==========================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start buyrug'ini qayta ishlash.
    Yangi foydalanuvchini ro'yxatdan o'tkazish yoki mavjudini yangilash.
    """
    user = update.effective_user

    # Foydalanuvchini bazaga qo'shish/yangilash
    add_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language=DEFAULT_LANGUAGE
    )

    # Til tanlash taklif qilish
    welcome_text = (
        "👋 *EcoDoc ga xush kelibsiz!*

"
        "Bu bot ekologik chiqindi hujjatlarini AI yordamida avtomat yaratadi.

"
        "🌍 Tilni tanlang / Sprache wählen:"
    )

    await update.message.reply_text(
        welcome_text,
        reply_markup=get_language_keyboard(),
        parse_mode="Markdown"
    )

    return LANGUAGE_SELECT


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Til tanlash callbackini qayta ishlash.
    """
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    lang_code = query.data.split("_")[1]  # "lang_uz" -> "uz"

    # Foydalanuvchi tilini yangilash
    add_user(telegram_id=user_id, language=lang_code)

    # Tilga qarab xabar
    if lang_code == "uz":
        text = (
            "✅ *O'zbek tili tanlandi!*

"
            "🏢 EcoDoc - ekologik chiqindi hujjatlarini avtomatlashtiruvchi bot.

"
            "*Imkoniyatlar:*
"
            "• 🏢 Korxona ma'lumotlarini saqlash
"
            "• 📋 AI yordamida professional hisobot
"
            "• 📄 Word (.docx) hujjat yaratish
"
            "• 📁 Hisobotlar arxivi

"
            "Quyidagi bo'limlardan birini tanlang:"
        )
    else:
        text = (
            "✅ *Deutsch ausgewählt!*

"
            "🏢 EcoDoc - Automatisiert ökologische Abfallberichte mit KI.

"
            "*Funktionen:*
"
            "• 🏢 Unternehmensdaten speichern
"
            "• 📋 Professioneller KI-Bericht
"
            "• 📄 Word (.docx) Dokument erstellen
"
            "• 📁 Berichtsarchiv

"
            "Wählen Sie einen Bereich:"
        )

    await query.edit_message_text(
        text,
        reply_markup=get_main_menu_keyboard(lang_code),
        parse_mode="Markdown"
    )

    return MENU


# ==========================================
# ASOSIY MENU CALLBACK
# ==========================================

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Asosiy menyu tugmalarini qayta ishlash.
    """
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user_data = get_user(user_id)
    language = user_data.get("language", DEFAULT_LANGUAGE) if user_data else DEFAULT_LANGUAGE

    action = query.data

    if action == "add_company":
        return await start_add_company(query, language)
    elif action == "create_report":
        return await start_create_report(query, user_id, language)
    elif action == "my_reports":
        return await show_reports(query, user_id, language)
    elif action == "settings":
        return await show_settings(query, language)
    elif action == "help":
        return await show_help(query, language)
    elif action == "cancel":
        return await cancel_action(query, language)
    elif action == "back_menu":
        return await back_to_menu(query, language)

    return MENU


async def back_to_menu(query, language: str):
    """
    Asosiy menyuga qaytish.
    """
    if language == "uz":
        text = "📋 Asosiy menyu:"
    else:
        text = "📋 Hauptmenü:"

    await query.edit_message_text(
        text,
        reply_markup=get_main_menu_keyboard(language),
        parse_mode="Markdown"
    )
    return MENU


async def cancel_action(query, language: str):
    """
    Amalni bekor qilish.
    """
    if language == "uz":
        text = "❌ Amal bekor qilindi."
    else:
        text = "❌ Vorgang abgebrochen."

    await query.edit_message_text(
        text,
        reply_markup=get_main_menu_keyboard(language),
        parse_mode="Markdown"
    )
    return MENU


# ==========================================
# KORXONA QO'SHISH (Add Company)
# ==========================================

async def start_add_company(query, language: str):
    """
    Korxona qo'shishni boshlash.
    """
    if language == "uz":
        text = (
            "🏢 *Yangi korxona qo'shish*

"
            "Korxona nomini kiriting:
"
            "(masalan: "O'zbekiston Plastik MCHJ")"
        )
    else:
        text = (
            "🏢 *Neues Unternehmen hinzufügen*

"
            "Geben Sie den Firmennamen ein:
"
            "(z.B.: "Deutschland Recycling GmbH")"
        )

    await query.edit_message_text(
        text,
        reply_markup=get_cancel_keyboard(language),
        parse_mode="Markdown"
    )
    return COMPANY_NAME


async def company_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Korxona nomini qabul qilish.
    """
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    language = user_data.get("language", DEFAULT_LANGUAGE) if user_data else DEFAULT_LANGUAGE

    name = update.message.text.strip()

    # Vaqtinchalik ma'lumotlarni saqlash
    context.user_data["company"] = {"name": name}

    if language == "uz":
        text = "📍 Korxona manzilini kiriting:
(masalan: Toshkent sh., Chilonzor tumani)"
    else:
        text = "📍 Geben Sie die Adresse ein:
(z.B.: Berlin, Hauptstraße 1)"

    await update.message.reply_text(text, reply_markup=get_cancel_keyboard(language))
    return COMPANY_ADDRESS


async def company_address_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Korxona manzilini qabul qilish.
    """
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    language = user_data.get("language", DEFAULT_LANGUAGE) if user_data else DEFAULT_LANGUAGE

    address = update.message.text.strip()
    context.user_data["company"]["address"] = address

    if language == "uz":
        text = "🆔 INN (Identifikatsiya raqami) ni kiriting:
(masalan: 123456789)"
    else:
        text = "🆔 Steuernummer eingeben:
(z.B.: 1234567890)"

    await update.message.reply_text(text, reply_markup=get_cancel_keyboard(language))
    return COMPANY_INN


async def company_inn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    INN/Steuernummer ni qabul qilish.
    """
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    language = user_data.get("language", DEFAULT_LANGUAGE) if user_data else DEFAULT_LANGUAGE

    inn = update.message.text.strip()
    context.user_data["company"]["inn"] = inn

    if language == "uz":
        text = "📞 Telefon raqamini kiriting:
(masalan: +998 90 123 45 67)"
    else:
        text = "📞 Telefonnummer eingeben:
(z.B.: +49 170 1234567)"

    await update.message.reply_text(text, reply_markup=get_cancel_keyboard(language))
    return COMPANY_PHONE


async def company_phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Telefon raqamini qabul qilish.
    """
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    language = user_data.get("language", DEFAULT_LANGUAGE) if user_data else DEFAULT_LANGUAGE

    phone = update.message.text.strip()
    context.user_data["company"]["phone"] = phone

    if language == "uz":
        text = "📧 Email manzilini kiriting (ixtiyoriy):
(yoki "o'tkazib yuborish" deb yozing)"
    else:
        text = "📧 E-Mail eingeben (optional):
(oder "überspringen" schreiben)"

    await update.message.reply_text(text, reply_markup=get_cancel_keyboard(language))
    return COMPANY_EMAIL


async def company_email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Email ni qabul qilish.
    """
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    language = user_data.get("language", DEFAULT_LANGUAGE) if user_data else DEFAULT_LANGUAGE

    email_text = update.message.text.strip().lower()

    if email_text in ["o'tkazib yuborish", "überspringen", "skip", "-"]:
        context.user_data["company"]["email"] = None
    else:
        context.user_data["company"]["email"] = email_text

    if language == "uz":
        text = "👤 Direktor F.I.O. ni kiriting:
(masalan: Valiyev Alijon Alisherovich)"
    else:
        text = "👤 Name des Geschäftsführers:
(z.B.: Max Mustermann)"

    await update.message.reply_text(text, reply_markup=get_cancel_keyboard(language))
    return COMPANY_DIRECTOR


async def company_director_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Direktor ismini qabul qilish va tasdiqlash.
    """
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    language = user_data.get("language", DEFAULT_LANGUAGE) if user_data else DEFAULT_LANGUAGE

    director = update.message.text.strip()
    context.user_data["company"]["director_name"] = director

    company = context.user_data["company"]

    # Ma'lumotlarni tekshirish
    validation = validate_all_company_data(
        name=company.get("name", ""),
        address=company.get("address", ""),
        inn=company.get("inn", ""),
        phone=company.get("phone", ""),
        email=company.get("email"),
        director_name=company.get("director_name"),
        country=language
    )

    if not validation["is_valid"]:
        # Xatoliklar bor
        errors_text = "\n".join([f"• {msg}" for msg in validation["errors"].values()])
        if language == "uz":
            text = f"❌ *Xatoliklar topildi:*\n{errors_text}\n\nIltimos, qayta kiriting."
        else:
            text = f"❌ *Fehler gefunden:*\n{errors_text}\n\nBitte korrigieren."

        await update.message.reply_text(text, parse_mode="Markdown")
        return COMPANY_NAME

    # Tasdiqlash xabari
    if language == "uz":
        text = (
            f"📋 *Korxona ma'lumotlari:*\n\n"
            f"🏢 Nomi: {validation['data']['name']}\n"
            f"📍 Manzil: {validation['data']['address']}\n"
            f"🆔 INN: {validation['data']['inn']}\n"
            f"📞 Telefon: {validation['data']['phone']}\n"
            f"📧 Email: {validation['data'].get('email', '-')}\n"
            f"👤 Direktor: {validation['data'].get('director_name', '-')}\n\n"
            f"✅ Ma'lumotlar to'g'rimi?"
        )
        confirm_text = "✅ Tasdiqlash"
        edit_text = "✏️ Tahrirlash"
    else:
        text = (
            f"📋 *Unternehmensdaten:*\n\n"
            f"🏢 Name: {validation['data']['name']}\n"
            f"📍 Adresse: {validation['data']['address']}\n"
            f"🆔 Steuernummer: {validation['data']['inn']}\n"
            f"📞 Telefon: {validation['data']['phone']}\n"
            f"📧 E-Mail: {validation['data'].get('email', '-')}\n"
            f"👤 Geschäftsführer: {validation['data'].get('director_name', '-')}\n\n"
            f"✅ Sind die Daten korrekt?"
        )
        confirm_text = "✅ Bestätigen"
        edit_text = "✏️ Bearbeiten"

    # Tasdiqlash tugmalari
    buttons = [
        [InlineKeyboardButton(confirm_text, callback_data="confirm_company")],
        [InlineKeyboardButton(edit_text, callback_data="edit_company")],
        [InlineKeyboardButton("❌ Bekor qilish" if language == "uz" else "❌ Abbrechen", 
                              callback_data="cancel")]
    ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

    # Tasdiqlangan ma'lumotlarni saqlash
    context.user_data["validated_company"] = validation["data"]

    return COMPANY_CONFIRM


async def company_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Korxona tasdiqlash callbackini qayta ishlash.
    """
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user_data = get_user(user_id)
    language = user_data.get("language", DEFAULT_LANGUAGE) if user_data else DEFAULT_LANGUAGE

    action = query.data

    if action == "confirm_company":
        # Korxonani bazaga saqlash
        company = context.user_data.get("validated_company", {})

        company_id = add_company(
            user_id=user_id,
            name=company.get("name"),
            address=company.get("address"),
            inn=company.get("inn"),
            phone=company.get("phone"),
            email=company.get("email"),
            director_name=company.get("director_name"),
            country=language
        )

        if company_id > 0:
            if language == "uz":
                text = f"✅ *Korxona muvaffaqiyatli qo'shildi!*\n\nID: {company_id}"
            else:
                text = f"✅ *Unternehmen erfolgreich hinzugefügt!*\n\nID: {company_id}"
        else:
            if language == "uz":
                text = "❌ *Korxona qo'shishda xatolik yuz berdi.*"
            else:
                text = "❌ *Fehler beim Hinzufügen des Unternehmens.*"

        # Vaqtinchalik ma'lumotlarni tozalash
        context.user_data.pop("company", None)
        context.user_data.pop("validated_company", None)

        await query.edit_message_text(
            text,
            reply_markup=get_main_menu_keyboard(language),
            parse_mode="Markdown"
        )
        return MENU

    elif action == "edit_company":
        # Qayta tahrirlash
        return await start_add_company(query, language)

    return MENU


# ==========================================
# HISOBOT YARATISH (Create Report)
# ==========================================

async def start_create_report(query, user_id: int, language: str):
    """
    Hisobot yaratishni boshlash.
    """
    # Foydalanuvchining korxonalari ro'yxatini olish
    companies = get_user_companies(user_id)

    if not companies:
        if language == "uz":
            text = (
                "❌ *Sizda hali korxona qo'shilmagan.*\n\n"
                "Avval korxona qo'shing:"
            )
        else:
            text = (
                "❌ *Sie haben noch kein Unternehmen hinzugefügt.*\n\n"
                "Fügen Sie zuerst ein Unternehmen hinzu:"
            )

        buttons = [
            [InlineKeyboardButton(
                "🏢 Korxona qo'shish" if language == "uz" else "🏢 Unternehmen hinzufügen",
                callback_data="add_company"
            )],
            [InlineKeyboardButton(
                "◀️ Orqaga" if language == "uz" else "◀️ Zurück",
                callback_data="back_menu"
            )]
        ]

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="Markdown"
        )
        return MENU

    # Korxonalar ro'yxatini ko'rsatish
    if language == "uz":
        text = "📋 *Hisobot yaratish*\n\nKorxonani tanlang:"
    else:
        text = "📋 *Bericht erstellen*\n\nUnternehmen auswählen:"

    buttons = []
    for company in companies:
        btn_text = f"🏢 {company['name']}"
        buttons.append([InlineKeyboardButton(btn_text, callback_data=f"comp_{company['id']}")])

    buttons.append([InlineKeyboardButton(
        "◀️ Orqaga" if language == "uz" else "◀️ Zurück",
        callback_data="back_menu"
    )])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

    return REPORT_SELECT_COMPANY


async def report_select_company_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Korxona tanlash callbackini qayta ishlash.
    """
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    user_data = get_user(user_id)
    language = user_data.get("language", DEFAULT_LANGUAGE) if user_data else DEFAULT_LANGUAGE

    company_id = int(query.data.split("_")[1])
    context.user_data["report_company_id"] = company_id

    # Korxona ma'lumotlarini olish
    companies = get_user_companies(user_id)
    selected_company = next((c for c in companies if c["id"] == company_id), None)
    context.user_data["report_company"] = selected_company

    if language == "uz":
        text = (
            f"✅ Korxona tanlandi: *{selected_company['name']}*\n\n"
            f"🗑️ Chiqindi turini kiriting:
"
            f"(masalan: Plastik idishlar, qog'oz, metall)"
        )
    else:
        text = (
            f"✅ Unternehmen ausgewählt: *{selected_company['name']}*\n\n"
            f"🗑️ Abfallart eingeben:
"
            f"(z.B.: Plastikflaschen, Papier, Metall)"
        )

    await query.edit_message_text(text, reply_markup=get_cancel_keyboard(language))
    return REPORT_WASTE_TYPE


async def report_waste_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Chiqindi turini qabul qilish.
    """
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    language = user_data.get("language", DEFAULT_LANGUAGE) if user_data else DEFAULT_LANGUAGE

    waste_type = update.message.text.strip()

    # Tekshirish
    valid, result = validate_waste_type(waste_type)
    if not valid:
        await update.message.reply_text(result, reply_markup=get_cancel_keyboard(language))
        return REPORT_WASTE_TYPE

    context.user_data["report_waste_type"] = result

    if language == "uz":
        text = "⚖️ Chiqindi miqdorini kiriting (kg):\n(masalan: 150.5)"
    else:
        text = "⚖️ Abfallmenge eingeben (kg):\n(z.B.: 150.5)"

    await update.message.reply_text(text, reply_markup=get_cancel_keyboard(language))
    return REPORT_QUANTITY


async def report_quantity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Miqdorni qabul qilish.
    """
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    language = user_data.get("language", DEFAULT_LANGUAGE) if user_data else DEFAULT_LANGUAGE

    quantity_str = update.message.text.strip()

    valid, result = validate_quantity(quantity_str)
    if not valid:
        await update.message.reply_text(result, reply_markup=get_cancel_keyboard(language))
        return REPORT_QUANTITY

    context.user_data["report_quantity"] = float(result)

    if language == "uz":
        text = "📅 Hisobot sanasini kiriting:
(masalan: 15.06.2026)"
    else:
        text = "📅 Berichtsdatum eingeben:
(z.B.: 15.06.2026)"

    await update.message.reply_text(text, reply_markup=get_cancel_keyboard(language))
    return REPORT_DATE


async def report_date_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sanani qabul qilish.
    """
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    language = user_data.get("language", DEFAULT_LANGUAGE) if user_data else DEFAULT_LANGUAGE

    date_str = update.message.text.strip()

    valid, result = validate_date(date_str)
    if not valid:
        await update.message.reply_text(result, reply_markup=get_cancel_keyboard(language))
        return REPORT_DATE

    context.user_data["report_date"] = result

    if language == "uz":
        text = "📝 Qo'shimcha tavsif (ixtiyoriy):\n(yoki "o'tkazib yuborish" deb yozing)"
    else:
        text = "📝 Zusätzliche Beschreibung (optional):\n(oder "überspringen" schreiben)"

    await update.message.reply_text(text, reply_markup=get_cancel_keyboard(language))
    return REPORT_DESCRIPTION


async def report_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Tavsifni qabul qilish va hisobotni yaratish.
    """
    user_id = update.effective_user.id
    user_data = get_user(user_id)
    language = user_data.get("language", DEFAULT_LANGUAGE) if user_data else DEFAULT_LANGUAGE

    desc_text = update.message.text.strip()

    if desc_text.lower() in ["o'tkazib yuborish", "überspringen", "skip", "-"]:
        context.user_data["report_description"] = None
    else:
        context.user_data["report_description"] = desc_text

    # Hisobot ma'lumotlarini yig'ish
    report_data = {
        "company": context.user_data.get("report_company", {}),
        "waste_type": context.user_data.get("report_waste_type", ""),
        "quantity": context.user_data.get("report_quantity", 0),
        "date": context.user_data.get("report_date", ""),
        "description": context.user_data.get("report_description"),
    }

    # AI hisobot matnini yaratish
    if language == "uz":
        await update.message.reply_text("🤖 *AI hisobot yaratilmoqda...*", parse_mode="Markdown")
    else:
        await update.message.reply_text("🤖 *KI-Bericht wird erstellt...*", parse_mode="Markdown")

    ai_text = generate_waste_report(
        language=language,
        company_name=report_data["company"].get("name", ""),
        company_address=report_data["company"].get("address", ""),
        waste_type=report_data["waste_type"],
        quantity=report_data["quantity"],
        report_date=report_data["date"],
        description=report_data["description"],
        director_name=report_data["company"].get("director_name")
    )

    if not ai_text:
        if language == "uz":
            text = "❌ *AI hisobot yaratishda xatolik.* Iltimos, keyinroq urinib ko'ring."
        else:
            text = "❌ *Fehler bei der KI-Berichterstellung.* Bitte später versuchen."

        await update.message.reply_text(text, reply_markup=get_main_menu_keyboard(language))
        return MENU

    # Word hujjatini yaratish
    if language == "uz":
        await update.message.reply_text("📄 *Word hujjat yaratilmoqda...*", parse_mode="Markdown")
    else:
        await update.message.reply_text("📄 *Word-Dokument wird erstellt...*", parse_mode="Markdown")

    doc_path = create_word_report(
        language=language,
        company_name=report_data["company"].get("name", ""),
        company_address=report_data["company"].get("address", ""),
        company_inn=report_data["company"].get("inn", ""),
        company_phone=report_data["company"].get("phone", ""),
        waste_type=report_data["waste_type"],
        quantity=report_data["quantity"],
        report_date=report_data["date"],
        ai_generated_text=ai_text,
        director_name=report_data["company"].get("director_name"),
        report_id=None
    )

    if doc_path and os.path.exists(doc_path):
        # Hisobotni bazaga saqlash
        report_id = add_waste_report(
            user_id=user_id,
            company_id=context.user_data.get("report_company_id"),
            waste_type=report_data["waste_type"],
            quantity=report_data["quantity"],
            report_date=report_data["date"],
            description=report_data["description"],
            ai_generated_text=ai_text,
            document_path=doc_path,
            language=language
        )

        # Faylni yuborish
        if language == "uz":
            caption = (
                f"✅ *Hisobot tayyor!*\n\n"
                f"🏢 Korxona: {report_data['company'].get('name')}\n"
                f"🗑️ Chiqindi: {report_data['waste_type']}\n"
                f"⚖️ Miqdor: {report_data['quantity']} kg\n"
                f"📅 Sana: {report_data['date']}"
            )
        else:
            caption = (
                f"✅ *Bericht fertig!*\n\n"
                f"🏢 Unternehmen: {report_data['company'].get('name')}\n"
                f"🗑️ Abfall: {report_data['waste_type']}\n"
                f"⚖️ Menge: {report_data['quantity']} kg\n"
                f"📅 Datum: {report_data['date']}"
            )

        with open(doc_path, "rb") as doc_file:
            await update.message.reply_document(
                document=doc_file,
                caption=caption,
                reply_markup=get_main_menu_keyboard(language),
                parse_mode="Markdown"
            )

        # Vaqtinchalik ma'lumotlarni tozalash
        context.user_data.pop("report_company_id", None)
        context.user_data.pop("report_company", None)
        context.user_data.pop("report_waste_type", None)
        context.user_data.pop("report_quantity", None)
        context.user_data.pop("report_date", None)
        context.user_data.pop("report_description", None)

    else:
        if language == "uz":
            text = "❌ *Hujjat yaratishda xatolik.*"
        else:
            text = "❌ *Fehler beim Erstellen des Dokuments.*"

        await update.message.reply_text(text, reply_markup=get_main_menu_keyboard(language))

    return MENU


# ==========================================
# MENING HISOBOTLARIM (My Reports)
# ==========================================

async def show_reports(query, user_id: int, language: str):
    """
    Foydalanuvchining hisobotlarini ko'rsatish.
    """
    reports = get_user_reports(user_id, limit=10)

    if not reports:
        if language == "uz":
            text = "📁 *Sizda hali hisobot yo'q.*\n\nHisobot yaratish uchun quyidagi tugmani bosing:"
        else:
            text = "📁 *Sie haben noch keine Berichte.*\n\nKlicken Sie zum Erstellen:"

        buttons = [
            [InlineKeyboardButton(
                "📋 Hisobot yaratish" if language == "uz" else "📋 Bericht erstellen",
                callback_data="create_report"
            )],
            [InlineKeyboardButton(
                "◀️ Orqaga" if language == "uz" else "◀️ Zurück",
                callback_data="back_menu"
            )]
        ]

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="Markdown"
        )
        return MENU

    if language == "uz":
        text = "📁 *So'nggi hisobotlar:*\n\n"
    else:
        text = "📁 *Neueste Berichte:*\n\n"

    for i, report in enumerate(reports, 1):
        company_name = report.get("company_name", "Noma'lum")
        text += (
            f"{i}. 🗑️ {report['waste_type']}\n"
            f"   ⚖️ {report['quantity']} kg | 📅 {report['report_date']}\n"
            f"   🏢 {company_name}\n\n"
        )

    await query.edit_message_text(
        text,
        reply_markup=get_main_menu_keyboard(language),
        parse_mode="Markdown"
    )
    return MENU


# ==========================================
# SOZLAMALAR (Settings)
# ==========================================

async def show_settings(query, language: str):
    """
    Sozlamalar menyuini ko'rsatish.
    """
    if language == "uz":
        text = "⚙️ *Sozlamalar:*"
        lang_btn = "🌍 Tilni o'zgartirish"
    else:
        text = "⚙️ *Einstellungen:*"
        lang_btn = "🌍 Sprache ändern"

    buttons = [
        [InlineKeyboardButton(lang_btn, callback_data="change_language")],
        [InlineKeyboardButton(
            "◀️ Orqaga" if language == "uz" else "◀️ Zurück",
            callback_data="back_menu"
        )]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )
    return MENU


# ==========================================
# YORDAM (Help)
# ==========================================

async def show_help(query, language: str):
    """
    Yordam ma'lumotlarini ko'rsatish.
    """
    if language == "uz":
        text = (
            "❓ *EcoDoc - Yordam*\n\n"
            "*Qanday foydalanish:*\n"
            "1️⃣ *Korxona qo'shish* - Yangi korxona ma'lumotlarini kiriting\n"
            "2️⃣ *Hisobot yaratish* - Chiqindi ma'lumotlarini kiriting, AI hisobot yozadi\n"
            "3️⃣ *Hisobotlarim* - Oldingi hisobotlarni ko'rish\n\n"
            "*Aloqa:* @sardor_username"
        )
    else:
        text = (
            "❓ *EcoDoc - Hilfe*\n\n"
            "*So verwenden Sie:*\n"
            "1️⃣ *Unternehmen hinzufügen* - Neue Unternehmensdaten eingeben\n"
            "2️⃣ *Bericht erstellen* - Abfalldaten eingeben, KI schreibt Bericht\n"
            "3️⃣ *Meine Berichte* - Frühere Berichte ansehen\n\n"
            "*Kontakt:* @sardor_username"
        )

    await query.edit_message_text(
        text,
        reply_markup=get_main_menu_keyboard(language),
        parse_mode="Markdown"
    )
    return MENU


# ==========================================
# BOTNI ISHGA TUSHIRISH
# ==========================================

def main():
    """
    Botni ishga tushirish.
    """
    print("🚀 EcoDoc bot ishga tushirilmoqda...")

    # Ma'lumotlar bazasini yaratish
    init_database()
    print("✅ Ma'lumotlar bazasi tayyor")

    # Bot ilovasini yaratish
    application = Application.builder().token(BOT_TOKEN).build()

    # Asosiy conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            LANGUAGE_SELECT: [
                CallbackQueryHandler(language_callback, pattern="^lang_")
            ],
            MENU: [
                CallbackQueryHandler(menu_callback, pattern="^(add_company|create_report|my_reports|settings|help|cancel|back_menu)$")
            ],
            # Korxona qo'shish holatlari
            COMPANY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, company_name_handler)],
            COMPANY_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, company_address_handler)],
            COMPANY_INN: [MessageHandler(filters.TEXT & ~filters.COMMAND, company_inn_handler)],
            COMPANY_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, company_phone_handler)],
            COMPANY_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, company_email_handler)],
            COMPANY_DIRECTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, company_director_handler)],
            COMPANY_CONFIRM: [
                CallbackQueryHandler(company_confirm_callback, pattern="^(confirm_company|edit_company)$")
            ],
            # Hisobot yaratish holatlari
            REPORT_SELECT_COMPANY: [
                CallbackQueryHandler(report_select_company_callback, pattern="^comp_\d+$")
            ],
            REPORT_WASTE_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, report_waste_type_handler)],
            REPORT_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, report_quantity_handler)],
            REPORT_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, report_date_handler)],
            REPORT_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, report_description_handler)],
        },
        fallbacks=[
            CommandHandler("start", start_command),
            CallbackQueryHandler(menu_callback, pattern="^cancel$")
        ],
        per_message=False
    )

    application.add_handler(conv_handler)

    print("✅ Bot sozlandi!")
    print("🤖 Bot ishlayapti...")

    # Botni ishga tushirish
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
