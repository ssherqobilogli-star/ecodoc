"""
EcoDoc - Ekologik chiqindi hujjatlarini avtomatlashtiruvchi bot
validators.py - Foydalanuvchi kiritgan ma'lumotlarni tekshirish

Bu modul quyidagilarni qiladi:
1. Telefon raqamni formatini tekshirish
2. INN/Steuernummer formatini tekshirish
3. Sana formatini tekshirish
4. Miqdor (son) formatini tekshirish
5. Email formatini tekshirish

Xatolarni oldini olish va professional foydalanuvchi tajribasi uchun muhim!
"""

import re
from datetime import datetime
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def validate_phone(phone: str, country: str = "uz") -> Tuple[bool, str]:
    """
    Telefon raqamini tekshirish.

    Args:
        phone: Telefon raqami matni
        country: Davlat kodi ('uz' yoki 'de')

    Returns:
        Tuple[bool, str]: (Muvaffaqiyatli?, xatolik xabari yoki tozalangan raqam)
    """
    try:
        # Barcha bo'sh joylarni olib tashlash
        phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        if country == "uz":
            # O'zbek telefon raqami: +998XXXXXXXXX
            pattern = r'^\+998[0-9]{9}$'
            if re.match(pattern, phone):
                return True, phone
            else:
                return False, "❌ Noto'g'ri format. To'g'ri format: +998 90 123 45 67"

        elif country == "de":
            # Nemis telefon raqami: +49 yoki 0 bilan boshlanadi
            if phone.startswith("0"):
                phone = "+49" + phone[1:]
            pattern = r'^\+49[0-9]{10,13}$'
            if re.match(pattern, phone):
                return True, phone
            else:
                return False, "❌ Falsches Format. Richtig: +49 170 1234567 oder 0170 1234567"

        else:
            return False, "❌ Noto'g'ri davlat kodi"

    except Exception as e:
        logger.error(f"❌ Telefon tekshirishda xatolik: {e}")
        return False, "❌ Xatolik yuz berdi"


def validate_inn(inn: str, country: str = "uz") -> Tuple[bool, str]:
    """
    INN (O'zbek) yoki Steuernummer (German) ni tekshirish.

    Args:
        inn: INN/Steuernummer raqami
        country: Davlat kodi

    Returns:
        Tuple[bool, str]: (Muvaffaqiyatli?, xatolik xabari yoki tozalangan raqam)
    """
    try:
        # Faqat raqamlarni qoldirish
        inn = re.sub(r'[^0-9]', '', inn)

        if country == "uz":
            # O'zbek INN: 9 ta raqam
            if len(inn) == 9 and inn.isdigit():
                return True, inn
            else:
                return False, "❌ INN 9 ta raqamdan iborat bo'lishi kerak (masalan: 123456789)"

        elif country == "de":
            # Nemis Steuernummer: 10-13 ta raqam
            if 10 <= len(inn) <= 13 and inn.isdigit():
                return True, inn
            else:
                return False, "❌ Steuernummer 10-13 Ziffern (z.B.: 1234567890)"

        else:
            return False, "❌ Noto'g'ri davlat kodi"

    except Exception as e:
        logger.error(f"❌ INN tekshirishda xatolik: {e}")
        return False, "❌ Xatolik yuz berdi"


def validate_date(date_str: str, format_str: str = "%d.%m.%Y") -> Tuple[bool, str]:
    """
    Sana formatini tekshirish.

    Args:
        date_str: Sana matni
        format_str: Kutilayotgan format (standart: DD.MM.YYYY)

    Returns:
        Tuple[bool, str]: (Muvaffaqiyatli?, xatolik xabari yoki tozalangan sana)
    """
    try:
        # Sana formatlarini tekshirish
        formats_to_try = [
            "%d.%m.%Y",  # 15.06.2026
            "%d/%m/%Y",  # 15/06/2026
            "%Y-%m-%d",  # 2026-06-15
            "%d-%m-%Y",  # 15-06-2026
        ]

        for fmt in formats_to_try:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                # Kelajakdagi sana emasligini tekshirish
                if parsed_date > datetime.now():
                    return False, "❌ Sana kelajakdan bo'lmasligi kerak"

                # Standart formatga o'tkazish
                return True, parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue

        return False, "❌ Noto'g'ri sana formati. To'g'ri format: 15.06.2026"

    except Exception as e:
        logger.error(f"❌ Sana tekshirishda xatolik: {e}")
        return False, "❌ Xatolik yuz berdi"


def validate_quantity(quantity_str: str) -> Tuple[bool, str]:
    """
    Chiqindi miqdorini tekshirish.

    Args:
        quantity_str: Miqdor matni

    Returns:
        Tuple[bool, str]: (Muvaffaqiyatli?, xatolik xabari yoki son qiymati)
    """
    try:
        # Vergulni nuqtaga almashtirish
        quantity_str = quantity_str.replace(",", ".").strip()

        # Son ekanligini tekshirish
        quantity = float(quantity_str)

        # Musbat son ekanligini tekshirish
        if quantity <= 0:
            return False, "❌ Miqdor 0 dan katta bo'lishi kerak"

        # Juda katta son ekanligini tekshirish (10 000 000 kg dan katta emas)
        if quantity > 10_000_000:
            return False, "❌ Miqdor juda katta. Iltimos, tekshiring"

        return True, str(quantity)

    except ValueError:
        return False, "❌ Noto'g'ri miqdor. Faqat raqam kiriting (masalan: 150.5)"
    except Exception as e:
        logger.error(f"❌ Miqdor tekshirishda xatolik: {e}")
        return False, "❌ Xatolik yuz berdi"


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Email formatini tekshirish.

    Args:
        email: Email manzili

    Returns:
        Tuple[bool, str]: (Muvaffaqiyatli?, xatolik xabari yoki tozalangan email)
    """
    try:
        email = email.strip().lower()

        # Email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if re.match(pattern, email):
            return True, email
        else:
            return False, "❌ Noto'g'ri email formati (masalan: info@korxona.uz)"

    except Exception as e:
        logger.error(f"❌ Email tekshirishda xatolik: {e}")
        return False, "❌ Xatolik yuz berdi"


def validate_company_name(name: str) -> Tuple[bool, str]:
    """
    Korxona nomini tekshirish.

    Args:
        name: Korxona nomi

    Returns:
        Tuple[bool, str]: (Muvaffaqiyatli?, xatolik xabari yoki tozalangan nom)
    """
    try:
        name = name.strip()

        if len(name) < 2:
            return False, "❌ Nomi juda qisqa (kamida 2 ta harf)"

        if len(name) > 200:
            return False, "❌ Nomi juda uzun (maksimum 200 ta harf)"

        # Maxsus belgilarni tekshirish
        if re.search(r'[<>{}\[\]]', name):
            return False, "❌ Nomi taqiqlangan belgilarni o'z ichiga olmasligi kerak"

        return True, name

    except Exception as e:
        logger.error(f"❌ Korxona nomi tekshirishda xatolik: {e}")
        return False, "❌ Xatolik yuz berdi"


def validate_waste_type(waste_type: str) -> Tuple[bool, str]:
    """
    Chiqindi turini tekshirish.

    Args:
        waste_type: Chiqindi turi

    Returns:
        Tuple[bool, str]: (Muvaffaqiyatli?, xatolik xabari yoki tozalangan matn)
    """
    try:
        waste_type = waste_type.strip()

        if len(waste_type) < 3:
            return False, "❌ Chiqindi turi juda qisqa (kamida 3 ta harf)"

        if len(waste_type) > 300:
            return False, "❌ Chiqindi turi juda uzun"

        return True, waste_type

    except Exception as e:
        logger.error(f"❌ Chiqindi turi tekshirishda xatolik: {e}")
        return False, "❌ Xatolik yuz berdi"


def validate_director_name(name: str) -> Tuple[bool, str]:
    """
    Direktor ismini tekshirish.

    Args:
        name: F.I.O.

    Returns:
        Tuple[bool, str]: (Muvaffaqiyatli?, xatolik xabari yoki tozalangan matn)
    """
    try:
        name = name.strip()

        if len(name) < 5:
            return False, "❌ Ism juda qisqa (kamida 5 ta harf, masalan: Alijon Valiyev)"

        if len(name) > 100:
            return False, "❌ Ism juda uzun"

        # Kamida 2 ta so'z bo'lishi kerak (ism va familiya)
        words = name.split()
        if len(words) < 2:
            return False, "❌ Iltimos, to'liq F.I.O. kiriting (ism va familiya)"

        return True, name

    except Exception as e:
        logger.error(f"❌ Direktor ismi tekshirishda xatolik: {e}")
        return False, "❌ Xatolik yuz berdi"


# Barcha tekshiruvlarni birlashtiruvchi funksiya
def validate_all_company_data(
    name: str,
    address: str,
    inn: str,
    phone: str,
    email: str = None,
    director_name: str = None,
    country: str = "uz"
) -> dict:
    """
    Barcha korxona ma'lumotlarini birdaniga tekshirish.

    Args:
        name: Korxona nomi
        address: Manzil
        inn: INN/Steuernummer
        phone: Telefon
        email: Email (ixtiyoriy)
        director_name: Direktor ismi (ixtiyoriy)
        country: Davlat kodi

    Returns:
        dict: Tekshiruv natijalari
    """
    results = {
        "is_valid": True,
        "errors": {},
        "data": {}
    }

    # Korxona nomi
    valid, value = validate_company_name(name)
    if valid:
        results["data"]["name"] = value
    else:
        results["is_valid"] = False
        results["errors"]["name"] = value

    # Manzil (oddiy tekshirish)
    address = address.strip()
    if len(address) < 5:
        results["is_valid"] = False
        results["errors"]["address"] = "❌ Manzil juda qisqa"
    else:
        results["data"]["address"] = address

    # INN
    valid, value = validate_inn(inn, country)
    if valid:
        results["data"]["inn"] = value
    else:
        results["is_valid"] = False
        results["errors"]["inn"] = value

    # Telefon
    valid, value = validate_phone(phone, country)
    if valid:
        results["data"]["phone"] = value
    else:
        results["is_valid"] = False
        results["errors"]["phone"] = value

    # Email (agar kiritilgan bo'lsa)
    if email:
        valid, value = validate_email(email)
        if valid:
            results["data"]["email"] = value
        else:
            results["is_valid"] = False
            results["errors"]["email"] = value

    # Direktor ismi (agar kiritilgan bo'lsa)
    if director_name:
        valid, value = validate_director_name(director_name)
        if valid:
            results["data"]["director_name"] = value
        else:
            results["is_valid"] = False
            results["errors"]["director_name"] = value

    return results


# Test uchun
if __name__ == "__main__":
    print("🧪 Validatsiya testlari...")

    # Telefon testi
    print("\n📱 Telefon tekshirish:")
    print(validate_phone("+998 90 123 45 67", "uz"))
    print(validate_phone("+49 170 1234567", "de"))
    print(validate_phone("12345", "uz"))  # Xato

    # INN testi
    print("\n🏢 INN tekshirish:")
    print(validate_inn("123456789", "uz"))
    print(validate_inn("1234567890", "de"))

    # Sana testi
    print("\n📅 Sana tekshirish:")
    print(validate_date("15.06.2026"))
    print(validate_date("2026-06-15"))

    # Miqdor testi
    print("\n⚖️ Miqdor tekshirish:")
    print(validate_quantity("150.5"))
    print(validate_quantity("-10"))  # Xato

    print("\n✅ Testlar tugadi!")
