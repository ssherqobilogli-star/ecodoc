# 🌱 EcoDoc — KI-gestützter Abfalldokumentations-Bot

> **Automatisierte Abfalldokumentation per Telegram — auf Deutsch 🇩🇪 und Usbekisch 🇺🇿**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram)](https://t.me)
[![Groq AI](https://img.shields.io/badge/Groq-LLaMA%203.3%2070B-orange)](https://groq.com)
[![Railway](https://img.shields.io/badge/Deploy-Railway-black?logo=railway)](https://railway.app)
[![License](https://img.shields.io/badge/Lizenz-MIT-green)](LICENSE)

---

## 📋 Projektbeschreibung

**EcoDoc** ist ein Telegram-Bot, der Unternehmen bei der Erstellung offizieller **Abfalldokumentation** unterstützt. Mithilfe von Künstlicher Intelligenz (Groq LLaMA 3.3 70B) werden professionelle Abfallnachweise automatisch generiert und als Word-Dokument (`.docx`) bereitgestellt.

Das Projekt wurde im Rahmen der Ausbildung im Bereich **Kreislaufwirtschaft** entwickelt und richtet sich sowohl an den deutschen als auch an den usbekischen Markt.

---

## ⚙️ Funktionen

| Funktion | Beschreibung |
|---|---|
| 🤖 **KI-Berichterstellung** | LLaMA 3.3 (70B) generiert professionelle Abfallnachweise |
| 🏢 **Unternehmensverwaltung** | Betriebsdaten speichern und wiederverwenden |
| 📄 **Word-Export** | Automatisch formatierte `.docx`-Dokumente |
| 🌍 **Zweisprachig** | Vollständig auf Deutsch 🇩🇪 und Usbekisch 🇺🇿 |
| 📁 **Berichtsarchiv** | Alle erstellten Dokumente jederzeit abrufbar |
| ✅ **Validierung** | Eingabeprüfung für Telefon, Steuernummer, Datum, Menge |

---

## 🏗️ Technischer Aufbau

```
ecodoc/
├── bot.py              → Telegram ConversationHandler (18 Zustände)
├── ai_generator.py     → Groq API → KI-Berichtstext
├── report.py           → python-docx → .docx Dokument
├── database.py         → SQLite (users, companies, waste_reports)
├── validators.py       → Eingabevalidierung
├── config.py           → Konfiguration (DE_CONFIG, UZ_CONFIG)
├── requirements.txt    → Python-Abhängigkeiten
├── Dockerfile          → Railway Deployment
└── .env.example        → API-Schlüssel Vorlage
```

---

## 🇩🇪 Rechtliche Grundlage (Deutschland)

- **Kreislaufwirtschaftsgesetz (KrWG)**
- **Abfallverzeichnis-Verordnung (AVV)**
- **Verpackungsgesetz (VerpackG)**
- **Elektro- und Elektronikgerätegesetz (ElektroG)**
- **Batteriegesetz (BattG)**

---

## 📦 Tech Stack

| Technologie | Version | Zweck |
|---|---|---|
| Python | 3.11 | Hauptsprache |
| python-telegram-bot | 20.7 | Telegram Bot Framework |
| Groq API (LLaMA 3.3 70B) | — | KI-Textgenerierung |
| python-docx | 1.1.2 | Word-Dokumenterstellung |
| SQLite | — | Lokale Datenbank |
| Railway | — | Cloud-Hosting |

---

## 🚀 Installation & Deployment

### Lokale Einrichtung

```bash
# 1. Repository klonen
git clone https://github.com/ssherqobilogli-star/ecodoc.git
cd ecodoc

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Umgebungsvariablen einrichten
cp .env.example .env
# .env öffnen und BOT_TOKEN + GROQ_API_KEY eintragen

# 4. Bot starten
python bot.py
```

### Railway Deployment

1. Dieses Repository auf GitHub pushen
2. [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Umgebungsvariablen setzen:

```
BOT_TOKEN=dein_telegram_bot_token
GROQ_API_KEY=dein_groq_api_key
```

4. Deploy — fertig ✅

---

---

# 🌱 EcoDoc — AI yordamida chiqindi hujjatlarini avtomatlashtiruvchi bot

> **Telegram orqali professional ekologik hisobotlarni avtomatik yaratish — Nemischa 🇩🇪 va O'zbekcha 🇺🇿**

---

## 📋 Loyiha haqida

**EcoDoc** — korxonalarga rasmiy **chiqindi hujjatlarini** tuzishda yordam beruvchi Telegram bot. Sun'iy intellekt (Groq LLaMA 3.3 70B) yordamida professional hisobot matni avtomatik yaratiladi va Word (`.docx`) formatida taqdim etiladi.

Loyiha Germaniyada **Kreislaufwirtschaft** (qayta ishlash iqtisodiyoti) sohasidagi Ausbildung portfolio sifatida ishlab chiqilgan bo'lib, Germaniya va O'zbekiston bozorlarini qamrab oladi.

---

## ⚙️ Imkoniyatlar

| Xususiyat | Tavsif |
|---|---|
| 🤖 **AI hisobot** | LLaMA 3.3 (70B) professional Abfalldokumentation matnini yozadi |
| 🏢 **Korxona boshqaruvi** | Ma'lumotlarni saqlash va qayta ishlatish |
| 📄 **Word eksport** | Avtomatik formatlangan `.docx` hujjat |
| 🌍 **Ikki tilli** | To'liq Nemischa 🇩🇪 va O'zbekcha 🇺🇿 |
| 📁 **Arxiv** | Barcha yaratilgan hisobotlar saqlanadi |
| ✅ **Tekshiruv** | Telefon, INN, sana, miqdor validatsiyasi |

---

## 🏗️ Texnik arxitektura

```
ecodoc/
├── bot.py              → Telegram ConversationHandler (18 holat)
├── ai_generator.py     → Groq API → hisobot matni
├── report.py           → python-docx → .docx hujjat
├── database.py         → SQLite (foydalanuvchilar, korxonalar, hisobotlar)
├── validators.py       → Ma'lumotlarni tekshirish
├── config.py           → Sozlamalar (DE_CONFIG, UZ_CONFIG)
├── requirements.txt    → Python kutubxonalari
├── Dockerfile          → Railway deployment
└── .env.example        → API kalitlar namunasi
```

---

## 🇺🇿 Qonuniy asos (O'zbekiston)

- O'zbekiston Respublikasi **Ekologiya kodeksi**
- **Chiqindilarni boshqarish** to'g'risidagi qonun (2019)
- **Atrof-muhitni muhofaza qilish** qoidalari
- Sanoat **ekologik monitoring** talablari

---

## 🚀 O'rnatish va ishga tushirish

```bash
# 1. Repozitoriyni klonlash
git clone https://github.com/ssherqobilogli-star/ecodoc.git
cd ecodoc

# 2. Kutubxonalarni o'rnatish
pip install -r requirements.txt

# 3. Muhit o'zgaruvchilarini sozlash
cp .env.example .env
# .env faylini oching: BOT_TOKEN va GROQ_API_KEY ni kiriting

# 4. Botni ishga tushirish
python bot.py
```

### Railway orqali deploy

1. Reponi GitHub'ga push qiling
2. [railway.app](https://railway.app) → New Project → Deploy from GitHub repo tanlang
3. Environment Variables qo'shing:

```
BOT_TOKEN=telegram_bot_tokeningiz
GROQ_API_KEY=groq_api_kalitingiz
```

4. Deploy — tayyor ✅

---

## 👤 Muallif

**Sardor Sherqobilogli** — [@ssherqobilogli-star](https://github.com/ssherqobilogli-star)

Ausbildung portfolio · Kreislaufwirtschaft · Abfalldokumentation · KI · 2026

---

*EcoDoc — ekologik kelajak uchun raqamli yechim 🌍*
