"""
EcoDoc - Ekologik chiqindi hujjatlarini avtomatlashtiruvchi bot
database.py - SQLite ma'lumotlar bazasi bilan ishlash

Jadvallar:
- users: Foydalanuvchilar ma'lumotlari
- companies: Korxonalar ma'lumotlari
- waste_reports: Chiqindi hisobotlari
- templates: Hisobot shablonlari
"""

import sqlite3
import os
from datetime import datetime
from config import DATABASE_PATH, LOG_LEVEL
import logging

# Logging sozlash
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_connection():
    """
    SQLite bazasiga ulanish yaratish.
    Agar papka mavjud bo'lmasa, avval yaratadi.

    Returns:
        sqlite3.Connection: Bazaga ulanish obyekti
    """
    try:
        # Ma'lumotlar bazasi papkasini yaratish
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Natijalarni lug'at sifatida qaytarish
        logger.info("✅ Ma'lumotlar bazasiga ulanish muvaffaqiyatli")
        return conn
    except sqlite3.Error as e:
        logger.error(f"❌ Bazaga ulanishda xatolik: {e}")
        raise


def init_database():
    """
    Barcha jadvallarni yaratish.
    Birinchi marta ishga tushirilganda chaqiriladi.

    Jadvallar:
        users: Foydalanuvchilar (Telegram ID, til, ro'yxatdan o'tgan sana)
        companies: Korxonalar (nomi, manzil, INN, telefon)
        waste_reports: Chiqindi hisobotlari (turi, miqdor, sana, fayl yo'li)
        templates: Hisobot shablonlari (nomi, tili, yo'li)
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # 1. Foydalanuvchilar jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language TEXT DEFAULT 'uz',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("✅ 'users' jadvali yaratildi/yangilandi")

        # 2. Korxonalar jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                address TEXT,
                inn TEXT,
                phone TEXT,
                email TEXT,
                director_name TEXT,
                country TEXT DEFAULT 'uz',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(telegram_id)
            )
        """)
        logger.info("✅ 'companies' jadvali yaratildi/yangilandi")

        # 3. Chiqindi hisobotlari jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS waste_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                company_id INTEGER,
                waste_type TEXT NOT NULL,
                waste_category TEXT,
                quantity REAL NOT NULL,
                unit TEXT DEFAULT 'kg',
                report_date DATE NOT NULL,
                description TEXT,
                ai_generated_text TEXT,
                document_path TEXT,
                language TEXT DEFAULT 'uz',
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(telegram_id),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)
        logger.info("✅ 'waste_reports' jadvali yaratildi/yangilandi")

        # 4. Hisobot shablonlari jadvali
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                language TEXT NOT NULL,
                file_path TEXT NOT NULL,
                description TEXT,
                is_default INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("✅ 'templates' jadvali yaratildi/yangilandi")

        conn.commit()
        logger.info("🎉 Barcha jadvallar muvaffaqiyatli yaratildi!")

    except sqlite3.Error as e:
        logger.error(f"❌ Jadvallarni yaratishda xatolik: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def add_user(telegram_id: int, username: str = None, 
             first_name: str = None, last_name: str = None,
             language: str = "uz") -> bool:
    """
    Yangi foydalanuvchini qo'shish yoki mavjudini yangilash.

    Args:
        telegram_id: Telegram foydalanuvchi IDsi
        username: Telegram username (@username)
        first_name: Ism
        last_name: Familiya
        language: Til kodi (uz/de)

    Returns:
        bool: Muvaffaqiyatli bo'lsa True
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Avval foydalanuvchi mavjudligini tekshirish
        cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
        existing = cursor.fetchone()

        if existing:
            # Mavjud foydalanuvchini yangilash
            cursor.execute("""
                UPDATE users 
                SET username = ?, first_name = ?, last_name = ?, 
                    language = ?, last_active = CURRENT_TIMESTAMP
                WHERE telegram_id = ?
            """, (username, first_name, last_name, language, telegram_id))
            logger.info(f"🔄 Foydalanuvchi yangilandi: {telegram_id}")
        else:
            # Yangi foydalanuvchi qo'shish
            cursor.execute("""
                INSERT INTO users (telegram_id, username, first_name, last_name, language)
                VALUES (?, ?, ?, ?, ?)
            """, (telegram_id, username, first_name, last_name, language))
            logger.info(f"➕ Yangi foydalanuvchi qo'shildi: {telegram_id}")

        conn.commit()
        return True

    except sqlite3.Error as e:
        logger.error(f"❌ Foydalanuvchi qo'shishda xatolik: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_user(telegram_id: int) -> dict:
    """
    Foydalanuvchi ma'lumotlarini olish.

    Args:
        telegram_id: Telegram foydalanuvchi IDsi

    Returns:
        dict: Foydalanuvchi ma'lumotlari yoki None
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None

    except sqlite3.Error as e:
        logger.error(f"❌ Foydalanuvchini olishda xatolik: {e}")
        return None
    finally:
        conn.close()


def add_company(user_id: int, name: str, address: str = None,
                inn: str = None, phone: str = None,
                email: str = None, director_name: str = None,
                country: str = "uz") -> int:
    """
    Yangi korxona qo'shish.

    Args:
        user_id: Foydalanuvchi Telegram IDsi
        name: Korxona nomi
        address: Manzil
        inn: INN (O'zbek) yoki Steuernummer (German)
        phone: Telefon
        email: Email
        director_name: Direktor FIO
        country: Davlat kodi

    Returns:
        int: Yangi korxona IDsi yoki -1 (xatolik)
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO companies (user_id, name, address, inn, phone, email, director_name, country)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, address, inn, phone, email, director_name, country))

        conn.commit()
        company_id = cursor.lastrowid
        logger.info(f"➕ Yangi korxona qo'shildi: {name} (ID: {company_id})")
        return company_id

    except sqlite3.Error as e:
        logger.error(f"❌ Korxona qo'shishda xatolik: {e}")
        conn.rollback()
        return -1
    finally:
        conn.close()


def get_user_companies(user_id: int) -> list:
    """
    Foydalanuvchining barcha korxonalari ro'yxatini olish.

    Args:
        user_id: Foydalanuvchi Telegram IDsi

    Returns:
        list: Korxonalar ro'yxati
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT * FROM companies 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (user_id,))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    except sqlite3.Error as e:
        logger.error(f"❌ Korxonalar ro'yxatini olishda xatolik: {e}")
        return []
    finally:
        conn.close()


def add_waste_report(user_id: int, company_id: int, waste_type: str,
                     quantity: float, report_date: str,
                     waste_category: str = None, description: str = None,
                     ai_generated_text: str = None, document_path: str = None,
                     language: str = "uz") -> int:
    """
    Chiqindi hisobotini qo'shish.

    Args:
        user_id: Foydalanuvchi IDsi
        company_id: Korxona IDsi
        waste_type: Chiqindi turi
        quantity: Miqdori
        report_date: Hisobot sanasi (YYYY-MM-DD)
        waste_category: Chiqindi kategoriyasi
        description: Tavsif
        ai_generated_text: AI yaratgan matn
        document_path: Hujjat fayli yo'li
        language: Til kodi

    Returns:
        int: Hisobot IDsi yoki -1
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO waste_reports 
            (user_id, company_id, waste_type, waste_category, quantity, 
             report_date, description, ai_generated_text, document_path, language)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, company_id, waste_type, waste_category, quantity,
              report_date, description, ai_generated_text, document_path, language))

        conn.commit()
        report_id = cursor.lastrowid
        logger.info(f"➕ Yangi hisobot qo'shildi: ID {report_id}")
        return report_id

    except sqlite3.Error as e:
        logger.error(f"❌ Hisobot qo'shishda xatolik: {e}")
        conn.rollback()
        return -1
    finally:
        conn.close()


def get_user_reports(user_id: int, limit: int = 10) -> list:
    """
    Foydalanuvchining hisobotlarini olish.

    Args:
        user_id: Foydalanuvchi IDsi
        limit: Maksimal qaytariladigan yozuvlar soni

    Returns:
        list: Hisobotlar ro'yxati
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT r.*, c.name as company_name
            FROM waste_reports r
            LEFT JOIN companies c ON r.company_id = c.id
            WHERE r.user_id = ?
            ORDER BY r.created_at DESC
            LIMIT ?
        """, (user_id, limit))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    except sqlite3.Error as e:
        logger.error(f"❌ Hisobotlarni olishda xatolik: {e}")
        return []
    finally:
        conn.close()


# Agar bu fayl to'g'ridan-to'g'ri ishga tushirilsa, bazani yaratish
if __name__ == "__main__":
    print("🚀 EcoDoc ma'lumotlar bazasi yaratilmoqda...")
    init_database()
    print("✅ Tayyor!")
