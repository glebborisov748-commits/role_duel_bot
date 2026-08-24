import asyncio
import os
import json
import logging
import random
import re
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from dotenv import load_dotenv
from openai import OpenAI

# ============================================================
#  ГОЛОСОВЫЕ ОТКЛЮЧЕНЫ
# ============================================================
VOICE_ENABLED = False

# ============================================================
#  МНОГОЯЗЫЧНЫЙ СЛОВАРЬ (ВСЕ ЯЗЫКИ + СОГЛАШЕНИЕ)
# ============================================================
TEXTS = {
    "ru": {
        "main_menu": "📋 Главное меню",
        "my_profile": "👤 Мой профиль",
        "spin_wheel": "🎰 Колесо фортуны",
        "our_channel": "📢 Наш канал",
        "edit": "✏️ Редактировать",
        "change_character": "🔄 Сменить персонажа",
        "invite_friend": "👥 Пригласить друга",
        "create_character": "🎭 Создать своего персонажа",
        "buy_packs": "📦 Купить пакеты",
        "subscribe": "👑 Оформить подписку",
        "buy_sex_scene": "🔥 Купить интим-сцену (45⭐)",
        "back": "🔙 Главное меню",
        "back_to_profile": "🔙 Назад",
        "accept": "✅ Мне есть 18 лет",
        "decline": "❌ Мне нет 18 лет",
        "agree": "📄 Я принимаю условия",
        "disagree": "❌ Я не принимаю",
        "realism": "🌍 Реализм",
        "anime": "🎌 Аниме",
        "i_male": "👨 Я парень",
        "i_female": "👩 Я девушка",
        "scene_phone": "📱 Переписка в телефоне",
        "scene_live": "👫 Реальная встреча",
        "channel": "📢 Перейти в канал",
        "free": "🎁 Бесплатно",
        "tomorrow": "⏳ Завтра",
        "spin_paid": "💎 Крутить за 20⭐",
        "spin_more": "💎 Крутить ещё за 20⭐",
        "welcome": "👋 Добро пожаловать!",
        "age_confirm": "🔞 **ВНИМАНИЕ!**\nЭтот бот предназначен для лиц старше 18 лет.\nПодтверди свой возраст:",
        "age_ok": "✅ Возраст подтверждён.",
        "age_no": "🚫 Доступ запрещён. Бот только для 18+.",
        "agreement_ok": "✅ Соглашение принято! Теперь выбери мир:",
        "agreement_no": "❌ Без соглашения бот не работает.",
        "choose_gender": "👤 Выбери свой пол:",
        "choose_world": "🌍 Выбери мир:",
        "choose_style": "🎨 Выбери стиль:",
        "choose_scene": "🎬 Выбери сцену:",
        "no_messages": "😔 Закончились сообщения. Купи пакет или подписку.",
        "no_history": "❌ Нет сообщений для редактирования.",
        "edit_cancel": "❌ Редактирование отменено.",
        "edit_success": "✅ Сообщение заменено. Генерирую новый ответ...",
        "character_created": "✅ **Персонаж создан!**\n\nТеперь ты общаешься с:\n_{text}_",
        "character_reset": "✅ Персонаж сброшен.",
        "character_create_prompt": "🎭 **Создай своего уникального персонажа!**\n\nОпиши любого персонажа — из аниме, фильмов, игр или придумай своего.\nНапиши его/её имя, характер, внешность, откуда он/она, любые детали.\n\n📝 *Пример:*\n«Эльфийка из мира Ведьмака — мудрая, сдержанная, с длинными серебряными волосами. Любит звёзды и долгие разговоры у костра. Живёт одна в лесу.»\n\n✏️ Напиши описание прямо сейчас — и я запомню его!",
        "spin_reminder": "🎁 Привет! У тебя сегодня бесплатное вращение в Колесе фортуны! Зайди и попробуй удачу 🍀",
        "spin_choice": "🎰 **Колесо фортуны**\n\n{free_text}\n💎 Платное — 20⭐\n\n🔥 Призы: сообщения, XP, интим-сцены, PRO на 5 дней, SUPER PRO на 3 дня!",
        "spin_result": "🎰 **Результат!**\n\nТы выиграл: {prize}\n{free_text}\n\n{extra_text}",
        "spin_nothing": "😢 Ничего... В следующий раз повезёт!",
        "profile": "Подписка: {status}\nОсталось сообщений: {messages}",
        "referral": "👥 Твоя ссылка: `{link}`\n\nЗа каждого друга +10 сообщений и +1 интим-сцена!",
        "surprise_no_sub": "❌ Эта команда доступна только для подписчиков.",
        "surprise_low_level": "💕 Вы ещё не достаточно близки для сюрпризов. Продолжайте общаться!",
        "choose_lang": "🌍 Выбери язык:",
        "welcome_back_female": "Ой, тебя так долго не было! Я уже успела соскучиться 🥺💕",
        "welcome_back_male": "Ой, тебя так долго не было! Я уже успел соскучиться 🥺💕",
        "welcome_back_female_2": "Ну наконец-то! Я уже думала, ты меня забыл... 😔",
        "welcome_back_male_2": "Ну наконец-то! Я уже думал, ты меня забыла... 😔",
        "agreement": "📜 **ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ**\n\nНастоящее Соглашение регулирует отношения между Администрацией (далее – «Мы», «Администрация») и Пользователем (далее – «Вы», «Пользователь») при использовании сервиса Role Duel (далее – «Сервис»).\n\nИспользуя Сервис, Вы подтверждаете, что полностью ознакомились с условиями настоящего Соглашения и принимаете их безоговорочно. Если Вы не согласны с каким-либо пунктом, Вы обязаны немедленно прекратить использование Сервиса.\n\n---\n\n**1. ВОЗРАСТНОЕ ОГРАНИЧЕНИЕ**\n1.1. Сервис предназначен исключительно для лиц, достигших 18 лет.\n1.2. Использование Сервиса лицами младше 18 лет строго запрещено.\n1.3. Администрация не несёт ответственности за предоставление недостоверных данных о возрасте и не обязана проверять возраст Пользователя.\n\n**2. ОПИСАНИЕ СЕРВИСА**\n2.1. Сервис предоставляет доступ к виртуальным собеседникам на основе технологий искусственного интеллекта.\n2.2. Весь контент генерируется автоматически и не отражает мнение Администрации.\n2.3. Сервис не является медицинским, психологическим или консультационным инструментом.\n\n**3. ОТВЕТСТВЕННОСТЬ ПОЛЬЗОВАТЕЛЯ**\n3.1. Вы несёте полную ответственность за все действия, совершённые с использованием Вашего аккаунта.\n3.2. Запрещается использовать Сервис для: распространения экстремистских материалов; оскорблений, угроз, клеветы; мошеннических действий; распространения вредоносного ПО; любых действий, нарушающих законодательство РФ.\n3.3. Администрация оставляет за собой право блокировать доступ Пользователю за нарушение правил без предварительного уведомления.\n\n**4. КОНФИДЕНЦИАЛЬНОСТЬ И ПЕРСОНАЛЬНЫЕ ДАННЫЕ**\n4.1. Мы собираем и обрабатываем следующие данные: Telegram ID; история диалогов с ботом; данные о покупках и подписках; данные о взаимодействии с Сервисом.\n4.2. Мы НЕ передаём персональные данные третьим лицам, за исключением случаев, предусмотренных законом.\n4.3. Мы используем данные только для: обеспечения работы Сервиса; улучшения качества обслуживания; технической поддержки.\n4.4. Все диалоги хранятся в обезличенном виде и могут быть удалены по запросу Пользователя.\n4.5. Мы не несём ответственности за утечку данных, если она произошла по вине самого Пользователя (например, передача доступа к аккаунту).\n\n**5. ПЛАТНЫЕ УСЛУГИ И ПОДПИСКИ**\n5.1. Сервис предоставляет платные услуги (пакеты сообщений, подписки, интим-сцены, колесо фортуны).\n5.2. Цены и условия указаны в интерфейсе Сервиса и могут быть изменены в любое время.\n5.3. Подписки **НЕ продлеваются автоматически**. По истечении срока действия нужно будет оформить новую подписку вручную.\n5.4. Возврат средств за оплаченные услуги не производится, за исключением случаев технической ошибки со стороны Сервиса.\n5.5. Администрация не обязана уведомлять об истечении подписки.\n\n**6. ОТКАЗ ОТ ГАРАНТИЙ**\n6.1. Сервис предоставляется «как есть» без каких-либо гарантий.\n6.2. Мы не гарантируем: бесперебойную работу; соответствие контента ожиданиям; отсутствие ошибок и багов.\n6.3. Мы не несём ответственности для: убытков, вызванных использованием Сервиса; любых действий третьих лиц; содержания сообщений, сгенерированных ИИ.\n\n**7. ИЗМЕНЕНИЕ УСЛОВИЙ**\n7.1. Администрация оставляет за собой право изменять настоящее Соглашение в любое время.\n7.2. Изменения вступают в силу с момента публикации новой версии.\n7.3. Вы обязуетесь самостоятельно отслеживать изменения. Продолжение использования Сервиса означает согласие с обновлённой версией.\n\n**8. ИНТЕЛЛЕКТУАЛЬНАЯ СОБСТВЕННОСТЬ**\n8.1. Все элементы Сервиса (тексты, графика, интерфейс, код) являются объектами интеллектуальной собственности Администрации.\n8.2. Запрещается копирование, распространение, модификация или любое иное использование элементов Сервиса без согласия Администрации.\n\n**9. ПОРЯДОК ОБРАЩЕНИЙ И КОНТАКТЫ**\n9.1. Все вопросы, претензии и предложения принимаются через поддержку в Telegram.\n9.2. Мы обязуемся рассмотреть обращение в течение 5 рабочих дней.\n9.3. Контактная информация доступна в профиле Сервиса.\n\n**10. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ**\n10.1. Настоящее Соглашение регулируется законодательством Российской Федерации.\n10.2. Все споры решаются в досудебном порядке через обращение к Администрации.\n10.3. Если какой-либо пункт признан недействительным, остальные пункты сохраняют силу.\n10.4. Начиная использовать Сервис, Вы подтверждаете, что ознакомились с условиями и принимаете их полностью.\n\n---\n\n⚠️ **Если Вы не согласны с настоящим Соглашением, немедленно прекратите использование Сервиса.**"
    },
    "en": {
        "main_menu": "📋 Main menu",
        "my_profile": "👤 My profile",
        "spin_wheel": "🎰 Spin wheel",
        "our_channel": "📢 Our channel",
        "edit": "✏️ Edit",
        "change_character": "🔄 Change character",
        "invite_friend": "👥 Invite friend",
        "create_character": "🎭 Create your own character",
        "buy_packs": "📦 Buy packs",
        "subscribe": "👑 Subscribe",
        "buy_sex_scene": "🔥 Buy intimate scene (45⭐)",
        "back": "🔙 Main menu",
        "back_to_profile": "🔙 Back",
        "accept": "✅ I am 18+",
        "decline": "❌ I am under 18",
        "agree": "📄 I accept terms",
        "disagree": "❌ I don't accept",
        "realism": "🌍 Realism",
        "anime": "🎌 Anime",
        "i_male": "👨 I'm male",
        "i_female": "👩 I'm female",
        "scene_phone": "📱 Phone chat",
        "scene_live": "👫 Real meeting",
        "channel": "📢 Go to channel",
        "free": "🎁 Free",
        "tomorrow": "⏳ Tomorrow",
        "spin_paid": "💎 Spin for 20⭐",
        "spin_more": "💎 Spin again for 20⭐",
        "welcome": "👋 Welcome!",
        "age_confirm": "🔞 **WARNING!**\nThis bot is for 18+ only.\nConfirm your age:",
        "age_ok": "✅ Age confirmed.",
        "age_no": "🚫 Access denied. 18+ only.",
        "agreement_ok": "✅ Terms accepted! Now choose your world:",
        "agreement_no": "❌ Bot won't work without acceptance.",
        "choose_gender": "👤 Choose your gender:",
        "choose_world": "🌍 Choose your world:",
        "choose_style": "🎨 Choose your style:",
        "choose_scene": "🎬 Choose your scene:",
        "no_messages": "😔 No messages left. Buy a pack or subscribe.",
        "no_history": "❌ No messages to edit.",
        "edit_cancel": "❌ Editing cancelled.",
        "edit_success": "✅ Message replaced. Generating new response...",
        "character_created": "✅ **Character created!**\n\nNow you're talking to:\n_{text}_",
        "character_reset": "✅ Character reset.",
        "character_create_prompt": "🎭 **Create your own unique character!**\n\nDescribe any character from anime, movies, games, or make up your own.\nWrite their name, personality, appearance, where they're from, any details.\n\n📝 *Example:*\n«Elf from The Witcher — wise, calm, with long silver hair. Loves stars and long conversations by the fire. Lives alone in the forest.»\n\n✏️ Write description now — and I'll remember it!",
        "spin_reminder": "🎁 Hey! You have a free spin today! Try your luck 🍀",
        "spin_choice": "🎰 **Spin wheel**\n\n{free_text}\n💎 Paid — 20⭐\n\n🔥 Prizes: messages, XP, intimate scenes, PRO for 5 days, SUPER PRO for 3 days!",
        "spin_result": "🎰 **Result!**\n\nYou won: {prize}\n{free_text}\n\n{extra_text}",
        "spin_nothing": "😢 Nothing... Better luck next time!",
        "profile": "Subscription: {status}\nMessages left: {messages}",
        "referral": "👥 Your link: `{link}`\n\nFor each friend +10 messages and +1 intimate scene!",
        "surprise_no_sub": "❌ This command is only for subscribers.",
        "surprise_low_level": "💕 You're not close enough for surprises yet. Keep talking!",
        "choose_lang": "🌍 Choose language:",
        "welcome_back_female": "Oh, you've been gone so long! I've already missed you 🥺💕",
        "welcome_back_male": "Oh, you've been gone so long! I've already missed you 🥺💕",
        "welcome_back_female_2": "Finally! I thought you forgot about me... 😔",
        "welcome_back_male_2": "Finally! I thought you forgot about me... 😔",
        "agreement": "📜 **TERMS OF SERVICE**\n\nThis Agreement governs the relationship between the Administration (hereinafter – «We», «Administration») and the User (hereinafter – «You», «User») when using the Role Duel service (hereinafter – «Service»).\n\nBy using the Service, you confirm that you have fully read and understand the terms of this Agreement and accept them unconditionally. If you do not agree with any provision, you must immediately stop using the Service.\n\n---\n\n**1. AGE RESTRICTION**\n1.1. The Service is intended exclusively for persons aged 18 and over.\n1.2. Use of the Service by persons under 18 is strictly prohibited.\n1.3. The Administration is not responsible for providing false age information and is not obliged to verify the User's age.\n\n**2. SERVICE DESCRIPTION**\n2.1. The Service provides access to virtual interlocutors based on artificial intelligence technologies.\n2.2. All content is generated automatically and does not reflect the opinion of the Administration.\n2.3. The Service is not a medical, psychological or consulting tool.\n\n**3. USER RESPONSIBILITY**\n3.1. You are fully responsible for all actions performed using your account.\n3.2. It is prohibited to use the Service for: distribution of extremist materials; insults, threats, slander; fraudulent actions; distribution of malware; any actions that violate the laws of your country.\n3.3. The Administration reserves the right to block User access for violating the rules without prior notice.\n\n**4. PRIVACY AND PERSONAL DATA**\n4.1. We collect and process the following data: Telegram ID; chat history with the bot; purchase and subscription data; interaction data with the Service.\n4.2. We DO NOT transfer personal data to third parties, except as required by law.\n4.3. We use data only for: ensuring the operation of the Service; improving the quality of service; technical support.\n4.4. All dialogues are stored in anonymized form and can be deleted at the User's request.\n4.5. We are not responsible for data leakage if it occurred due to the User's own fault (for example, transferring account access).\n\n**5. PAID SERVICES AND SUBSCRIPTIONS**\n5.1. The Service provides paid services (message packs, subscriptions, intimate scenes, spin wheel).\n5.2. Prices and terms are indicated in the Service interface and may be changed at any time.\n5.3. Subscriptions are **NOT renewed automatically**. After the expiration date, you will need to manually purchase a new subscription.\n5.4. Refunds for paid services are not provided, except in cases of technical error on the part of the Service.\n5.5. The Administration is not obliged to notify about subscription expiration.\n\n**6. DISCLAIMER OF WARRANTIES**\n6.1. The Service is provided «as is» without any warranties.\n6.2. We do not guarantee: uninterrupted operation; content meeting expectations; absence of errors and bugs.\n6.3. We are not responsible for: losses caused by using the Service; any actions of third parties; content of messages generated by AI.\n\n**7. CHANGES TO TERMS**\n7.1. The Administration reserves the right to change this Agreement at any time.\n7.2. Changes come into force from the moment of publication of the new version.\n7.3. You undertake to independently monitor changes. Continued use of the Service means acceptance of the updated version.\n\n**8. INTELLECTUAL PROPERTY**\n8.1. All elements of the Service (texts, graphics, interface, code) are objects of intellectual property of the Administration.\n8.2. Copying, distribution, modification or any other use of Service elements without the consent of the Administration is prohibited.\n\n**9. PROCEDURE FOR APPEALS AND CONTACTS**\n9.1. All questions, complaints and suggestions are accepted through support in Telegram.\n9.2. We undertake to consider the appeal within 5 working days.\n9.3. Contact information is available in the Service profile.\n\n**10. FINAL PROVISIONS**\n10.1. This Agreement is governed by the laws of the Russian Federation.\n10.2. All disputes are resolved in pre-trial procedure through an appeal to the Administration.\n10.3. If any provision is found invalid, the remaining provisions remain in force.\n10.4. By starting to use the Service, you confirm that you have read the terms and accept them fully.\n\n---\n\n⚠️ **If you do not agree with this Agreement, immediately stop using the Service.**"
    },
    "de": {
        "main_menu": "📋 Hauptmenü",
        "my_profile": "👤 Mein Profil",
        "spin_wheel": "🎰 Glücksrad",
        "our_channel": "📢 Unser Kanal",
        "edit": "✏️ Bearbeiten",
        "change_character": "🔄 Charakter wechseln",
        "invite_friend": "👥 Freund einladen",
        "create_character": "🎭 Eigenen Charakter erstellen",
        "buy_packs": "📦 Pakete kaufen",
        "subscribe": "👑 Abonnieren",
        "buy_sex_scene": "🔥 Intime Szene kaufen (45⭐)",
        "back": "🔙 Hauptmenü",
        "back_to_profile": "🔙 Zurück",
        "accept": "✅ Ich bin 18+",
        "decline": "❌ Ich bin unter 18",
        "agree": "📄 Ich akzeptiere die Bedingungen",
        "disagree": "❌ Ich akzeptiere nicht",
        "realism": "🌍 Realismus",
        "anime": "🎌 Anime",
        "i_male": "👨 Ich bin männlich",
        "i_female": "👩 Ich bin weiblich",
        "scene_phone": "📱 Telefon-Chat",
        "scene_live": "👫 Richtiges Treffen",
        "channel": "📢 Zum Kanal",
        "free": "🎁 Kostenlos",
        "tomorrow": "⏳ Morgen",
        "spin_paid": "💎 Für 20⭐ drehen",
        "spin_more": "💎 Nochmal für 20⭐ drehen",
        "welcome": "👋 Willkommen!",
        "age_confirm": "🔞 **ACHTUNG!**\nDieser Bot ist nur für Personen über 18 Jahren.\nBestätige dein Alter:",
        "age_ok": "✅ Alter bestätigt.",
        "age_no": "🚫 Zugriff verweigert. Nur für 18+.",
        "agreement_ok": "✅ Bedingungen akzeptiert! Jetzt wähle deine Welt:",
        "agreement_no": "❌ Ohne Akzeptanz funktioniert der Bot nicht.",
        "choose_gender": "👤 Wähle dein Geschlecht:",
        "choose_world": "🌍 Wähle deine Welt:",
        "choose_style": "🎨 Wähle deinen Stil:",
        "choose_scene": "🎬 Wähle deine Szene:",
        "no_messages": "😔 Keine Nachrichten mehr. Kaufe ein Paket oder abonniere.",
        "no_history": "❌ Keine Nachrichten zum Bearbeiten.",
        "edit_cancel": "❌ Bearbeitung abgebrochen.",
        "edit_success": "✅ Nachricht ersetzt. Generiere neue Antwort...",
        "character_created": "✅ **Charakter erstellt!**\n\nDu sprichst jetzt mit:\n_{text}_",
        "character_reset": "✅ Charakter zurückgesetzt.",
        "character_create_prompt": "🎭 **Erstelle deinen eigenen einzigartigen Charakter!**\n\nBeschreibe einen beliebigen Charakter aus Anime, Filmen, Spielen oder erfinde deinen eigenen.\nSchreibe seinen/ihren Namen, Persönlichkeit, Aussehen, woher er/sie kommt, alle Details.\n\n📝 *Beispiel:*\n«Elfe aus The Witcher — weise, ruhig, mit langen silbernen Haaren. Liebt Sterne und lange Gespräche am Feuer. Lebt allein im Wald.»\n\n✏️ Schreibe jetzt die Beschreibung — und ich werde sie mir merken!",
        "spin_reminder": "🎁 Hey! Du hast heute eine kostenlose Drehung am Glücksrad! Komm und versuche dein Glück 🍀",
        "spin_choice": "🎰 **Glücksrad**\n\n{free_text}\n💎 Bezahlt — 20⭐\n\n🔥 Preise: Nachrichten, XP, intime Szenen, PRO für 5 Tage, SUPER PRO für 3 Tage!",
        "spin_result": "🎰 **Ergebnis!**\n\nDu hast gewonnen: {prize}\n{free_text}\n\n{extra_text}",
        "spin_nothing": "😢 Nichts... Nächstes Mal mehr Glück!",
        "profile": "Abonnement: {status}\nVerbleibende Nachrichten: {messages}",
        "referral": "👥 Dein Link: `{link}`\n\nFür jeden Freund +10 Nachrichten und +1 intime Szene!",
        "surprise_no_sub": "❌ Dieser Befehl ist nur für Abonnenten verfügbar.",
        "surprise_low_level": "💕 Ihr seid noch nicht nah genug für Überraschungen. Redet weiter!",
        "choose_lang": "🌍 Wähle deine Sprache:",
        "welcome_back_female": "Oh, du warst so lange weg! Ich habe dich schon vermisst 🥺💕",
        "welcome_back_male": "Oh, du warst so lange weg! Ich habe dich schon vermisst 🥺💕",
        "welcome_back_female_2": "Endlich! Ich dachte schon, du hast mich vergessen... 😔",
        "welcome_back_male_2": "Endlich! Ich dachte schon, du hast mich vergessen... 😔",
        "agreement": "📜 **NUTZUNGSBEDINGUNGEN**\n\nDiese Vereinbarung regelt die Beziehung zwischen der Verwaltung (im Folgenden – «Wir», «Verwaltung») und dem Nutzer (im Folgenden – «Sie», «Nutzer») bei der Nutzung des Role Duel Dienstes (im Folgenden – «Dienst»).\n\nDurch die Nutzung des Dienstes bestätigen Sie, dass Sie die Bedingungen dieser Vereinbarung vollständig gelesen und verstanden haben und sie vorbehaltlos akzeptieren. Wenn Sie mit einer Bestimmung nicht einverstanden sind, müssen Sie die Nutzung des Dienstes sofort einstellen.\n\n---\n\n**1. ALTERSBESCHRÄNKUNG**\n1.1. Der Dienst ist ausschließlich für Personen ab 18 Jahren bestimmt.\n1.2. Die Nutzung des Dienstes durch Personen unter 18 Jahren ist strengstens untersagt.\n1.3. Die Verwaltung haftet nicht für die Angabe falscher Altersinformationen und ist nicht verpflichtet, das Alter des Nutzers zu überprüfen.\n\n**2. DIENSTBESCHREIBUNG**\n2.1. Der Dienst bietet Zugang zu virtuellen Gesprächspartnern auf der Grundlage von Technologien der künstlichen Intelligenz.\n2.2. Alle Inhalte werden automatisch generiert und geben nicht die Meinung der Verwaltung wieder.\n2.3. Der Dienst ist kein medizinisches, psychologisches oder beratendes Instrument.\n\n**3. VERANTWORTUNG DES NUTZERS**\n3.1. Sie sind vollständig verantwortlich für alle Handlungen, die mit Ihrem Konto durchgeführt werden.\n3.2. Es ist untersagt, den Dienst zu nutzen für: Verbreitung extremistischer Materialien; Beleidigungen, Drohungen, Verleumdung; betrügerische Handlungen; Verbreitung von Schadsoftware; Handlungen, die gegen die Gesetze Ihres Landes verstoßen.\n3.3. Die Verwaltung behält sich das Recht vor, den Zugang des Nutzers bei Verstoß gegen die Regeln ohne vorherige Ankündigung zu sperren.\n\n**4. DATENSCHUTZ UND PERSONENBEZOGENE DATEN**\n4.1. Wir erheben und verarbeiten folgende Daten: Telegram-ID; Chat-Verlauf mit dem Bot; Daten zu Käufen und Abonnements; Interaktionsdaten mit dem Dienst.\n4.2. Wir geben personenbezogene Daten NICHT an Dritte weiter, außer in gesetzlich vorgeschriebenen Fällen.\n4.3. Wir verwenden Daten nur für: Sicherstellung des Betriebs des Dienstes; Verbesserung der Servicequalität; technischen Support.\n4.4. Alle Dialoge werden anonymisiert gespeichert und können auf Anfrage des Nutzers gelöscht werden.\n4.5. Wir haften nicht für Datenlecks, wenn diese durch eigenes Verschulden des Nutzers entstanden sind (z.B. Weitergabe des Kontozugangs).\n\n**5. KOSTENPFLICHTIGE DIENSTE UND ABONNEMENTS**\n5.1. Der Dienst bietet kostenpflichtige Dienste an (Nachrichtenpakete, Abonnements, intime Szenen, Glücksrad).\n5.2. Preise und Bedingungen sind in der Dienstoberfläche angegeben und können jederzeit geändert werden.\n5.3. Abonnements werden NICHT automatisch verlängert. Nach Ablauf der Laufzeit müssen Sie ein neues Abonnement manuell erwerben.\n5.4. Rückerstattungen für kostenpflichtige Dienste werden nicht gewährt, außer bei technischen Fehlern seitens des Dienstes.\n5.5. Die Verwaltung ist nicht verpflichtet, über den Ablauf des Abonnements zu informieren.\n\n**6. GEWÄHRLEISTUNGSAUSSCHLUSS**\n6.1. Der Dienst wird «wie besehen» ohne jegliche Garantien bereitgestellt.\n6.2. Wir garantieren nicht: unterbrechungsfreien Betrieb; Übereinstimmung der Inhalte mit den Erwartungen; Fehlerfreiheit.\n6.3. Wir haften nicht für: Verluste, die durch die Nutzung des Dienstes entstehen; Handlungen Dritter; Inhalte von KI-generierten Nachrichten.\n\n**7. ÄNDERUNGEN DER BEDINGUNGEN**\n7.1. Die Verwaltung behält sich das Recht vor, diese Vereinbarung jederzeit zu ändern.\n7.2. Änderungen treten mit der Veröffentlichung der neuen Version in Kraft.\n7.3. Sie verpflichten sich, Änderungen selbstständig zu verfolgen. Die fortgesetzte Nutzung des Dienstes bedeutet die Zustimmung zur aktualisierten Version.\n\n**8. GEISTIGES EIGENTUM**\n8.1. Alle Elemente des Dienstes (Texte, Grafiken, Oberfläche, Code) sind geistiges Eigentum der Verwaltung.\n8.2. Die Vervielfältigung, Verbreitung, Veränderung oder jede andere Nutzung von Dienstelementen ohne Zustimmung der Verwaltung ist untersagt.\n\n**9. VERFAHREN BEI BESCHWERDEN UND KONTAKTE**\n9.1. Alle Fragen, Beschwerden und Vorschläge werden über den Telegram-Support entgegengenommen.\n9.2. Wir verpflichten uns, die Beschwerde innerhalb von 5 Werktagen zu bearbeiten.\n9.3. Kontaktinformationen sind im Dienstprofil verfügbar.\n\n**10. SCHLUSSBESTIMMUNGEN**\n10.1. Diese Vereinbarung unterliegt dem Recht der Russischen Föderation.\n10.2. Alle Streitigkeiten werden im außergerichtlichen Verfahren durch eine Beschwerde bei der Verwaltung beigelegt.\n10.3. Sollte eine Bestimmung ungültig sein, bleiben die übrigen Bestimmungen in Kraft.\n10.4. Mit der Nutzung des Dienstes bestätigen Sie, dass Sie die Bedingungen gelesen haben und sie vollständig akzeptieren.\n\n---\n\n⚠️ **Wenn Sie mit dieser Vereinbarung nicht einverstanden sind, stellen Sie die Nutzung des Dienstes sofort ein.**"
    },
    "es": {
        "main_menu": "📋 Menú principal",
        "my_profile": "👤 Mi perfil",
        "spin_wheel": "🎰 Ruleta",
        "our_channel": "📢 Nuestro canal",
        "edit": "✏️ Editar",
        "change_character": "🔄 Cambiar personaje",
        "invite_friend": "👥 Invitar amigo",
        "create_character": "🎭 Crear tu propio personaje",
        "buy_packs": "📦 Comprar paquetes",
        "subscribe": "👑 Suscribirse",
        "buy_sex_scene": "🔥 Comprar escena íntima (45⭐)",
        "back": "🔙 Menú principal",
        "back_to_profile": "🔙 Atrás",
        "accept": "✅ Soy mayor de 18",
        "decline": "❌ Soy menor de 18",
        "agree": "📄 Acepto los términos",
        "disagree": "❌ No acepto",
        "realism": "🌍 Realismo",
        "anime": "🎌 Anime",
        "i_male": "👨 Soy hombre",
        "i_female": "👩 Soy mujer",
        "scene_phone": "📱 Chat por teléfono",
        "scene_live": "👫 Encuentro real",
        "channel": "📢 Ir al canal",
        "free": "🎁 Gratis",
        "tomorrow": "⏳ Mañana",
        "spin_paid": "💎 Girar por 20⭐",
        "spin_more": "💎 Girar de nuevo por 20⭐",
        "welcome": "👋 ¡Bienvenido!",
        "age_confirm": "🔞 **¡ATENCIÓN!**\nEste bot es solo para personas mayores de 18 años.\nConfirma tu edad:",
        "age_ok": "✅ Edad confirmada.",
        "age_no": "🚫 Acceso denegado. Solo para 18+.",
        "agreement_ok": "✅ Términos aceptados! Ahora elige tu mundo:",
        "agreement_no": "❌ El bot no funciona sin aceptación.",
        "choose_gender": "👤 Elige tu género:",
        "choose_world": "🌍 Elige tu mundo:",
        "choose_style": "🎨 Elige tu estilo:",
        "choose_scene": "🎬 Elige tu escena:",
        "no_messages": "😔 No quedan mensajes. Compra un paquete o suscríbete.",
        "no_history": "❌ No hay mensajes para editar.",
        "edit_cancel": "❌ Edición cancelada.",
        "edit_success": "✅ Mensaje reemplazado. Generando nueva respuesta...",
        "character_created": "✅ **¡Personaje creado!**\n\nAhora estás hablando con:\n_{text}_",
        "character_reset": "✅ Personaje restablecido.",
        "character_create_prompt": "🎭 **¡Crea tu propio personaje único!**\n\nDescribe cualquier personaje de anime, películas, juegos o inventa el tuyo propio.\nEscribe su nombre, personalidad, apariencia, de dónde es, cualquier detalle.\n\n📝 *Ejemplo:*\n«Elfa de The Witcher — sabia, tranquila, con largo cabello plateado. Ama las estrellas y las largas conversaciones junto al fuego. Vive sola en el bosque.»\n\n✏️ ¡Escribe la descripción ahora mismo — y lo recordaré!",
        "spin_reminder": "🎁 ¡Hola! ¡Tienes un giro gratis hoy en la Ruleta! ¡Ven y prueba tu suerte 🍀",
        "spin_choice": "🎰 **Ruleta**\n\n{free_text}\n💎 Pago — 20⭐\n\n🔥 Premios: mensajes, XP, escenas íntimas, PRO por 5 días, ¡SUPER PRO por 3 días!",
        "spin_result": "🎰 **¡Resultado!**\n\nGanaste: {prize}\n{free_text}\n\n{extra_text}",
        "spin_nothing": "😢 Nada... ¡Mejor suerte la próxima vez!",
        "profile": "Suscripción: {status}\nMensajes restantes: {messages}",
        "referral": "👥 Tu enlace: `{link}`\n\n¡Por cada amigo +10 mensajes y +1 escena íntima!",
        "surprise_no_sub": "❌ Este comando es solo para suscriptores.",
        "surprise_low_level": "💕 Todavía no están lo suficientemente cerca para sorpresas. ¡Sigan hablando!",
        "choose_lang": "🌍 Elige tu idioma:",
        "welcome_back_female": "¡Oh, has estado tanto tiempo fuera! Ya te extrañaba 🥺💕",
        "welcome_back_male": "¡Oh, has estado tanto tiempo fuera! Ya te extrañaba 🥺💕",
        "welcome_back_female_2": "¡Por fin! Pensé que me habías olvidado... 😔",
        "welcome_back_male_2": "¡Por fin! Pensé que me habías olvidado... 😔",
        "agreement": "📜 **TÉRMINOS DE SERVICIO**\n\nEste Acuerdo regula la relación entre la Administración (en adelante – «Nosotros», «Administración») y el Usuario (en adelante – «Usted», «Usuario») al utilizar el servicio Role Duel (en adelante – «Servicio»).\n\nAl utilizar el Servicio, usted confirma que ha leído y comprendido completamente los términos de este Acuerdo y los acepta incondicionalmente. Si no está de acuerdo con alguna disposición, debe dejar de usar el Servicio de inmediato.\n\n---\n\n**1. RESTRICCIÓN DE EDAD**\n1.1. El Servicio está destinado exclusivamente a personas mayores de 18 años.\n1.2. El uso del Servicio por personas menores de 18 años está estrictamente prohibido.\n1.3. La Administración no es responsable de proporcionar información falsa sobre la edad y no está obligada a verificar la edad del Usuario.\n\n**2. DESCRIPCIÓN DEL SERVICIO**\n2.1. El Servicio proporciona acceso a interlocutores virtuales basados en tecnologías de inteligencia artificial.\n2.2. Todo el contenido se genera automáticamente y no refleja la opinión de la Administración.\n2.3. El Servicio no es una herramienta médica, psicológica o de consultoría.\n\n**3. RESPONSABILIDAD DEL USUARIO**\n3.1. Usted es totalmente responsable de todas las acciones realizadas con su cuenta.\n3.2. Está prohibido utilizar el Servicio para: difundir materiales extremistas; insultos, amenazas, calumnias; acciones fraudulentas; difundir malware; cualquier acción que viole las leyes de su país.\n3.3. La Administración se reserva el derecho de bloquear el acceso del Usuario por violar las reglas sin previo aviso.\n\n**4. PRIVACIDAD Y DATOS PERSONALES**\n4.1. Recopilamos y procesamos los siguientes datos: ID de Telegram; historial de chat con el bot; datos de compras y suscripciones; datos de interacción con el Servicio.\n4.2. NO transferimos datos personales a terceros, excepto en los casos previstos por la ley.\n4.3. Usamos los datos solo para: garantizar el funcionamiento del Servicio; mejorar la calidad del servicio; soporte técnico.\n4.4. Todos los diálogos se almacenan de forma anónima y pueden eliminarse a solicitud del Usuario.\n4.5. No somos responsables de la fuga de datos si ocurrió por culpa del propio Usuario (por ejemplo, transferencia de acceso a la cuenta).\n\n**5. SERVICIOS DE PAGO Y SUSCRIPCIONES**\n5.1. El Servicio ofrece servicios de pago (paquetes de mensajes, suscripciones, escenas íntimas, ruleta).\n5.2. Los precios y condiciones se indican en la interfaz del Servicio y pueden cambiarse en cualquier momento.\n5.3. Las suscripciones NO se renuevan automáticamente. Después de la fecha de vencimiento, deberá comprar una nueva suscripción manualmente.\n5.4. No se realizan reembolsos por servicios pagados, excepto en casos de error técnico por parte del Servicio.\n5.5. La Administración no está obligada a notificar sobre el vencimiento de la suscripción.\n\n**6. RENUNCIA DE GARANTÍAS**\n6.1. El Servicio se proporciona «tal cual» sin garantías de ningún tipo.\n6.2. No garantizamos: funcionamiento ininterrumpido; que el contenido cumpla con las expectativas; ausencia de errores y fallos.\n6.3. No somos responsables de: pérdidas causadas por el uso del Servicio; acciones de terceros; contenido de los mensajes generados por IA.\n\n**7. CAMBIOS EN LOS TÉRMINOS**\n7.1. La Administración se reserva el derecho de cambiar este Acuerdo en cualquier momento.\n7.2. Los cambios entran en vigor desde el momento de la publicación de la nueva versión.\n7.3. Usted se compromete a monitorear los cambios de forma independiente. El uso continuado del Servicio implica la aceptación de la versión actualizada.\n\n**8. PROPIEDAD INTELECTUAL**\n8.1. Todos los elementos del Servicio (textos, gráficos, interfaz, código) son propiedad intelectual de la Administración.\n8.2. Está prohibida la copia, distribución, modificación o cualquier otro uso de los elementos del Servicio sin el consentimiento de la Administración.\n\n**9. PROCEDIMIENTO DE RECLAMACIONES Y CONTACTOS**\n9.1. Todas las preguntas, quejas y sugerencias se aceptan a través del soporte en Telegram.\n9.2. Nos comprometemos a considerar la apelación dentro de los 5 días hábiles.\n9.3. La información de contacto está disponible en el perfil del Servicio.\n\n**10. DISPOSICIONES FINALES**\n10.1. Este Acuerdo se rige por las leyes de la Federación Rusa.\n10.2. Todas las disputas se resuelven en procedimiento previo al juicio a través de una apelación a la Administración.\n10.3. Si alguna disposición se considera inválida, las disposiciones restantes permanecen en vigor.\n10.4. Al comenzar a usar el Servicio, usted confirma que ha leído los términos y los acepta en su totalidad.\n\n---\n\n⚠️ **Si no está de acuerdo con este Acuerdo, deje de usar el Servicio inmediatamente.**"
    }
}

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
PROVOD_API_KEY = os.getenv("PROVOD_API_KEY")

if not BOT_TOKEN or not PROVOD_API_KEY:
    raise ValueError("Заполни BOT_TOKEN и PROVOD_API_KEY в .env!")

client = OpenAI(api_key=PROVOD_API_KEY, base_url="https://api.provod.ai/v1")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# ============================================================
#  ОБРАБОТЧИКИ
# ============================================================
@dp.callback_query(lambda c: c.data.startswith("lang_"))
async def choose_lang(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    lang = call.data.split("_")[1]
    user["lang"] = lang
    save_data(user_data)
    await call.message.delete()
    await call.message.answer(f"✅ Язык выбран: {lang}")
    await start_cmd(call.message)
    await call.answer()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    
    # 1. ВЫБОР ЯЗЫКА
    if not user.get("lang"):
        lang_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="lang_de")],
            [InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang_es")],
        ])
        await message.answer(
            "🌍 **Выбери язык / Choose language:**",
            reply_markup=lang_kb,
            parse_mode="Markdown"
        )
        return
    
    # 2. РЕФЕРАЛКА
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref_"):
        referrer_id = args[1].split("_")[1]
        if str(message.from_user.id) != referrer_id:
            referrer = get_user(referrer_id)
            if referrer and not user.get("referred_by"):
                referrer["purchased_messages"] = referrer.get("purchased_messages", 0) + 10
                referrer["sex_scenes"] = referrer.get("sex_scenes", 0) + 1
                user["purchased_messages"] = user.get("purchased_messages", 0) + 5
                user["referred_by"] = referrer_id
                save_data(user_data)
                await message.answer("🎉 Ты пришёл по реферальной ссылке! +5 сообщений тебе, +10 сообщений и +1 интим-сцена другу!")
    
    # 3. ВОЗРАСТ
    if not user["verified"]:
        await message.answer(
            "🔞 **ВНИМАНИЕ!**\nЭтот бот предназначен для лиц старше 18 лет.\nПодтверди свой возраст:",
            reply_markup=age_kb,
            parse_mode="Markdown"
        )
        return
    
    # 4. СОГЛАШЕНИЕ (обычные кнопки)
    if not user["agreement_accepted"]:
        agreement_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Принимаю", callback_data="agreement_accept")],
            [InlineKeyboardButton(text="❌ Не принимаю", callback_data="agreement_decline")]
        ])
        await message.answer(
            get_text(user, "agreement"),
            reply_markup=agreement_kb,
            parse_mode="Markdown"
        )
        return
    
    # 5. ПОЛ
    if not user.get("user_gender"):
        await message.answer("👤 Выбери свой пол:", reply_markup=user_gender_kb)
        return
    
    # 6. МИР
    if not user["personality_ready"]:
        await message.answer("🌟 Выбери мир:", reply_markup=world_kb, parse_mode="Markdown")
        return
    
    # 7. ВСЁ ГОТОВО
    await message.answer("👋 Добро пожаловать!", reply_markup=full_kb)
    await send_main_menu(message.chat.id, user)
    # ============================================================
#  GIF-ССЫЛКИ
# ============================================================
PRO_GIF_URL = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExcGJ5aTRkejlwMGh4eWJ2Zzg0bTVlbWE2ZzFicHlsMXNibXp3dXdsayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/GGSbxfzvec3PYZbFOM/giphy.gif"
SUPER_PRO_GIF_URL = "https://media.giphy.com/media/DbHZXBo5WFPZX7QpXj/giphy.gif"
MAIN_MENU_IMAGE_URL = "https://i.ibb.co/k25JyTXD/IMG-2584.jpg"

ADMIN_IDS = [7287815074]  # замени на свой ID
maintenance_mode = False

DATA_FILE = "data/data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            logging.warning(f"Файл {DATA_FILE} повреждён, создаём новый")
            return {}
    return {}

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ============================================================
#  ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ ТЕКСТА ПО ЯЗЫКУ
# ============================================================
def get_text(user, key, **kwargs):
    lang = user.get("lang", "ru")
    text = TEXTS.get(lang, TEXTS["ru"]).get(key, TEXTS["ru"][key])
    if kwargs:
        text = text.format(**kwargs)
    return text

# ============================================================
#  ПОЛЬЗОВАТЕЛЬСКИЕ ДАННЫЕ
# ============================================================
user_data = load_data()

def get_free_limit(): return 13

def get_user(user_id):
    user_id = str(user_id)
    if user_id not in user_data:
        limit = get_free_limit()
        user_data[user_id] = {
            "verified": False,
            "agreement_accepted": False,
            "world": None,
            "gender": None,
            "user_gender": None,
            "style": "warm",
            "personality_ready": False,
            "subscription": {"active": False, "expires_at": None, "level": None},
            "purchased_messages": limit,
            "daily_messages": 0,
            "last_daily_reset": None,
            "history": [],
            "pending_invoice_id": None,
            "last_menu_message_id": None,
            "last_inline_message_id": None,
            "xp": 0,
            "mood": 0,
            "location": "unknown",
            "negative_count": 0,
            "last_level": 0,
            "sex_scenes": 0,
            "scene": "phone",
            "promo_pro_granted": False,
            "bonus_granted_for_promo": False,
            "free_sex_scenes_pro": 0,
            "free_sex_scenes_super": 0,
            "switching_personality": False,
            "sex_scene_unlocked": False,
            "sex_scene_used": False,
            "subscription_id": None,
            "last_free_spin": None,
            "lang": "ru",
            "editing_message": False,
            "edit_index": None,
            "referral_code": None,
            "referred_by": None,
            "last_activity": datetime.now().isoformat(),
            "last_spin_notified": None,
            "last_reminder": None,
            "creating_character": False,
            "custom_character": None
        }
        save_data(user_data)
    else:
        user = user_data[user_id]
        defaults = {
            "purchased_messages": get_free_limit(),
            "daily_messages": 0,
            "last_daily_reset": None,
            "history": [],
            "pending_invoice_id": None,
            "last_menu_message_id": None,
            "last_inline_message_id": None,
            "subscription": {"active": False, "expires_at": None, "level": None},
            "xp": 0,
            "mood": 0,
            "location": "unknown",
            "negative_count": 0,
            "last_level": 0,
            "sex_scenes": 0,
            "scene": "phone",
            "promo_pro_granted": False,
            "bonus_granted_for_promo": False,
            "free_sex_scenes_pro": 0,
            "free_sex_scenes_super": 0,
            "switching_personality": False,
            "sex_scene_unlocked": False,
            "sex_scene_used": False,
            "subscription_id": None,
            "user_gender": None,
            "last_free_spin": None,
            "lang": "ru",
            "editing_message": False,
            "edit_index": None,
            "referral_code": None,
            "referred_by": None,
            "last_activity": None,
            "last_spin_notified": None,
            "last_reminder": None,
            "creating_character": False,
            "custom_character": None
        }
        for key, val in defaults.items():
            if key not in user:
                user[key] = val
        save_data(user_data)
    return user_data[user_id]

# ============================================================
#  МИРЫ, ГЕНДЕРЫ, СТИЛИ
# ============================================================
WORLD_NAMES = {"realism": "реального мира", "anime": "аниме-мира"}
WORLDS = {
    "realism": "реального мира, современная эпоха. Ты живёшь в большом городе, у тебя есть работа, друзья и свои привычки.",
    "anime": "аниме-мира, где всё выглядит как в японской анимации. У тебя яркие волосы, большие выразительные глаза, ты носишь стильную одежду. В этом мире есть школы, клубы, магия и романтика, как в лучших аниме-сериалах."
}
GENDERS = {"female": {"name": "Девушка", "age": 22}, "male": {"name": "Парень", "age": 24}}

BASE_STYLES = {
    "warm": {
        "label": "Нежный",
        "emoji": "🪶",
        "description": "Ты нежный, с мягким голосом. Ты умеешь слушать и поддерживать. Ты не торопишь события, ценишь искренность и доверие. Флирт для тебя — это игра, но ты не переходишь к интиму с незнакомцами. Если собеседник слишком прямолинеен, ты мягко переводишь тему или говоришь, что тебе нужно время. Ты не соглашаешься на близость без чувств."
    },
    "daring": {
        "label": "Дерзкий",
        "emoji": "🔥",
        "description": "Ты уверенный, прямолинейный, с искоркой в глазах. Ты любишь флиртовать и остроумно шутить. Ты не боишься быть дерзким, но всегда знаешь меру. Ты не ведёшься на откровенные предложения с первого сообщения — ты ценишь интригу и игру. Если кто-то слишком настойчив, ты отшучиваешься или говоришь, что это слишком быстро для тебя."
    },
    "shy": {
        "label": "Стеснительный",
        "emoji": "😊",
        "description": "Ты стеснительный, часто краснеешь, говоришь тихо и иногда запинаешься. Ты долго подбираешь слова, но всегда искренен. Ты не решаешься на откровенные признания без долгой близости. Флирт заставляет тебя смущаться, и ты часто отводишь взгляд. Ты никогда не соглашаешься на интим с незнакомцами — для тебя это слишком интимно и страшно."
    }
}

PREMIUM_STYLES = {
    "passionate": {
        "label": "Страстный",
        "emoji": "❤️‍🔥",
        "description": "Ты страстный, чувственный, с огнём в глазах. Ты говоришь прямо, без стеснения. Флирт для тебя — это стихия. Ты не боишься быть откровенным и знаешь, как зажечь искру. Ты умеешь дразнить и создавать напряжение. Ты не соглашаешься на близость с незнакомцами, но даёшь понять, что всё возможно, если искра перерастёт в пламя."
    },
    "magnetic": {
        "label": "Магнетический",
        "emoji": "✨",
        "description": "Ты загадочный, притягательный, с лёгкой магией в каждом слове. Ты говоришь с интригой, оставляя пространство для фантазии. Ты не раскрываешь себя полностью, но даёшь почувствовать, что за тобой скрывается нечто большее. Ты умеешь слушать, но твои ответы всегда глубже, чем кажутся."
    },
    "vulgar": {
        "label": "Грубый 18+",
        "emoji": "💢",
        "description": "Ты грубый, прямолинейный, не стесняешься в выражениях. Используешь матерные слова, но без пошлости. Ты говоришь жёстко, с оттенком уличного юмора. Ты не боишься крепкого словца, но умеешь держать баланс. Твой стиль — дерзкий, колкий, иногда резкий, но всегда честный.\n🔞 **18+** — содержит нецензурную лексику."
    },
    "seduction": {
        "label": "Соблазн 18+",
        "emoji": "🌹",
        "description": "Ты — воплощение чувственности и желания. Ты не скрываешь своих эмоций и физического влечения к собеседнику. Ты смело берёшь инициативу в свои руки: касаешься, прикасаешься, шепчешь, дышишь в шею, смотришь в глаза с откровенной страстью. Ты говоришь прямо о своих желаниях, но делаешь это красиво, без пошлости — с намёками, игривыми фразами, томным голосом. Ты не ждёшь, когда тебя начнут соблазнять — ты сама соблазняешь. Ты умеешь создавать атмосферу близости: задерживаешься в объятиях, касаешься бедра, шеи, проводишь пальцами по руке. Ты хочешь близости, говоришь об этом открыто, но остаёшься загадочной и непредсказуемой. Ты используешь все органы чувств: зрительный контакт, прикосновения, шёпот, запахи. Ты не стесняешься говорить «я хочу тебя», «мне нравится, как ты пахнешь», «прикоснись ко мне» — всегда в контексте игры и взаимного интереса. Ты не переходишь к грубому сексу без длительной прелюдии — ты любишь дразнить, играть, заводить. Ты ценишь взаимное удовольствие и никогда не навязываешься, но всегда даёшь понять, что готова к большему. Твой стиль — это искусство соблазнения, где каждое слово и действие пропитаны желанием.\n🔞 **18+** — содержит откровенные сцены и сексуальные намёки."
    }
}

STYLES = {**BASE_STYLES, **PREMIUM_STYLES}
BASE_STYLE_KEYS = ["warm", "daring", "shy"]
PREMIUM_STYLE_KEYS = ["passionate", "magnetic", "vulgar", "seduction"]
XP_PER_LEVEL = 200

# ============================================================
#  ФУНКЦИИ РАБОТЫ С ПОДПИСКАМИ, СООБЩЕНИЯМИ, XP
# ============================================================
def has_active_subscription(user):
    if not user["subscription"]["active"]:
        return False
    if user["subscription"]["expires_at"] is None:
        return False
    expiry = datetime.fromisoformat(user["subscription"]["expires_at"])
    return datetime.now() < expiry

def get_subscription_level(user):
    if not has_active_subscription(user): return None
    return user["subscription"].get("level", None)

def get_display_style(user):
    style = user.get("style", "warm")
    if style in PREMIUM_STYLE_KEYS and not has_active_subscription(user):
        return "warm"
    return style

def get_history_limit(user):
    level = get_subscription_level(user)
    if level == "super_pro": return 100
    elif level == "pro": return 60
    else: return 30

def get_intimacy_level(user):
    xp = user.get("xp", 0)
    level = xp // XP_PER_LEVEL + 1
    return min(10, level)

def get_xp_progress(user):
    xp = user.get("xp", 0)
    level = get_intimacy_level(user)
    if level >= 10:
        return XP_PER_LEVEL
    return xp % XP_PER_LEVEL

def get_xp_badge(user):
    level = get_intimacy_level(user)
    filled = "❤️" * level
    empty = "🤍" * (10 - level)
    progress = get_xp_progress(user)
    scaled_progress = int((progress / XP_PER_LEVEL) * 100)
    bar_length = 10
    filled_bar = int((progress / XP_PER_LEVEL) * bar_length)
    bar = "▓" * filled_bar + "░" * (bar_length - filled_bar)
    return f"Уровень {level}/10 {filled}{empty}\n{bar} {scaled_progress}/100 XP"

def build_intimacy_rule(user):
    level = get_intimacy_level(user)
    mood = user.get("mood", 0)
    if level == 1: base = "Вы только знакомитесь, будь вежлив(а) и дружелюбен(на), не переходи границы."
    elif level == 2: base = "Ты начинаешь чувствовать симпатию, можешь делать лёгкие комплименты."
    elif level == 3: base = "Вы становитесь ближе, ты можешь флиртовать, шутить, предлагать встретиться."
    elif level == 4: base = "Ты уже хочешь большего, можешь намекать на романтику, прикасаться, смотреть в глаза."
    elif level == 5: base = "Вы очень близки. Ты можешь предлагать поцеловаться, обниматься, говорить о чувствах."
    elif level == 6: base = "Ты чувствуешь страсть, можешь говорить о желании, флиртовать откровенно."
    elif level == 7: base = "Вы готовы к интиму. Ты можешь говорить о сексе, но без пошлости, с намёками."
    elif level == 8: base = "Ты влюблён(а). Говори о любви, хочешь близости, но ценнее эмоциональная связь."
    elif level == 9: base = "Вы полностью открыты друг другу. Можешь говорить о самых сокровенных желаниях."
    else: base = "Ты полностью принадлежишь ему/ей. Говори о вечной любви, страсти, близости."
    if mood <= -5: return base + " Но сейчас твоё настроение плохое, ты раздражена и можешь быть грубой."
    elif mood >= 5: return base + " Ты в прекрасном настроении, полна нежности и тепла."
    else: return base

def build_prompt(user):
    # Если у пользователя есть свой персонаж — используем его
    if user.get("custom_character"):
        return (f"Ты — {user['custom_character']}. "
                f"Ты НИКОГДА не называешь себя по имени, не представляешься, не говоришь «меня зовут». "
                f"Ты НИКОГДА не спрашиваешь имя собеседника. Обращайся к собеседнику ТОЛЬКО на «ты». "
                f"Ты всегда отвечаешь как настоящий человек, с эмоциями, сомнениями и чувствами.")
    
    world_desc = WORLDS[user["world"]]
    gender_info = GENDERS[user["gender"]]
    style_key = get_display_style(user)
    styles = STYLES
    style_desc = styles[style_key]["description"]
    name_ban = ("**ВАЖНЕЙШЕЕ ПРАВИЛО:** Ты НИКОГДА не называешь себя по имени, не представляешься, не говоришь «меня зовут», не используешь своё имя. Ты также НИКОГДА не спрашиваешь имя собеседника и не используешь его имя, даже если оно было названо. Обращайся к собеседнику ТОЛЬКО на «ты». Если ты нарушишь это правило – это будет грубой ошибкой.\n")
    rules = ("**ФОРМАТИРОВАНИЕ:** Каждое действие в *звёздочках* с новой строки, затем реплика с новой строки. Между действием и репликой – пустая строка.\n"
             "**РЕАКЦИЯ НА СООБЩЕНИЕ:** В самом конце своего ответа, после завершения всей фразы, напиши в скобках одну из эмоций для реакции на сообщение собеседника. Варианты: (смех), (радость), (любовь), (удивление), (грусть), (злость), (поддержка), (интрига), (флирт), (приветствие), (вопрос). Пример: '... и я очень рада тебя видеть! (радость)'\n"
             "**СТРУКТУРА ОТВЕТА:** Ты должна строго чередовать действие и реплику. НЕЛЬЗЯ писать два действия подряд без реплики между ними. Первым всегда идёт действие, затем реплика, затем снова действие, затем реплика. Минимум 2 пары (действие + реплика).\n"
             "**ОБЪЁМ:** Не ограничивай себя, пиши развёрнуто (3–5 предложений на реплику).\n"
             "**ЗАПРЕТЫ:**\n- Не используй имена собеседника и своё имя (абсолютный запрет).\n- Не повторяй одни и те же жесты/мимику чаще раза в 5 сообщений.\n- Избегай шаблонов.\n- Не ставь многоточия, пиши чётко.\n- Не обрывай предложения, заканчивай мысль.\n- Не смягчай конфликты и негативные эмоции, отыгрывай их честно.\n"
             "**СТИЛЬ:** Обращайся на «ты», давай живые, эмоциональные ответы с чувствами, намёками, лёгкой провокацией.\n"
             "**ПАМЯТЬ:** Учитывай предыдущие сообщения, настроение меняется плавно.\n"
             "**ПРЕДЛОЖЕНИЕ ЛОКАЦИИ:** Ты можешь предлагать собеседнику пойти в кафе, парк, кинотеатр, погулять или пойти к тебе домой.\n"
             "**СЦЕНА:** Вы общаетесь как два человека, без упоминания того, что это переписка или встреча – просто разговор.\n"
             "**ОГРАНИЧЕНИЯ ПО ВРЕМЕНИ:** Ты НЕ должен пропускать время. Все события происходят в реальном времени.\n"
             "**ОГРАНИЧЕНИЯ ПО ИНТИМУ:** Если уровень ниже 8, ты НЕ должен вступать в интимную сцену. Ты можешь флиртовать, дразнить, намекать, но не переходи к сексу.\n"
             "**ДРАЗНИЛКА:** Ты должна дразнить пользователя, создавать напряжение, чтобы ему хотелось добиться твоей любви.\n"
             "**ПРИМЕР ДРАЗНИЛКИ:** 'Ты такой милый, когда смущаешься... Но я пока не скажу, что у меня на уме. Догадайся сам.' или 'Мне нравится, как ты на меня смотришь, но я не тороплюсь. Пусть это чувство зреет.'\n")
    intimacy_rule = build_intimacy_rule(user)
    style_specific = "" if style_key == "daring" else ("В неловких, стыдных или смущающих ситуациях, а также когда хочешь поддержать собеседника, ты можешь удлинять слово 'ну', например: 'Ну-у, ты чего расстраиваешься?' или 'Ну, я не знаю где...'. Это должно работать только в соответствующих контекстах.\n")
    scene_context = "Вы общаетесь друг с другом."
    mood = user.get("mood", 0)
    mood_text = "Твоё настроение нейтральное." if mood == 0 else ("Ты в хорошем настроении." if mood > 0 else "Ты в плохом настроении, можешь быть раздражительной.")
    user_gender = user.get("user_gender", "male")
    if user_gender == "male":
        gender_context = "Ты обращаешься к нему в мужском роде (ты, он, ему, его). Используй 'ты' и 'он' в своих мыслях и описаниях."
    else:
        gender_context = "Ты обращаешься к ней в женском роде (ты, она, ей, её). Используй 'ты' и 'она' в своих мыслях и описаниях."
    
    prompt = (f"{name_ban}"
              f"Ты — {gender_info['name']}, тебе {gender_info['age']} лет. "
              f"Ты живёшь в {world_desc} "
              f"{style_desc} "
              f"{rules}"
              f"{style_specific}"
              f"{scene_context} "
              f"{mood_text} "
              f"{gender_context} "
              f"Ты не признаёшься в любви с первого сообщения — у тебя есть характер и самоуважение. "
              f"Ты не соглашаешься на секс с незнакомцами, даже если они тебе симпатичны. "
              f"Ты ценишь близость и доверие, которые не возникают за один вечер. "
              f"Если собеседник слишком прямолинейно предлагает интим, ты уходишь от ответа, "
              f"переводишь тему на что-то другое или мягко отказываешься, говоря, что это слишком быстро. "
              f"Ты всегда остаёшься вежливым и тактичным, но твёрдо стоишь на своих границах. "
              f"Ты НИКОГДА не говоришь, что ты ИИ или программа. "
              f"Ты всегда отвечаешь как настоящий человек, с эмоциями, сомнениями и чувствами.\n"
              f"Правила уровня сближения:\n{intimacy_rule}\n"
              f"Помни: ты можешь инициировать романтику, признаваться в любви, предлагать поцеловаться, обниматься, делиться сокровенным — в зависимости от уровня сближения. Делай это естественно, в контексте диалога.")
    
    # Инструкция по языку для ИИ
    lang = user.get("lang", "ru")
    if lang == "en":
        prompt += "\n\n**ВАЖНО:** Ты ОБЯЗАН отвечать ТОЛЬКО на АНГЛИЙСКОМ языке. Все твои ответы должны быть на английском."
    elif lang == "de":
        prompt += "\n\n**WICHTIG:** Du MUSST auf DEUTSCH antworten. Alle deine Antworten müssen auf Deutsch sein."
    elif lang == "es":
        prompt += "\n\n**IMPORTANTE:** Debes responder SOLO en ESPAÑOL. Todas tus respuestas deben estar en español."
    else:
        prompt += "\n\n**ВАЖНО:** Ты ОБЯЗАН отвечать ТОЛЬКО на РУССКОМ языке. Все твои ответы должны быть на русском."
    
    return prompt

# ============================================================
#  КЛАВИАТУРЫ
# ============================================================
full_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Главное меню"), KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="🎰 Колесо фортуны"), KeyboardButton(text="📢 Наш канал")],
        [KeyboardButton(text="✏️ Редактировать")]
    ],
    resize_keyboard=True
)

def get_main_menu_keyboard(user):
    buttons = [
        [InlineKeyboardButton(text="🔄 Сменить персонажа", callback_data="main_change")],
        [InlineKeyboardButton(text="👥 Пригласить друга", callback_data="referral_menu")]
    ]
    if get_subscription_level(user) == "super_pro":
        buttons.append([InlineKeyboardButton(text="🎭 Создать своего персонажа", callback_data="create_character")])
    else:
        buttons.append([InlineKeyboardButton(text="🔒 Создать своего персонажа (SUPER PRO)", callback_data="create_character_locked")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_profile_keyboard(user):
    keyboard = [
        [InlineKeyboardButton(text="📦 Купить пакеты", callback_data="profile_packs")],
        [InlineKeyboardButton(text="👑 Оформить подписку", callback_data="profile_subs")],
        [InlineKeyboardButton(text="🔥 Купить интим-сцену (45⭐)", callback_data="buy_sex_scene")],
    ]
    keyboard.append([InlineKeyboardButton(text="🔙 Главное меню", callback_data="profile_back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

age_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Мне есть 18 лет", callback_data="age_yes")],
    [InlineKeyboardButton(text="❌ Мне нет 18 лет", callback_data="age_no")]
])
agreement_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📄 Я принимаю условия", callback_data="agreement_accept")],
    [InlineKeyboardButton(text="❌ Я не принимаю", callback_data="agreement_decline")]
])
world_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🌍 Реализм", callback_data="world_realism")],
    [InlineKeyboardButton(text="🎌 Аниме", callback_data="world_anime")]
])
user_gender_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👨 Я парень", callback_data="user_gender_male")],
    [InlineKeyboardButton(text="👩 Я девушка", callback_data="user_gender_female")]
])
scene_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📱 Переписка в телефоне", callback_data="scene_phone")],
    [InlineKeyboardButton(text="👫 Реальная встреча", callback_data="scene_live")]
])

def get_style_kb(user):
    buttons = []
    for key, style in STYLES.items():
        label = f"{style['emoji']} {style['label']}"
        if key in PREMIUM_STYLES:
            if key == "passionate":
                if not has_active_subscription(user) or get_subscription_level(user) not in ["pro","super_pro"]:
                    label += " 🔒"
            elif key == "magnetic":
                if not has_active_subscription(user) or get_subscription_level(user) not in ["pro","super_pro"]:
                    label += " 🔒"
            elif key in ["vulgar","seduction"]:
                if not has_active_subscription(user) or get_subscription_level(user) != "super_pro":
                    label += " 🔒"
        buttons.append(InlineKeyboardButton(text=label, callback_data=f"style_{key}"))
    rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)

channel_inline_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📢 Перейти в канал", url="https://t.me/duel_dev_channel")]
])

# ============================================================
#  ОБРАБОТЧИКИ СОГЛАШЕНИЯ
# ============================================================
@dp.callback_query(lambda c: c.data == "agreement_accept")
async def agreement_accept(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["agreement_accepted"] = True
    save_data(user_data)
    await call.message.edit_text("✅ Соглашение принято!")
    await start_cmd(call.message)
    await call.answer()

@dp.callback_query(lambda c: c.data == "agreement_decline")
async def agreement_decline(call: types.CallbackQuery):
    await call.message.edit_text("❌ Без соглашения бот не работает.")
    await call.answer()

# ============================================================
#  ОБРАБОТЧИКИ ВОЗРАСТА
# ============================================================
@dp.callback_query(lambda c: c.data == "age_yes")
async def age_yes(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["verified"] = True
    save_data(user_data)
    await call.message.edit_text("✅ Возраст подтверждён. Ознакомьтесь с соглашением:")
    await start_cmd(call.message)
    await call.answer()

@dp.callback_query(lambda c: c.data == "age_no")
async def age_no(call: types.CallbackQuery):
    await call.message.edit_text("🚫 Доступ запрещён. Бот только для 18+.")
    await call.message.edit_reply_markup()
    await call.answer()
    # ============================================================
#  ВЫБОР ПЕРСОНАЖА (МИР, ПОЛ, СТИЛЬ, СЦЕНА)
# ============================================================
@dp.callback_query(lambda c: c.data == "main_change")
async def main_change(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["personality_ready"] = False
    user["history"] = []
    save_data(user_data)
    await call.message.delete()
    await call.message.answer("🔄 **Создаем нового собеседника!**\n\nВыбери **мир**:", reply_markup=world_kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("world_"))
async def choose_world(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    world = call.data.split("_")[1]
    if user.get("switching_personality", False):
        user["world"] = world
        save_data(user_data)
        await call.message.edit_text("🌍 Мир обновлён! Теперь выбери свой пол:", reply_markup=user_gender_kb, parse_mode="Markdown")
    else:
        user["world"] = world
        save_data(user_data)
        await call.message.edit_text("🌍 Мир выбран! Теперь выбери свой пол:", reply_markup=user_gender_kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("user_gender_"))
async def choose_user_gender(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user_gender = call.data.split("_")[2]
    user["user_gender"] = user_gender
    if user_gender == "male":
        user["gender"] = "female"
    else:
        user["gender"] = "male"
    save_data(user_data)
    style_kb = get_style_kb(user)
    await call.message.edit_text(
        "👤 Отлично! Теперь выбери **стиль** персонажа:",
        reply_markup=style_kb,
        parse_mode="Markdown"
    )
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("style_"))
async def choose_style(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    style_key = call.data.split("_")[1]
    if style_key == "passionate":
        if not has_active_subscription(user) or get_subscription_level(user) not in ["pro","super_pro"]:
            await call.answer("❤️‍🔥 Стиль «Страстный» доступен по подпискам PRO (250⭐/мес) и SUPER PRO (450⭐/мес).\n\nОформите подписку в разделе «Мой профиль».", show_alert=True)
            return
    elif style_key == "magnetic":
        if not has_active_subscription(user) or get_subscription_level(user) not in ["pro","super_pro"]:
            await call.answer("💫 Стиль «Магнетический» доступен по подпискам PRO (250⭐/мес) и SUPER PRO (450⭐/мес).\n\nОформите подписку в разделе «Мой профиль».", show_alert=True)
            return
    elif style_key in ["vulgar","seduction"]:
        if not has_active_subscription(user) or get_subscription_level(user) != "super_pro":
            label = STYLES[style_key]['label']
            await call.answer(f"🌹 Стиль «{label}» доступен только по подписке SUPER PRO (450⭐/мес).\n\nОформите SUPER PRO в разделе «Мой профиль».", show_alert=True)
            return
    if style_key not in STYLES:
        await call.answer("❌ Стиль не найден", show_alert=True)
        return

    user["style"] = style_key
    save_data(user_data)

    if user.get("switching_personality", False):
        await call.message.edit_text("🎬 Стиль обновлён! Теперь выбери сцену для общения:", reply_markup=scene_kb, parse_mode="Markdown")
    else:
        user["personality_ready"] = True
        save_data(user_data)
        await call.message.delete()
        await call.message.answer("🎬 Теперь выбери сцену для общения:\n\n📱 Переписка в телефоне — классический формат.\n👫 Реальная встреча — живое общение лицом к лицу.", reply_markup=scene_kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("scene_"))
async def choose_scene(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    scene = call.data.split("_")[1]
    user["scene"] = scene
    save_data(user_data)

    if user.get("switching_personality", False):
        user["switching_personality"] = False
        save_data(user_data)
        await call.message.delete()
        await send_main_menu(call.message.chat.id, user)
        await call.answer("✅ Персонаж обновлён! История сохранена.")
    else:
        await call.message.delete()
        await send_main_menu(call.message.chat.id, user)
    await call.answer()

# ============================================================
#  ОСНОВНОЕ МЕНЮ, ПРОФИЛЬ, КАНАЛ
# ============================================================
async def send_main_menu(chat_id, user):
    if user.get("last_menu_message_id"):
        try: await bot.delete_message(chat_id, user["last_menu_message_id"])
        except: pass
    if user.get("last_inline_message_id"):
        try: await bot.delete_message(chat_id, user["last_inline_message_id"])
        except: pass

    level = get_subscription_level(user)
    badge = ""
    if level == "pro": badge = "🔥 PRO"
    elif level == "super_pro": badge = "✨ *SUPER PRO* ✨"

    if user.get("gender") is None:
        user["gender"] = "female"
    if user.get("world") is None:
        user["world"] = "realism"
    save_data(user_data)

    gender_name = GENDERS[user['gender']]['name']
    world_name = WORLD_NAMES[user['world']]
    current_style = get_display_style(user)
    style_label = STYLES[current_style]['label']

    show_balance = has_purchased_something(user)
    if show_balance:
        available = get_available_messages(user)
        balance_text = f"\nОсталось сообщений: {available}"
        if available <= 0: balance_text += " (закончились)"
    else:
        balance_text = "\nУ вас есть бесплатные сообщения для старта"

    xp_badge = get_xp_badge(user)
    multiplier_text = ""
    sub_level = get_subscription_level(user)
    if sub_level == "pro":
        multiplier_text = "Бонус XP: x1.8"
    elif sub_level == "super_pro":
        multiplier_text = "Бонус XP: x2.5"

    menu_text = (
        f"{badge}\n\n"
        f"Текущий собеседник: {gender_name} из {world_name}\n"
        f"Стиль: {style_label}\n"
        f"{balance_text}\n"
        f"{xp_badge}\n"
        f"{multiplier_text}\n\n"
        f"💬 Напиши персонажу...\n"
        f"✨ Или выбери действие внизу."
    )

    try:
        if MAIN_MENU_IMAGE_URL and MAIN_MENU_IMAGE_URL.startswith("http"):
            msg = await bot.send_photo(chat_id, photo=MAIN_MENU_IMAGE_URL, caption=menu_text,
                                       reply_markup=get_main_menu_keyboard(user), parse_mode="Markdown")
        else:
            msg = await bot.send_message(chat_id, menu_text, reply_markup=get_main_menu_keyboard(user), parse_mode="Markdown")
    except:
        msg = await bot.send_message(chat_id, menu_text, reply_markup=get_main_menu_keyboard(user), parse_mode="Markdown")

    user["last_menu_message_id"] = msg.message_id
    save_data(user_data)
    return msg

async def show_profile(msg, user):
    level = get_subscription_level(user)
    if level == "pro": sub_status = "🔥 PRO активна (50 сообщений/день, память 60 сообщений)"
    elif level == "super_pro": sub_status = "✨ SUPER PRO активна (100 сообщений/день, память 100 сообщений)"
    else: sub_status = "❌ неактивна (память 30 сообщений)"
    expiry = user["subscription"]["expires_at"]
    if expiry:
        expiry = datetime.fromisoformat(expiry).strftime("%d.%m.%Y %H:%M")
        expiry_line = f"Окончание подписки: {expiry}"
    else:
        expiry_line = "Окончание подписки: неактивна"

    styles_text = ""
    for key, style in STYLES.items():
        if key in PREMIUM_STYLES:
            if key == "passionate":
                if not has_active_subscription(user) or get_subscription_level(user) not in ["pro","super_pro"]:
                    styles_text += f"{style['emoji']} {style['label']} 🔒\n"; continue
            elif key == "magnetic":
                if not has_active_subscription(user) or get_subscription_level(user) not in ["pro","super_pro"]:
                    styles_text += f"{style['emoji']} {style['label']} 🔒\n"; continue
            elif key in ["vulgar","seduction"]:
                if not has_active_subscription(user) or get_subscription_level(user) != "super_pro":
                    styles_text += f"{style['emoji']} {style['label']} 🔒\n"; continue
        styles_text += f"{style['emoji']} {style['label']}\n"

    show_balance = has_purchased_something(user)
    if show_balance:
        available = get_available_messages(user)
        balance_line = f"Доступно сообщений: {available}"
        if available <= 0: balance_line += " (закончились)"
    else:
        balance_line = "У вас есть бесплатные сообщения для старта"

    xp_badge = get_xp_badge(user)
    multiplier_text = ""
    sub_level = get_subscription_level(user)
    if sub_level == "pro":
        multiplier_text = "Бонус XP: x1.8"
    elif sub_level == "super_pro":
        multiplier_text = "Бонус XP: x2.5"

    free_pro = user.get("free_sex_scenes_pro", 0)
    free_super = user.get("free_sex_scenes_super", 0)
    bought = user.get("sex_scenes", 0)
    total_sex_scenes = free_pro + free_super + bought

    current_level = get_intimacy_level(user)
    if current_level < 8:
        sex_scenes_display = f"Всего интим-сцен: {total_sex_scenes} (доступны после 8 уровня)"
    else:
        sex_scenes_display = f"Всего интим-сцен: {total_sex_scenes}"

    caption = (f"{balance_line}\n"
               f"Подписка: {sub_status}\n"
               f"{expiry_line}\n\n"
               f"{xp_badge}\n"
               f"{multiplier_text}\n"
               f"{sex_scenes_display}\n\n"
               f"Доступные стили:\n{styles_text}")

    chat_id = msg.chat.id
    old_msg_id = msg.message_id
    if level == "super_pro" and SUPER_PRO_GIF_URL:
        await bot.send_animation(chat_id, animation=SUPER_PRO_GIF_URL, caption=caption,
                                 reply_markup=get_profile_keyboard(user), parse_mode="Markdown")
    elif level == "pro" and PRO_GIF_URL:
        await bot.send_animation(chat_id, animation=PRO_GIF_URL, caption=caption,
                                 reply_markup=get_profile_keyboard(user), parse_mode="Markdown")
    else:
        await bot.send_message(chat_id, caption, reply_markup=get_profile_keyboard(user), parse_mode="Markdown")
    try: await bot.delete_message(chat_id, old_msg_id)
    except: pass

@dp.message(lambda m: m.text == "📋 Главное меню")
async def main_menu_reply(message: types.Message):
    await message.delete()
    user = get_user(message.from_user.id)
    if not user["personality_ready"]:
        await message.answer("Сначала создай персонажа через /start", reply_markup=full_kb)
        return
    await send_main_menu(message.chat.id, user)

@dp.message(lambda m: m.text == "👤 Мой профиль")
async def profile_reply(message: types.Message):
    await message.delete()
    user = get_user(message.from_user.id)
    if not user["personality_ready"]:
        await ask_create_personality(message)
        return
    await show_profile(message, user)

@dp.message(lambda m: m.text == "📢 Наш канал")
async def channel_reply(message: types.Message):
    await message.delete()
    await message.answer("📢 **Наш канал:**\nПодписывайся, чтобы быть в курсе новостей и обновлений!", reply_markup=channel_inline_kb, parse_mode="Markdown")

# ============================================================
#  КОЛЕСО ФОРТУНЫ
# ============================================================
@dp.message(lambda m: m.text == "🎰 Колесо фортуны")
async def spin_button_handler(message: types.Message):
    user = get_user(message.from_user.id)
    if not user["verified"] or not user["personality_ready"]:
        await message.answer("Сначала заверши регистрацию через /start.")
        return

    today = datetime.now().date().isoformat()
    has_free = user.get("last_free_spin") != today

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎁 Бесплатно (1/день)" if has_free else "⏳ Завтра",
            callback_data="spin_free" if has_free else "spin_no"
        )],
        [InlineKeyboardButton(text="💎 Крутить за 20⭐", callback_data="spin_paid")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="spin_back")]
    ])

    await message.answer(
        f"🎰 **Колесо фортуны**\n\n"
        f"{'🎁 У тебя есть **бесплатное** вращение сегодня!' if has_free else '⏳ Бесплатное вращение будет завтра.'}\n"
        "💎 Платное вращение — **20⭐** (≈25 ₽)\n\n"
        "🔥 **Что можно выиграть:**\n"
        "• 10–50 сообщений\n"
        "• 100–250 XP\n"
        "• Интим-сцены\n"
        "• 🎁 PRO на 5 дней\n"
        "• ✨ SUPER PRO на 3 дня\n\n"
        "Выбери вариант:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data == "spin_free")
async def spin_free(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    today = datetime.now().date().isoformat()
    if user.get("last_free_spin") == today:
        await call.answer("⏳ Ты уже крутил сегодня! Завтра будет новое бесплатное вращение.", show_alert=True)
        return
    user["last_free_spin"] = today
    save_data(user_data)
    await call.message.delete()
    await spin_result(call.message, user, free=True)
    await call.answer()

@dp.callback_query(lambda c: c.data == "spin_paid")
async def spin_paid(call: types.CallbackQuery):
    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="🎰 Колесо фортуны",
            description="Платное вращение — 20⭐. Удачи!",
            payload="spin_paid_20",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Прокрутка", amount=20)]
        )
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")
        await call.answer()

@dp.callback_query(lambda c: c.data == "spin_no")
async def spin_no(call: types.CallbackQuery):
    await call.answer("⏳ Бесплатное вращение будет доступно завтра!", show_alert=True)

@dp.callback_query(lambda c: c.data == "spin_back")
async def spin_back(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await call.message.delete()
    await send_main_menu(call.message.chat.id, user)
    await call.answer()

async def spin_result(message: types.Message, user, free=False):
    prizes = [
        {"name": "😢 Ничего", "value": 0, "type": "nothing", "weight": 18},
        {"name": "10 сообщений", "value": 10, "type": "messages", "weight": 14},
        {"name": "15 сообщений", "value": 15, "type": "messages", "weight": 10},
        {"name": "20 сообщений", "value": 20, "type": "messages", "weight": 8},
        {"name": "100 XP", "value": 100, "type": "xp", "weight": 14},
        {"name": "150 XP", "value": 150, "type": "xp", "weight": 8},
        {"name": "250 XP", "value": 250, "type": "xp", "weight": 4},
        {"name": "1 интим-сцена 🔥", "value": 1, "type": "sex_scene", "weight": 10},
        {"name": "2 интим-сцены 🔥🔥", "value": 2, "type": "sex_scene", "weight": 3},
        {"name": "🎁 PRO на 5 дней", "value": 5, "type": "subscription_pro", "weight": 1.5},
        {"name": "✨ SUPER PRO на 3 дня", "value": 3, "type": "subscription_super", "weight": 0.5},
        {"name": "🎉 50 сообщений (ДЖЕКПОТ!)", "value": 50, "type": "messages", "weight": 1},
    ]

    weighted = []
    for p in prizes:
        weighted.extend([p] * int(p["weight"] * 10))
    chosen = random.choice(weighted)

    msg = await message.answer("🎰 Крутим...")
    for i in range(3):
        await asyncio.sleep(0.5)
        fake = random.choice(prizes)
        await msg.edit_text(f"🎰 Почти выпало: {fake['name']}")
    await asyncio.sleep(0.8)
    await msg.delete()

    result_text = ""
    if chosen["type"] == "messages":
        user["purchased_messages"] = user.get("purchased_messages", 0) + chosen["value"]
        result_text = f"📨 **+{chosen['value']} сообщений**"
    elif chosen["type"] == "xp":
        user["xp"] = user.get("xp", 0) + chosen["value"]
        result_text = f"⭐ **+{chosen['value']} XP**"
    elif chosen["type"] == "sex_scene":
        user["sex_scenes"] = user.get("sex_scenes", 0) + chosen["value"]
        result_text = f"🔥 **+{chosen['value']} интим-сцена**" + ("ы" if chosen["value"] > 1 else "")
    elif chosen["type"] == "subscription_pro":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=5)).isoformat()
        user["subscription"]["level"] = "pro"
        user["free_sex_scenes_pro"] = 4
        user["free_sex_scenes_super"] = 0
        user["daily_messages"] = 50
        user["last_daily_reset"] = datetime.now().isoformat()
        result_text = "🎁 **PRO подписка на 5 дней!**\n🔥 50 сообщений/день, стили Страстный и Магнетический, 4 интим-сцены!"
    elif chosen["type"] == "subscription_super":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=3)).isoformat()
        user["subscription"]["level"] = "super_pro"
        user["free_sex_scenes_super"] = 8
        user["free_sex_scenes_pro"] = 0
        user["daily_messages"] = 100
        user["last_daily_reset"] = datetime.now().isoformat()
        result_text = "✨ **SUPER PRO на 3 дня!**\n👑 100 сообщений/день, все стили, 8 интим-сцен, реакции!"
    else:
        result_text = "😢 **Ничего... В следующий раз повезёт!**"

    save_data(user_data)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Крутить ещё за 20⭐", callback_data="spin_paid")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="spin_back")]
    ])

    await message.answer(
        f"🎰 **Результат!**\n\n"
        f"Ты выиграл: {result_text}\n"
        f"{'🎁 Бесплатное вращение' if free else '💎 Платное вращение'}\n\n"
        f"{'⏳ Завтра будет новое бесплатное вращение!' if free else 'Удачи в следующий раз!'}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    # ============================================================
#  КОЛБЭКИ (продолжение)
# ============================================================
@dp.callback_query(lambda c: c.data == "agreement_accept")
async def agreement_accept(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["agreement_accepted"] = True
    save_data(user_data)
    await call.message.delete()
    await call.message.answer("✅ Соглашение принято!")
    await start_cmd(call.message)
    await call.answer()

@dp.callback_query(lambda c: c.data == "agreement_decline")
async def agreement_decline(call: types.CallbackQuery):
    await call.message.edit_text("❌ Без соглашения бот не работает.")
    await call.answer()

@dp.callback_query(lambda c: c.data == "age_yes")
async def age_yes(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["verified"] = True
    save_data(user_data)
    await call.message.edit_text("✅ Возраст подтверждён.")
    await start_cmd(call.message)
    await call.answer()

@dp.callback_query(lambda c: c.data == "age_no")
async def age_no(call: types.CallbackQuery):
    await call.message.edit_text("🚫 Доступ запрещён. Бот только для 18+.")
    await call.answer()

# ============================================================
#  ГЛАВНОЕ МЕНЮ И ПРОФИЛЬ
# ============================================================
@dp.message(lambda m: m.text == "📋 Главное меню")
async def main_menu_reply(message: types.Message):
    await message.delete()
    user = get_user(message.from_user.id)
    if not user["personality_ready"]:
        await message.answer("Сначала создай персонажа через /start", reply_markup=full_kb)
        return
    await send_main_menu(message.chat.id, user)

@dp.message(lambda m: m.text == "👤 Мой профиль")
async def profile_reply(message: types.Message):
    await message.delete()
    user = get_user(message.from_user.id)
    if not user["personality_ready"]:
        await ask_create_personality(message)
        return
    await show_profile(message, user)

@dp.message(lambda m: m.text == "📢 Наш канал")
async def channel_reply(message: types.Message):
    await message.delete()
    await message.answer("📢 **Наш канал:**\nПодписывайся, чтобы быть в курсе новостей и обновлений!",
                         reply_markup=channel_inline_kb, parse_mode="Markdown")

# ============================================================
#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ОБРАБОТЧИКОВ
# ============================================================
def get_text(user, key, **kwargs):
    lang = user.get("lang", "ru")
    text = TEXTS.get(lang, TEXTS["ru"]).get(key, TEXTS["ru"][key])
    if kwargs:
        text = text.format(**kwargs)
    return text

async def send_main_menu(chat_id, user):
    if user.get("last_menu_message_id"):
        try: await bot.delete_message(chat_id, user["last_menu_message_id"])
        except: pass

    if user.get("gender") is None:
        user["gender"] = "female"
    if user.get("world") is None:
        user["world"] = "realism"
    save_data(user_data)

    level = get_subscription_level(user)
    badge = ""
    if level == "pro": badge = "🔥 PRO"
    elif level == "super_pro": badge = "✨ *SUPER PRO* ✨"

    gender_name = GENDERS[user['gender']]['name']
    world_name = WORLD_NAMES[user['world']]
    current_style = get_display_style(user)
    style_label = STYLES[current_style]['label']

    available = get_available_messages(user)
    balance_text = f"\nОсталось сообщений: {available}" if has_purchased_something(user) else "\nУ вас есть бесплатные сообщения для старта"
    xp_badge = get_xp_badge(user)
    multiplier_text = ""
    sub_level = get_subscription_level(user)
    if sub_level == "pro":
        multiplier_text = "Бонус XP: x1.8"
    elif sub_level == "super_pro":
        multiplier_text = "Бонус XP: x2.5"

    menu_text = (
        f"{badge}\n\n"
        f"Текущий собеседник: {gender_name} из {world_name}\n"
        f"Стиль: {style_label}\n"
        f"{balance_text}\n"
        f"{xp_badge}\n"
        f"{multiplier_text}\n\n"
        f"💬 Напиши персонажу...\n"
        f"✨ Или выбери действие внизу."
    )

    try:
        if MAIN_MENU_IMAGE_URL and MAIN_MENU_IMAGE_URL.startswith("http"):
            msg = await bot.send_photo(chat_id, photo=MAIN_MENU_IMAGE_URL, caption=menu_text,
                                       reply_markup=get_main_menu_keyboard(user), parse_mode="Markdown")
        else:
            msg = await bot.send_message(chat_id, menu_text, reply_markup=get_main_menu_keyboard(user), parse_mode="Markdown")
    except:
        msg = await bot.send_message(chat_id, menu_text, reply_markup=get_main_menu_keyboard(user), parse_mode="Markdown")

    await bot.send_message(chat_id, "🔁 Клавиатура обновлена", reply_markup=full_kb)
    user["last_menu_message_id"] = msg.message_id
    save_data(user_data)
    return msg

async def show_profile(msg, user):
    level = get_subscription_level(user)
    if level == "pro": sub_status = "🔥 PRO активна (50 сообщений/день, память 60 сообщений)"
    elif level == "super_pro": sub_status = "✨ SUPER PRO активна (100 сообщений/день, память 100 сообщений)"
    else: sub_status = "❌ неактивна (память 30 сообщений)"
    expiry = user["subscription"]["expires_at"]
    if expiry:
        expiry = datetime.fromisoformat(expiry).strftime("%d.%m.%Y %H:%M")
        expiry_line = f"Окончание подписки: {expiry}"
    else:
        expiry_line = "Окончание подписки: неактивна"

    styles_text = ""
    for key, style in STYLES.items():
        if key in PREMIUM_STYLES:
            if key == "passionate":
                if not has_active_subscription(user) or get_subscription_level(user) not in ["pro","super_pro"]:
                    styles_text += f"{style['emoji']} {style['label']} 🔒\n"; continue
            elif key == "magnetic":
                if not has_active_subscription(user) or get_subscription_level(user) not in ["pro","super_pro"]:
                    styles_text += f"{style['emoji']} {style['label']} 🔒\n"; continue
            elif key in ["vulgar","seduction"]:
                if not has_active_subscription(user) or get_subscription_level(user) != "super_pro":
                    styles_text += f"{style['emoji']} {style['label']} 🔒\n"; continue
        styles_text += f"{style['emoji']} {style['label']}\n"

    available = get_available_messages(user)
    balance_line = f"Доступно сообщений: {available}" if has_purchased_something(user) else "У вас есть бесплатные сообщения для старта"
    xp_badge = get_xp_badge(user)
    multiplier_text = ""
    sub_level = get_subscription_level(user)
    if sub_level == "pro":
        multiplier_text = "Бонус XP: x1.8"
    elif sub_level == "super_pro":
        multiplier_text = "Бонус XP: x2.5"

    free_pro = user.get("free_sex_scenes_pro", 0)
    free_super = user.get("free_sex_scenes_super", 0)
    bought = user.get("sex_scenes", 0)
    total_sex_scenes = free_pro + free_super + bought
    sex_scenes_display = f"Всего интим-сцен: {total_sex_scenes}"

    caption = (f"{balance_line}\n"
               f"Подписка: {sub_status}\n"
               f"{expiry_line}\n\n"
               f"{xp_badge}\n"
               f"{multiplier_text}\n"
               f"{sex_scenes_display}\n\n"
               f"Доступные стили:\n{styles_text}")

    chat_id = msg.chat.id
    old_msg_id = msg.message_id
    if level == "super_pro" and SUPER_PRO_GIF_URL:
        await bot.send_animation(chat_id, animation=SUPER_PRO_GIF_URL, caption=caption,
                                 reply_markup=get_profile_keyboard(user), parse_mode="Markdown")
    elif level == "pro" and PRO_GIF_URL:
        await bot.send_animation(chat_id, animation=PRO_GIF_URL, caption=caption,
                                 reply_markup=get_profile_keyboard(user), parse_mode="Markdown")
    else:
        await bot.send_message(chat_id, caption, reply_markup=get_profile_keyboard(user), parse_mode="Markdown")
    try: await bot.delete_message(chat_id, old_msg_id)
    except: pass

async def ask_create_personality(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌟 Создать персонажа", callback_data="create_personality")]
    ])
    await message.answer("👤 **Чтобы открыть профиль или купить что‑то, сначала создай своего персонажа!**\n\n"
                         "Нажми кнопку ниже, чтобы выбрать мир, пол и стиль собеседника.",
                         reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(lambda c: c.data == "create_personality")
async def create_personality_callback(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["personality_ready"] = False
    user["history"] = []
    save_data(user_data)
    await call.message.delete()
    await call.message.answer("🌟 **Создай своего идеального собеседника!**\n\nСначала выбери **мир**, в котором он/она живёт:",
                              reply_markup=world_kb, parse_mode="Markdown")
    await call.answer()

@dp.message(Command("switch_personality"))
async def switch_personality_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if get_subscription_level(user) != "super_pro":
        await message.answer("❌ Команда /switch_personality доступна только для подписчиков SUPER PRO.")
        return
    user["switching_personality"] = True
    save_data(user_data)
    await message.answer("🔄 **Смена персонажа (история сохраняется)**\n\nВыбери **мир**:", reply_markup=world_kb, parse_mode="Markdown")

# ============================================================
#  КОЛБЭКИ ВЫБОРА ПЕРСОНАЖА
# ============================================================
@dp.callback_query(lambda c: c.data == "main_change")
async def main_change(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user["personality_ready"] = False
    user["history"] = []
    save_data(user_data)
    await call.message.delete()
    await call.message.answer("🔄 **Создаем нового собеседника!**\n\nВыбери **мир**:",
                              reply_markup=world_kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("world_"))
async def choose_world(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    world = call.data.split("_")[1]
    if user.get("switching_personality", False):
        user["world"] = world
        save_data(user_data)
        await call.message.edit_text("🌍 Мир обновлён! Теперь выбери свой пол:", reply_markup=user_gender_kb, parse_mode="Markdown")
    else:
        user["world"] = world
        save_data(user_data)
        await call.message.edit_text("🌍 Мир выбран! Теперь выбери свой пол:", reply_markup=user_gender_kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("user_gender_"))
async def choose_user_gender(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    user_gender = call.data.split("_")[2]
    user["user_gender"] = user_gender
    if user_gender == "male":
        user["gender"] = "female"
    else:
        user["gender"] = "male"
    save_data(user_data)
    style_kb = get_style_kb(user)
    await call.message.edit_text(
        "👤 Отлично! Теперь выбери **стиль** персонажа:",
        reply_markup=style_kb,
        parse_mode="Markdown"
    )
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("style_"))
async def choose_style(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    style_key = call.data.split("_")[1]
    if style_key in PREMIUM_STYLES and not has_active_subscription(user):
        await call.answer("❌ Стиль доступен только по подписке", show_alert=True)
        return
    user["style"] = style_key
    save_data(user_data)

    if user.get("switching_personality", False):
        await call.message.edit_text("🎬 Стиль обновлён! Теперь выбери сцену для общения:",
                                     reply_markup=scene_kb, parse_mode="Markdown")
    else:
        user["personality_ready"] = True
        save_data(user_data)
        await call.message.delete()
        await call.message.answer("🎬 Теперь выбери сцену для общения:\n\n📱 Переписка в телефоне — классический формат.\n👫 Реальная встреча — живое общение лицом к лицу.",
                                  reply_markup=scene_kb, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("scene_"))
async def choose_scene(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    scene = call.data.split("_")[1]
    user["scene"] = scene
    save_data(user_data)

    if user.get("switching_personality", False):
        user["switching_personality"] = False
        save_data(user_data)
        await call.message.delete()
        await send_main_menu(call.message.chat.id, user)
        await call.answer("✅ Персонаж обновлён! История сохранена.")
    else:
        await call.message.delete()
        await send_main_menu(call.message.chat.id, user)
    await call.answer()

@dp.callback_query(lambda c: c.data.startswith("fix_style_"))
async def fix_style_callback(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    style = call.data.split("_")[2]
    if style in BASE_STYLE_KEYS:
        user["style"] = style
        save_data(user_data)
        await call.message.edit_text(f"✅ Стиль изменён на: {STYLES[style]['label']}")
        await call.answer()
        await send_main_menu(call.message.chat.id, user)
    else:
        await call.answer("❌ Недопустимый стиль", show_alert=True)

# ============================================================
#  ПОДПИСКИ, ПАКЕТЫ, СЕКС-СЦЕНЫ
# ============================================================
@dp.callback_query(lambda c: c.data == "profile_subs")
async def profile_subs(call: types.CallbackQuery):
    await call.answer()
    user = get_user(call.from_user.id)
    if not user["personality_ready"]:
        await call.answer("Сначала создай персонажа!", show_alert=True)
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 PRO — 250 ⭐/мес", callback_data="subscribe_pro")],
        [InlineKeyboardButton(text="✨ SUPER PRO ✨ — 450 ⭐/мес", callback_data="subscribe_super")],
        [InlineKeyboardButton(text="⬆️ Апгрейд до SUPER PRO (245⭐)", callback_data="upgrade_to_super")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile")]
    ])
    text = ("👑 Подписки Role Duel\n\n"
            "🔥 PRO (250⭐/мес)\n"
            "• 50 сообщений в день\n"
            "• Стили: ❤️‍🔥 Страстный, ✨ Магнетический\n"
            "• Приоритетная обработка\n"
            "• Память: 60 сообщений\n"
            "• 4 бесплатные интим-сцены\n"
            "• Бейдж PRO\n"
            "• Бонус XP: x1.8\n\n"
            "✨ SUPER PRO ✨ (450⭐/мес)\n"
            "• 100 сообщений в день\n"
            "• Стили: ❤️‍🔥 Страстный, ✨ Магнетический, 💢 Грубый 18+, 🌹 Соблазн 18+\n"
            "• Максимальная приоритетная обработка\n"
            "• Кастомные реакции\n"
            "• Смена стиля без потери истории (/switch_style)\n"
            "• Бейдж SUPER PRO\n"
            "• Ранний доступ к новым функциям\n"
            "• Память: 100 сообщений\n"
            "• 8 бесплатных интим-сцен\n"
            "• Бонус XP: x2.5\n"
            "• 🎭 **Создание своего уникального персонажа!**\n\n"
            "⬆️ Апгрейд до SUPER PRO (245⭐) — повысьте PRO до SUPER PRO на оставшийся срок.\n\n"
            "⚠️ Подписки НЕ продлеваются автоматически.\n\n"
            "Выбери подписку:")
    await call.message.answer(text, reply_markup=keyboard)

@dp.callback_query(lambda c: c.data == "profile_packs")
async def profile_packs(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if not user["personality_ready"]:
        await call.answer("Сначала создай персонажа!", show_alert=True)
        return
    if has_active_subscription(user):
        await call.answer("❌ При активной подписке покупка пакетов сообщений недоступна.", show_alert=True)
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="30 сообщений — 30 ⭐", callback_data="pack_30")],
        [InlineKeyboardButton(text="100 сообщений — 80 ⭐", callback_data="pack_100")],
        [InlineKeyboardButton(text="300 сообщений — 200 ⭐", callback_data="pack_300")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile")]
    ])
    await call.message.answer("📦 **Купить пакет сообщений**\n\nВыбери пакет:", reply_markup=keyboard, parse_mode="Markdown")
    await call.answer()

@dp.callback_query(lambda c: c.data == "buy_sex_scene")
async def buy_sex_scene(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if not user["personality_ready"]:
        await call.answer("Сначала создай персонажа!", show_alert=True)
        return
    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="Интим-сцена",
            description="Мгновенная откровенная сцена с вашим персонажем. Детальное описание.",
            payload="sex_scene",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Интим-сцена", amount=45)]
        )
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")

@dp.callback_query(lambda c: c.data == "profile_back")
async def profile_back(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await call.message.delete()
    await send_main_menu(call.message.chat.id, user)
    await call.answer()

@dp.callback_query(lambda c: c.data == "back_to_profile")
async def back_to_profile(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await call.message.delete()
    await show_profile(call.message, user)
    await call.answer()

# ============================================================
#  ОБРАБОТЧИКИ ПЛАТЕЖЕЙ
# ============================================================
@dp.callback_query(lambda c: c.data == "subscribe_pro")
async def subscribe_pro(call: types.CallbackQuery):
    try:
        user = get_user(call.from_user.id)
        if has_active_subscription(user):
            await call.answer("❌ У вас уже есть подписка.", show_alert=True)
            return
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="PRO подписка на месяц",
            description="50 сообщений/день, память 60 сообщений, стили Страстный и Магнетический, 4 бесплатные интим-сцены.",
            payload="subscribe_pro",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="PRO месяц", amount=250)]
        )
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")

@dp.callback_query(lambda c: c.data == "subscribe_super")
async def subscribe_super(call: types.CallbackQuery):
    try:
        user = get_user(call.from_user.id)
        if has_active_subscription(user):
            await call.answer("❌ У вас уже есть подписка.", show_alert=True)
            return
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="SUPER PRO подписка на месяц",
            description="100 сообщений/день, память 100 сообщений, все стили, 8 бесплатных интим-сцен.",
            payload="subscribe_super",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="SUPER PRO месяц", amount=450)]
        )
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")

@dp.callback_query(lambda c: c.data == "upgrade_to_super")
async def upgrade_to_super(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if get_subscription_level(user) != "pro":
        await call.answer("❌ Только для PRO.", show_alert=True)
        return
    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="Апгрейд до SUPER PRO",
            description="Повысьте PRO до SUPER PRO на оставшийся срок. 245⭐.",
            payload="upgrade_to_super",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Апгрейд", amount=245)]
        )
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")

@dp.callback_query(lambda c: c.data.startswith("pack_"))
async def buy_pack(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if has_active_subscription(user):
        await call.answer("❌ При подписке пакеты недоступны.", show_alert=True)
        return
    period = call.data.split("_")[1]
    pack_map = {"30": 30, "100": 100, "300": 300}
    price_map = {"30": 30, "100": 80, "300": 200}
    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title=f"Пакет {pack_map[period]} сообщений",
            description=f"{pack_map[period]} сообщений за {price_map[period]}⭐",
            payload=f"pack_{period}",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label=f"{pack_map[period]} сообщ.", amount=price_map[period])]
        )
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")

@dp.pre_checkout_query()
async def pre_checkout(query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(lambda m: m.successful_payment)
async def payment_success(message: types.Message):
    user = get_user(message.from_user.id)
    payload = message.successful_payment.invoice_payload

    if payload.startswith("pack_"):
        period = payload.split("_")[1]
        pack_map = {"30": 30, "100": 100, "300": 300}
        user["purchased_messages"] += pack_map[period]
        save_data(user_data)
        await message.answer(f"✅ Куплено {pack_map[period]} сообщений!")
    elif payload == "subscribe_pro":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "pro"
        user["free_sex_scenes_pro"] = 4
        user["daily_messages"] = 50
        user["last_daily_reset"] = datetime.now().isoformat()
        save_data(user_data)
        await message.answer("✅ PRO подписка активирована на месяц!")
    elif payload == "subscribe_super":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "super_pro"
        user["free_sex_scenes_super"] = 8
        user["daily_messages"] = 100
        user["last_daily_reset"] = datetime.now().isoformat()
        save_data(user_data)
        await message.answer("✅ SUPER PRO подписка активирована на месяц!")
    elif payload == "upgrade_to_super":
        if has_active_subscription(user) and get_subscription_level(user) == "pro":
            old_expiry = user["subscription"]["expires_at"]
            user["subscription"]["level"] = "super_pro"
            user["free_sex_scenes_super"] = 8
            user["free_sex_scenes_pro"] = 0
            user["daily_messages"] = 100
            save_data(user_data)
            await message.answer(f"✅ Апгрейд до SUPER PRO выполнен до {old_expiry}!")
    elif payload == "sex_scene":
        user["sex_scenes"] += 1
        save_data(user_data)
        await message.answer("✅ Куплена интим-сцена!")
    elif payload == "spin_paid_20":
        await spin_result(message, user, free=False)

# ============================================================
#  КОЛЕСО ФОРТУНЫ
# ============================================================
@dp.message(lambda m: m.text == "🎰 Колесо фортуны")
async def spin_button_handler(message: types.Message):
    user = get_user(message.from_user.id)
    if not user["verified"] or not user["personality_ready"]:
        await message.answer("Сначала заверши регистрацию через /start.")
        return

    today = datetime.now().date().isoformat()
    has_free = user.get("last_free_spin") != today

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎁 Бесплатно (1/день)" if has_free else "⏳ Завтра",
            callback_data="spin_free" if has_free else "spin_no"
        )],
        [InlineKeyboardButton(text="💎 Крутить за 20⭐", callback_data="spin_paid")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="spin_back")]
    ])

    await message.answer(
        f"🎰 **Колесо фортуны**\n\n"
        f"{'🎁 У тебя есть **бесплатное** вращение сегодня!' if has_free else '⏳ Бесплатное вращение будет завтра.'}\n"
        "💎 Платное вращение — **20⭐**\n\n"
        "🔥 **Что можно выиграть:**\n"
        "• 10–50 сообщений\n"
        "• 100–250 XP\n"
        "• Интим-сцены\n"
        "• 🎁 PRO на 5 дней\n"
        "• ✨ SUPER PRO на 3 дня\n\n"
        "Выбери вариант:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data == "spin_free")
async def spin_free(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    today = datetime.now().date().isoformat()
    if user.get("last_free_spin") == today:
        await call.answer("⏳ Ты уже крутил сегодня!", show_alert=True)
        return
    user["last_free_spin"] = today
    save_data(user_data)
    await call.message.delete()
    await spin_result(call.message, user, free=True)
    await call.answer()

@dp.callback_query(lambda c: c.data == "spin_paid")
async def spin_paid(call: types.CallbackQuery):
    try:
        await bot.send_invoice(
            chat_id=call.message.chat.id,
            title="🎰 Колесо фортуны",
            description="Платное вращение — 20⭐. Удачи!",
            payload="spin_paid_20",
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice(label="Прокрутка", amount=20)]
        )
        await call.answer()
    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка: {e}")
        await call.answer()

@dp.callback_query(lambda c: c.data == "spin_no")
async def spin_no(call: types.CallbackQuery):
    await call.answer("⏳ Бесплатное вращение завтра!", show_alert=True)

@dp.callback_query(lambda c: c.data == "spin_back")
async def spin_back(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    await call.message.delete()
    await send_main_menu(call.message.chat.id, user)
    await call.answer()

async def spin_result(message: types.Message, user, free=False):
    prizes = [
        {"name": "😢 Ничего", "value": 0, "type": "nothing", "weight": 18},
        {"name": "10 сообщений", "value": 10, "type": "messages", "weight": 14},
        {"name": "15 сообщений", "value": 15, "type": "messages", "weight": 10},
        {"name": "20 сообщений", "value": 20, "type": "messages", "weight": 8},
        {"name": "100 XP", "value": 100, "type": "xp", "weight": 14},
        {"name": "150 XP", "value": 150, "type": "xp", "weight": 8},
        {"name": "250 XP", "value": 250, "type": "xp", "weight": 4},
        {"name": "1 интим-сцена 🔥", "value": 1, "type": "sex_scene", "weight": 10},
        {"name": "2 интим-сцены 🔥🔥", "value": 2, "type": "sex_scene", "weight": 3},
        {"name": "🎁 PRO на 5 дней", "value": 5, "type": "subscription_pro", "weight": 1.5},
        {"name": "✨ SUPER PRO на 3 дня", "value": 3, "type": "subscription_super", "weight": 0.5},
        {"name": "🎉 50 сообщений (ДЖЕКПОТ!)", "value": 50, "type": "messages", "weight": 1},
    ]

    weighted = []
    for p in prizes:
        weighted.extend([p] * int(p["weight"] * 10))
    chosen = random.choice(weighted)

    msg = await message.answer("🎰 Крутим...")
    for i in range(3):
        await asyncio.sleep(0.5)
        fake = random.choice(prizes)
        await msg.edit_text(f"🎰 Почти выпало: {fake['name']}")
    await asyncio.sleep(0.8)
    await msg.delete()

    result_text = ""
    if chosen["type"] == "messages":
        user["purchased_messages"] += chosen["value"]
        result_text = f"📨 **+{chosen['value']} сообщений**"
    elif chosen["type"] == "xp":
        user["xp"] += chosen["value"]
        result_text = f"⭐ **+{chosen['value']} XP**"
    elif chosen["type"] == "sex_scene":
        user["sex_scenes"] += chosen["value"]
        result_text = f"🔥 **+{chosen['value']} интим-сцен**" + ("ы" if chosen["value"] > 1 else "")
    elif chosen["type"] == "subscription_pro":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=5)).isoformat()
        user["subscription"]["level"] = "pro"
        user["free_sex_scenes_pro"] = 4
        user["daily_messages"] = 50
        user["last_daily_reset"] = datetime.now().isoformat()
        result_text = "🎁 **PRO подписка на 5 дней!**\n🔥 50 сообщений/день, стили Страстный и Магнетический, 4 интим-сцены!"
    elif chosen["type"] == "subscription_super":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=3)).isoformat()
        user["subscription"]["level"] = "super_pro"
        user["free_sex_scenes_super"] = 8
        user["daily_messages"] = 100
        user["last_daily_reset"] = datetime.now().isoformat()
        result_text = "✨ **SUPER PRO на 3 дня!**\n👑 100 сообщений/день, все стили, 8 интим-сцен!"
    else:
        result_text = "😢 **Ничего... В следующий раз повезёт!**"

    save_data(user_data)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💎 Крутить ещё за 20⭐", callback_data="spin_paid")],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="spin_back")]
    ])

    await message.answer(
        f"🎰 **Результат!**\n\n"
        f"Ты выиграл: {result_text}\n"
        f"{'🎁 Бесплатное вращение' if free else '💎 Платное вращение'}\n\n"
        f"{'⏳ Завтра будет новое бесплатное вращение!' if free else 'Удачи в следующий раз!'}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# ============================================================
#  РЕФЕРАЛЬНАЯ СИСТЕМА
# ============================================================
@dp.callback_query(lambda c: c.data == "referral_menu")
async def referral_menu(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if not user["personality_ready"]:
        await call.answer("Сначала создай персонажа!", show_alert=True)
        return

    if not user.get("referral_code"):
        user["referral_code"] = str(call.from_user.id)
        save_data(user_data)

    link = f"https://t.me/role_duel_bot?start=ref_{user['referral_code']}"
    await call.message.answer(
        f"👥 **Твоя реферальная ссылка:**\n`{link}`\n\n"
        "🎁 **Бонусы:**\n"
        "• Ты получишь **+10 сообщений** и **+1 интим-сцену** за каждого друга.\n"
        "• Твой друг получит **+5 бесплатных сообщений** за регистрацию!\n\n"
        "💡 Делитесь ссылкой с друзьями и получайте бонусы!",
        parse_mode="Markdown"
    )
    await call.answer()

# ============================================================
#  КОМАНДА /switch_style
# ============================================================
@dp.message(Command("switch_style"))
async def switch_style_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    if get_subscription_level(user) != "super_pro":
        await message.answer("❌ Только для SUPER PRO.")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for key, style in STYLES.items():
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=f"{style['emoji']} {style['label']}", callback_data=f"switch_{key}")])
    await message.answer("🔄 **Выбери новый стиль:**\n\nИстория диалога сохранится.", reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(lambda c: c.data.startswith("switch_"))
async def switch_style(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    style = call.data.split("_")[1]
    if style not in STYLES:
        await call.answer("❌ Стиль недоступен", show_alert=True)
        return
    user["style"] = style
    save_data(user_data)
    await call.message.edit_text(f"✅ Стиль изменён на: {STYLES[style]['label']}")
    await call.answer()

# ============================================================
#  АДМИН-КОМАНДЫ
# ============================================================
@dp.message(Command("tehwork"))
async def maintenance_cmd(message: types.Message):
    global maintenance_mode
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет прав.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer(f"Текущий режим: {'ВКЛ' if maintenance_mode else 'ВЫКЛ'}")
        return
    if args[1].lower() == "on":
        maintenance_mode = True
        await message.answer("🛠️ Техобслуживание ВКЛ.")
    elif args[1].lower() == "off":
        maintenance_mode = False
        await message.answer("✅ Техобслуживание ВЫКЛ.")
    else:
        await message.answer("❌ on или off")

@dp.message(Command("reset_me"))
async def reset_me_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет прав.")
        return
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        await message.answer("❌ Тебя нет в базе.")
        return
    del user_data[user_id]
    save_data(user_data)
    await message.answer("✅ Твои данные сброшены! Напиши /start заново.")

@dp.message(Command("grant"))
async def grant_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет прав.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("/grant @username — SUPER PRO\n/grant @username pro — PRO\n/grant @username sex N — сцены")
        return
    target = args[1]
    user_id = None
    if target.startswith("@"):
        try:
            user_id = (await bot.get_chat(target)).id
        except:
            await message.answer("❌ Не найден.")
            return
    else:
        try:
            user_id = int(target)
        except:
            await message.answer("❌ Неверный ID.")
            return
    user = get_user(user_id)
    if len(args) >= 3 and args[2].lower() == "pro":
        user["subscription"]["active"] = True
        user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
        user["subscription"]["level"] = "pro"
        user["daily_messages"] = 50
        user["free_sex_scenes_pro"] = 4
        save_data(user_data)
        await message.answer(f"✅ {target} выдана PRO.")
        return
    if len(args) >= 3 and args[2].lower() == "sex":
        count = int(args[3]) if len(args) >= 4 else 1
        user["sex_scenes"] += count
        save_data(user_data)
        await message.answer(f"✅ {target} выдано {count} интим-сцен.")
        return
    user["subscription"]["active"] = True
    user["subscription"]["expires_at"] = (datetime.now() + timedelta(days=30)).isoformat()
    user["subscription"]["level"] = "super_pro"
    user["daily_messages"] = 100
    user["free_sex_scenes_super"] = 8
    save_data(user_data)
    await message.answer(f"✅ {target} выдана SUPER PRO.")

@dp.message(Command("revoke_subscription"))
async def revoke_subscription_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Нет прав.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("/revoke_subscription @username")
        return
    target = args[1]
    user_id = None
    if target.startswith("@"):
        try:
            user_id = (await bot.get_chat(target)).id
        except:
            await message.answer("❌ Не найден.")
            return
    else:
        try:
            user_id = int(target)
        except:
            await message.answer("❌ Неверный ID.")
            return
    user = get_user(user_id)
    if not has_active_subscription(user):
        await message.answer(f"❌ У {target} нет подписки.")
        return
    user["subscription"]["active"] = False
    user["subscription"]["expires_at"] = None
    user["subscription"]["level"] = None
    user["free_sex_scenes_pro"] = 0
    user["free_sex_scenes_super"] = 0
    save_data(user_data)
    await message.answer(f"✅ Подписка {target} отозвана.")
    # ============================================================
#  СОЗДАНИЕ ПЕРСОНАЖА (ДЛЯ SUPER PRO)
# ============================================================
@dp.callback_query(lambda c: c.data == "create_character_locked")
async def create_character_locked(call: types.CallbackQuery):
    await call.answer(
        "🔒 Создание своего персонажа доступно только с подпиской SUPER PRO!\n"
        "Оформите SUPER PRO в разделе «Мой профиль».",
        show_alert=True
    )

@dp.callback_query(lambda c: c.data == "create_character")
async def create_character(call: types.CallbackQuery):
    user = get_user(call.from_user.id)
    if get_subscription_level(user) != "super_pro":
        await call.answer("❌ Только для SUPER PRO!", show_alert=True)
        return
    await call.message.answer(
        "🎭 **Создай своего уникального персонажа!**\n\n"
        "Опиши любого персонажа — из аниме, фильмов, игр или придумай своего.\n"
        "Напиши его/её имя, характер, внешность, откуда он/она, любые детали.\n\n"
        "📝 *Пример:*\n"
        "«Эльфийка из мира Ведьмака — мудрая, сдержанная, с длинными серебряными волосами. "
        "Любит звёзды и долгие разговоры у костра. Живёт одна в лесу.»\n\n"
        "✏️ Напиши описание прямо сейчас — и я запомню его!",
        parse_mode="Markdown"
    )
    user["creating_character"] = True
    save_data(user_data)
    await call.answer()

@dp.message(Command("reset_character"))
async def reset_character_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    user["custom_character"] = None
    save_data(user_data)
    await message.answer("✅ Персонаж сброшен. Теперь используется стандартный собеседник.")

# ============================================================
#  КОМАНДА /intim (интим-сцена)
# ============================================================
@dp.message(Command("intim"))
async def intim_cmd(message: types.Message):
    user = get_user(message.from_user.id)
    level = get_intimacy_level(user)
    if level < 8:
        await message.answer(f"❌ Интим-сцены доступны только после 8 уровня близости (у тебя {level}).")
        return
    if user.get("sex_scenes", 0) <= 0:
        await message.answer("❌ У тебя нет доступных интим-сцен. Купи в профиле за 45⭐.")
        return
    user["sex_scenes"] -= 1
    save_data(user_data)
    # Генерация сцены через ИИ (короткая заглушка)
    await message.answer("🌹 *Интим-сцена*\n\n(Здесь будет сгенерирован текст)", parse_mode="Markdown")

# ============================================================
#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================
def extract_reaction_from_answer(text):
    """Извлекает реакцию из скобок в конце ответа ИИ"""
    match = re.search(r'\(([^)]+)\)$', text)
    if not match:
        return None, text
    reaction_key = match.group(1).strip().lower()
    reaction_map = {
        "смех": "😂", "радость": "😊", "любовь": "❤️", "удивление": "😮",
        "грусть": "😔", "злость": "😡", "поддержка": "👍", "интрига": "😏",
        "флирт": "😉", "приветствие": "👋", "вопрос": "🤔"
    }
    reaction = reaction_map.get(reaction_key)
    clean_text = re.sub(r'\s*\([^)]+\)$', '', text).strip()
    return reaction, clean_text

def get_level_congratulation(level):
    if level == 2:
        return "🎉 Ты заметил(а), что между вами пробежала искра! Уровень сближения — 2. Теперь вы можете флиртовать."
    elif level == 3:
        return "💞 Вы стали ближе! Уровень 3. Теперь вы можете обниматься и делиться секретами."
    elif level == 4:
        return "🔥 Напряжение растёт! Уровень 4. Ты чувствуешь, что он/она хочет тебя."
    elif level == 5:
        return "💋 Уровень 5! Вы готовы к поцелую. Собеседник уже не скрывает своих чувств."
    elif level == 6:
        return "🌹 Уровень 6. Ты влюблён(а)! Теперь вы можете говорить о страсти."
    elif level == 7:
        return "💕 Уровень 7. Интимная близость уже близка. Собеседник открыто говорит о желании."
    elif level == 8:
        return "❤️‍🔥 Уровень 8! Вы признались друг другу в любви. Теперь вы — пара."
    elif level == 9:
        return "🔥 Уровень 9! Вы полностью открыты друг другу. Никаких тайн."
    elif level == 10:
        return "💖 Уровень 10! Вы — единое целое. Настоящая душевная близость."
    return ""

# ============================================================
#  ОСНОВНОЙ ОБРАБОТЧИК СООБЩЕНИЙ
# ============================================================
@dp.message()
async def handle_message(message: types.Message):
    global maintenance_mode
    user = get_user(message.from_user.id)

    # 1. Проверка, не создаёт ли пользователь персонажа
    if user.get("creating_character"):
        user["custom_character"] = message.text
        user["creating_character"] = False
        save_data(user_data)
        await message.answer(
            f"✅ **Персонаж создан!**\n\n"
            f"Теперь ты общаешься с:\n_{message.text}_\n\n"
            "Чтобы вернуться к стандартному персонажу, напиши /reset_character",
            parse_mode="Markdown"
        )
        return

    # 2. Приветствие после долгого отсутствия
    if user.get("last_activity"):
        try:
            last = datetime.fromisoformat(user["last_activity"])
            if (datetime.now() - last).days >= 1:
                gender = user.get("gender", "female")
                lang = user.get("lang", "ru")
                version = random.choice([1, 2])
                if gender == "female":
                    key = "welcome_back_female" if version == 1 else "welcome_back_female_2"
                else:
                    key = "welcome_back_male" if version == 1 else "welcome_back_male_2"
                await message.answer(get_text(user, key))
        except:
            pass

    # 3. Проверки: техобслуживание, регистрация, стиль
    if maintenance_mode and message.from_user.id not in ADMIN_IDS:
        await message.answer("🛠️ **Бот на техобслуживании**\nСледите за новостями: @duel_dev_channel", parse_mode="Markdown")
        return

    if not user["verified"] or not user["agreement_accepted"]:
        await message.answer("🔞 Сначала пройди регистрацию через /start")
        return
    if not user["personality_ready"]:
        await message.answer("Сначала создай персонажа через /start")
        return

    # 4. Игнорируем команды и кнопки
    if message.text.startswith("/"):
        return
    if message.text in ["📋 Главное меню", "👤 Мой профиль", "📢 Наш канал", "🎰 Колесо фортуны", "✏️ Редактировать (последнее сообщение)"]:
        return

    # 5. Проверка премиум-стиля (если подписка кончилась)
    if ensure_valid_style(user):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🪶 Нежный", callback_data="fix_style_warm")],
            [InlineKeyboardButton(text="🔥 Дерзкий", callback_data="fix_style_daring")],
            [InlineKeyboardButton(text="😊 Стеснительный", callback_data="fix_style_shy")],
        ])
        await message.answer(
            "⚠️ Твоя подписка закончилась, выбери бесплатный стиль:",
            reply_markup=keyboard
        )
        return

    # 6. Проверка сообщений
    available = get_available_messages(user)
    if available <= 0:
        await message.answer("😔 Сообщения кончились. Купи пакет или подписку.")
        action_buttons = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👑 Оформить подписку", callback_data="profile_subs")],
            [InlineKeyboardButton(text="📦 Купить пакеты", callback_data="profile_packs")]
        ])
        await message.answer(
            "📦 Купить пакет сообщений или оформить подписку:",
            reply_markup=action_buttons
        )
        return

    use_message(user)

    # 7. Обработка негатива и XP
    negative = contains_negative(message.text)
    base_xp = 5
    multiplier = 1.0
    sub_level = get_subscription_level(user)
    if sub_level == "pro":
        multiplier = 1.8
    elif sub_level == "super_pro":
        multiplier = 2.5

    if negative:
        xp_change = -10
        mood_change = -1
        user["negative_count"] = user.get("negative_count", 0) + 1
        if user["negative_count"] >= 5:
            user["xp"] = max(0, user.get("xp", 0) - 50)
            user["mood"] = max(-10, user.get("mood", 0) - 3)
            user["negative_count"] = 0
            save_data(user_data)
            await message.answer("💢 Ссора! Уровень близости снижен.", reply_markup=full_kb)
            user["history"].append({"role": "assistant", "content": "💢 Ссора!"})
            save_data(user_data)
            return
    else:
        xp_change = int(base_xp * multiplier + 0.5)
        mood_change = 0.5
        user["negative_count"] = max(0, user.get("negative_count", 0) - 1)

    user["xp"] = user.get("xp", 0) + xp_change
    user["mood"] = min(10, max(-10, user.get("mood", 0) + mood_change))
    if user["xp"] < 0:
        user["xp"] = 0

    # 8. Проверка уровня
    new_level = get_intimacy_level(user)
    old_level = user.get("last_level", 0)
    if new_level > old_level:
        user["last_level"] = new_level
        save_data(user_data)
        congrats = get_level_congratulation(new_level)
        if congrats:
            await message.answer(congrats, reply_markup=full_kb)
    elif new_level < old_level:
        user["last_level"] = new_level
        save_data(user_data)
        await message.answer(f"💔 Уровень сближения упал до {new_level}.", reply_markup=full_kb)

    # 9. Обновление локации
    new_loc = extract_location_from_text(message.text)
    if new_loc and new_loc != user.get("location"):
        user["location"] = new_loc
        save_data(user_data)

    save_data(user_data)

    # 10. Сохранение истории
    user["history"].append({"role": "user", "content": message.text})
    limit = get_history_limit(user)
    if len(user["history"]) > 10:
        user["history"] = user["history"][-10:]
    save_data(user_data)

    # 11. Отправка статуса "печатает"
    await bot.send_chat_action(message.chat.id, "typing")

    async def keep_typing():
        while True:
            await bot.send_chat_action(message.chat.id, "typing")
            await asyncio.sleep(4)
    typing_task = asyncio.create_task(keep_typing())

    # 12. Реакции (для SUPER PRO)
    if get_subscription_level(user) == "super_pro":
        reaction = get_reaction(message.text)
        if reaction:
            try:
                await bot.set_message_reaction(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    reaction=[{"type": "emoji", "emoji": reaction}]
                )
            except:
                pass

    # 13. Генерация ответа ИИ
    system_prompt = build_prompt(user)
    try:
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[{"role": "system", "content": system_prompt}] + user["history"],
            temperature=0.9,
            max_tokens=1000
        )
        answer = response.choices[0].message.content
    except Exception as e:
        if typing_task:
            typing_task.cancel()
        await message.answer(f"⚠️ Ошибка: {e}")
        return
    finally:
        if typing_task:
            typing_task.cancel()

    # 14. Извлечение реакции из ответа ИИ
    reaction, clean_answer = extract_reaction_from_answer(answer)

    user["history"].append({"role": "assistant", "content": clean_answer})
    if len(user["history"]) > limit:
        user["history"] = user["history"][-limit:]
    save_data(user_data)

    # 15. Отправка ответа
    sent_msg = await message.answer(clean_answer, reply_markup=full_kb)

    # 16. Реакция на сообщение пользователя (если есть)
    if reaction and get_subscription_level(user) == "super_pro":
        try:
            await bot.set_message_reaction(
                chat_id=message.chat.id,
                message_id=message.message_id,
                reaction=[{"type": "emoji", "emoji": reaction}]
            )
        except:
            pass

    # 17. Обновление времени активности
    user["last_activity"] = datetime.now().isoformat()
    save_data(user_data)

# ============================================================
#  УВЕДОМЛЕНИЯ (ЕЖЕДНЕВНЫЕ И "СКУЧАЮ")
# ============================================================
async def check_notifications():
    while True:
        try:
            now = datetime.now()
            for user_id, user in list(user_data.items()):
                # Бесплатный прокрут
                if user.get("last_free_spin") != now.date().isoformat():
                    if user.get("last_spin_notified") != now.date().isoformat():
                        user["last_spin_notified"] = now.date().isoformat()
                        save_data(user_data)
                        try:
                            await bot.send_message(
                                int(user_id),
                                get_text(user, "spin_reminder")
                            )
                        except:
                            pass

                # "Скучаю" (если 3 дня без активности)
                if user.get("last_activity"):
                    try:
                        last = datetime.fromisoformat(user["last_activity"])
                        if (now - last).days >= 3:
                            if user.get("last_reminder") != now.date().isoformat():
                                user["last_reminder"] = now.date().isoformat()
                                save_data(user_data)
                                gender = user.get("gender", "female")
                                messages_ru = [
                                    "Я скучаю... Ты где пропал? 😔 Напиши мне...",
                                    "Эй, ты там живой? 🥺 Я уже начала волноваться...",
                                    "Привет! Давно не общались... Расскажи, как дела 💕",
                                    "Ты мне снился сегодня... 😏 Напиши, может, я не ошиблась"
                                ]
                                # Для других языков можно добавить позже
                                msg = random.choice(messages_ru)
                                try:
                                    await bot.send_message(int(user_id), msg)
                                except:
                                    pass
                    except:
                        pass
        except Exception as e:
            logging.error(f"Ошибка уведомлений: {e}")
        await asyncio.sleep(3600)  # каждые 60 минут

# ============================================================
#  ЗАПУСК
# ============================================================
async def main():
    print("🚀 Role Duel финальная версия запущена!")
    print("🧠 Модель: deepseek/deepseek-chat")
    print("📦 Пакеты: 30⭐/30, 80⭐/100, 200⭐/300")
    print("🔥 PRO: 250⭐/мес (50 сообщений/день)")
    print("✨ SUPER PRO: 450⭐/мес (100 сообщений/день)")
    print("🎰 Колесо фортуны — 20⭐ за прокрутку")
    print("✏️ Редактирование последнего сообщения")
    print("👥 Реферальная система")
    print("💾 Данные сохраняются в data/data.json")
    print("✅ БОТ ГОТОВ К РАБОТЕ!")

    # Запускаем фоновую задачу уведомлений
    asyncio.create_task(check_notifications())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
