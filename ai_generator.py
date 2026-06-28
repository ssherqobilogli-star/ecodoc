"""
EcoDoc - Ekologik chiqindi hujjatlarini avtomatlashtiruvchi bot
ai_generator.py - Groq API orqali professional hisobot matni yaratish

Bu modul quyidagilarni qiladi:
1. Chiqindi ma'lumotlarini qabul qiladi
2. Groq API (llama-3.3-70b) orqali professional matn yaratadi
3. O'zbek va nemis tillarida hisobot tayyorlaydi

Ausbildung uchun muhim: Nemis tilida professional terminologiya ishlatiladi
"""

import os
import requests
import json
from typing import Dict, Optional
from config import GROQ_API_KEY, GROQ_MODEL, UZ_CONFIG, DE_CONFIG
import logging

logger = logging.getLogger(__name__)


def generate_waste_report(
    language: str,
    company_name: str,
    company_address: str,
    waste_type: str,
    quantity: float,
    report_date: str,
    waste_category: str = None,
    description: str = None,
    director_name: str = None
) -> Optional[str]:
    """
    AI yordamida professional chiqindi hisobot matni yaratish.

    Args:
        language: Til kodi ('uz' yoki 'de')
        company_name: Korxona nomi
        company_address: Korxona manzili
        waste_type: Chiqindi turi
        quantity: Miqdori (kg)
        report_date: Hisobot sanasi
        waste_category: Chiqindi kategoriyasi (nemis versiya uchun)
        description: Qo'shimcha tavsif
        director_name: Direktor ismi

    Returns:
        str: AI yaratgan hisobot matni yoki None (xatolik)
    """

    try:
        # Tilga qarab prompt tayyorlash
        if language == "uz":
            prompt = _create_uzbek_prompt(
                company_name, company_address, waste_type,
                quantity, report_date, description, director_name
            )
        elif language == "de":
            prompt = _create_german_prompt(
                company_name, company_address, waste_type,
                quantity, report_date, waste_category, description, director_name
            )
        else:
            logger.error(f"❌ Noto'g'ri til kodi: {language}")
            return None

        # Groq API ga so'rov yuborish
        response = _call_groq_api(prompt)

        if response:
            logger.info(f"✅ AI hisobot muvaffaqiyatli yaratildi ({language})")
            return response
        else:
            return None

    except Exception as e:
        logger.error(f"❌ AI hisobot yaratishda xatolik: {e}")
        return None


def _create_uzbek_prompt(
    company_name: str,
    company_address: str,
    waste_type: str,
    quantity: float,
    report_date: str,
    description: str = None,
    director_name: str = None
) -> str:
    """
    O'zbek tilida AI prompt yaratish.

    Returns:
        str: Groq API uchun prompt matni
    """

    prompt = f"""Siz professional ekologik hisobot mutaxassisisiz. 
Quyidagi ma'lumotlar asosida O'zbekiston qonunlariga mos, rasmiy chiqindi hisobotini yozing.

HISOBOT MA'LUMOTLARI:
- Korxona nomi: {company_name}
- Manzil: {company_address}
- Chiqindi turi: {waste_type}
- Miqdori: {quantity} kg
- Sana: {report_date}
- Mas'ul shaxs: {director_name or 'Aniqlanmagan'}
"""

    if description:
        prompt += f"- Qo'shimcha ma'lumot: {description}"

    prompt += """

TALABLAR:
1. Rasmiy, professional uslubda yozing
2. O'zbekiston ekologiya qonunlariga mos kelishi kerak
3. Quyidagi bo'limlarni o'z ichiga olsin:
   - KIRISH (hisobot maqsadi)
   - KORXONA HAQIDA MA'LUMOT
   - CHIQINDI TAVSIFI
   - MIQDOR VA O'LCHOV BIRLIGI
   - SAQLASH VA UTILIZATSIYA USULLARI
   - XULOSA VA TAVSIYALAR
4. Har bir bo'lim aniq va tushunarli bo'lsin
5. Umumiy hajmi 300-500 so'z
6. Faqat hisobot matnini yozing, boshqa izohlar bermang
"""

    return prompt


def _create_german_prompt(
    company_name: str,
    company_address: str,
    waste_type: str,
    quantity: float,
    report_date: str,
    waste_category: str = None,
    description: str = None,
    director_name: str = None
) -> str:
    """
    Nemis tilida AI prompt yaratish.
    Kreislaufwirtschaft (qayta ishlash) sohasi uchun professional terminologiya.

    Returns:
        str: Groq API uchun prompt matni (Deutsch)
    """

    prompt = f"""Sie sind ein professioneller Experte für Abfallwirtschaft und Kreislaufwirtschaft in Deutschland.
Erstellen Sie einen offiziellen Abfallnachweis basierend auf den folgenden Daten.

ABFALLNACHWEIS DATEN:
- Betrieb/Unternehmen: {company_name}
- Adresse: {company_address}
- Abfallart: {waste_type}
- Abfallkategorie: {waste_category or 'Nicht spezifiziert'}
- Menge: {quantity} kg
- Datum: {report_date}
- Verantwortliche Person: {director_name or 'Nicht angegeben'}
"""

    if description:
        prompt += f"- Zusätzliche Informationen: {description}"

    prompt += """

ANFORDERUNGEN:
1. Schreiben Sie in professionellem, offiziellem Stil
2. Beachten Sie das Kreislaufwirtschaftsgesetz (KrWG)
3. Verwenden Sie korrekte Fachbegriffe der Abfallwirtschaft
4. Die Dokumentation muss folgende Abschnitte enthalten:
   - EINLEITUNG (Zweck der Dokumentation)
   - UNTERNEHMENSBESCHREIBUNG
   - ABfallbeschreibung UND EIGENSCHAFTEN
   - MENGE UND MESSEINHEIT
   - LAGERUNG UND VERWERTUNG/ENTSORGUNG
   - NACHWEIS UND DOKUMENTATION
   - SCHLUSSFOLGERUNG UND EMPFEHLUNGEN
5. Jedes Kapitel muss präzise und verständlich sein
6. Gesamtlänge: 300-500 Wörter
7. Schreiben Sie NUR den Berichtstext, keine zusätzlichen Kommentare
8. Verwenden Sie die korrekten deutschen Fachbegriffe:
   - Abfallverzeichnis (AVV)
   - Verwertung (Recycling)
   - Entsorgung (Disposal)
   - Nachweispflicht (Documentation obligation)
   - Gefährliche Abfälle (Hazardous waste)
"""

    return prompt


def _call_groq_api(prompt: str) -> Optional[str]:
    """
    Groq API ga so'rov yuborish va javob olish.

    Args:
        prompt: AI uchun tayyorlangan prompt matni

    Returns:
        str: AI javobi yoki None
    """

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "Siz professional ekologik hisobot mutaxassisisiz. Faqat so'ralgan hisobotni yozing."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # Aniqroq javoblar uchun past harorat
            "max_tokens": 2000   # Yetarli uzunlik
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            ai_text = result["choices"][0]["message"]["content"]
            logger.info("✅ Groq API muvaffaqiyatli javob berdi")
            return ai_text
        else:
            logger.error(f"❌ Groq API xatolik: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Groq API so'rovida xatolik: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Groq API umumiy xatolik: {e}")
        return None


def generate_waste_summary(reports: list, language: str = "uz") -> Optional[str]:
    """
    Bir necha hisobotlar asosida umumiy xulosa yaratish.

    Args:
        reports: Hisobotlar ro'yxati
        language: Til kodi

    Returns:
        str: Umumiy xulosa matni
    """

    try:
        if language == "uz":
            prompt = f"""Quyidagi chiqindi hisobotlari asosida umumiy xulosa va tahlil yozing:

"""
            for i, report in enumerate(reports, 1):
                prompt += f"{i}. {report['waste_type']} - {report['quantity']} kg ({report['report_date']})"

            prompt += """
TALABLAR:
- Umumiy chiqindi hajmini hisoblang
- Eng ko'p chiqindi turini aniqlang
- Qayta ishlash tavsiyalarini bering
- 150-200 so'z
"""
        else:
            prompt = f"""Erstellen Sie eine Zusammenfassung basierend auf folgenden Abfallberichten:

"""
            for i, report in enumerate(reports, 1):
                prompt += f"{i}. {report['waste_type']} - {report['quantity']} kg ({report['report_date']})"

            prompt += """
ANFORDERUNGEN:
- Gesamtabfallmenge berechnen
- Häufigste Abfallart identifizieren
- Recycling-Empfehlungen geben
- 150-200 Wörter
"""

        return _call_groq_api(prompt)

    except Exception as e:
        logger.error(f"❌ Xulosa yaratishda xatolik: {e}")
        return None


# Test uchun
if __name__ == "__main__":
    print("🧪 AI generator testi...")

    # O'zbek testi
    result_uz = generate_waste_report(
        language="uz",
        company_name="Test Korxona",
        company_address="Toshkent, O'zbekiston",
        waste_type="Plastik idishlar",
        quantity=150.5,
        report_date="15.06.2026",
        director_name="Test Testov"
    )

    if result_uz:
        print("✅ O'zbek hisobot muvaffaqiyatli yaratildi!")
        print(result_uz[:200] + "...")
    else:
        print("❌ O'zbek hisobot yaratilmadi (API kalitini tekshiring)")
