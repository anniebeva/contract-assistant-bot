import logging
import io
import tempfile
import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from pypdf import PdfReader
from docx import Document
from bot.conversation import add_to_history, get_history, reset_history
from llm.client import call_groq
from llm.prompts import SYSTEM_PROMPT, SYSTEM_PROMPT_QUESTION
from config.settings import MAX_HISTORY
from rag.keyword_retriever import retrieve_context

async def extract_text_from_file(document) -> tuple[str, str | None]:
    """Возвращает (текст, ошибка)"""
    file_extension = os.path.splitext(document.file_name)[1].lower()
    
    file_obj = await document.get_file()
    file_bytes = await file_obj.download_as_bytearray()
    
    try:
        if file_extension == '.pdf':
            reader = PdfReader(io.BytesIO(file_bytes))
            text = "\n".join(page.extract_text() for page in reader.pages)
            return text, None
        elif file_extension == '.docx':
            doc = Document(io.BytesIO(file_bytes))
            text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
            return text, None
        else:
            return "", "Неподдерживаемый формат файла. Отправьте PDF или DOCX."
    except Exception as e:
        logging.error(f"File extraction error: {e}")
        return "", "Ошибка при чтении файла. Попробуйте другой файл или скопируйте текст вручную."
    

async def process_text(user_id: int, text: str, reply_func) -> None:
    """reply_func - функция для отправки ответа пользователю (update.message.reply_text)"""
    if not text.strip():
        await reply_func("Из файла не удалось извлечь текст. Попробуйте другой файл или отправьте текст вручную.")
        return
    
    await reply_func("Анализирую договор...")
    
    add_to_history(user_id, "user", text, MAX_HISTORY)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + get_history(user_id)
    
    try:
        reply = await call_groq(messages)
        add_to_history(user_id, "assistant", reply, MAX_HISTORY)
    except Exception as e:
        logging.error(f"LLM error: {e}")
        reply = "⚠️ Ошибка при вызове модели. Попробуйте позже."
    
    if len(reply) > 4000:
        for i in range(0, len(reply), 4000):
            await reply_func(reply[i:i+4000])
    else:
        await reply_func(reply)

# Обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    logging.info("Получена команда /start")
    message = update.message
    if message is None:
        logging.warning("update.message is None")
        return
    await message.reply_text(
        "🤖 **Contract Assistant Bot**\n\n"
        "Я проверяю договоры на риски: штрафы, сроки оплаты, форс-мажор, односторонние изменения.\n\n"
        "📎 Отправьте текст договора или файл (PDF/DOCX).\n"
        "/reset — очистить историю.\n\n"
        "⚠️ Демо-версия. Для конфиденциальных договоров используйте локальный LLM.",
        parse_mode="Markdown"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /reset - очищает историю диалога"""
    message = update.message
    if message is None:
        return
    user = update.effective_user
    if user is None:
        await message.reply_text("Не удалось идентифицировать пользователя.")
        return
    reset_history(user.id)
    await message.reply_text("История диалога очищена.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка текстовых сообщений с определением типа запроса.
    
    Определяет тип запроса на основе длины текста и наличия договорных маркеров:
    - Вопросы (до 300 символов без договорных терминов) → RAG поиск в базе знаний
    - Договоры → проверка на соответствие политикам компании
    
    Args:
        update: Telegram Update объект
        context: Telegram Context объект
    """
    message = update.message
    if message is None:
        return
    user = update.effective_user
    if user is None:
        await message.reply_text("Не удалось идентифицировать пользователя.")
        return
    
    text = message.text
    print(f"📩 Получено сообщение: {text}")
    
    if not text or not text.strip():
        await message.reply_text("Пожалуйста, отправьте текст договора или задайте вопрос.")
        return

    # Определяем тип запроса: вопрос или договор
    is_question = len(text) < 300 and not any(
        word in text.lower() for word in ["договор", "стороны", "поставка", "платеж", "сумма", "штраф", "пеня"]
    )

    if is_question:
        # Обработка вопроса через RAG
        await message.chat.send_action(action=ChatAction.TYPING)
        fragments = retrieve_context(text)
        
        if fragments:
            context_str = "\n\n---\n\n".join([f["content"] for f in fragments])
            from llm.prompts import SYSTEM_PROMPT_QUESTION
            system_prompt = SYSTEM_PROMPT_QUESTION.format(context=context_str, question=text)
            messages = [{"role": "system", "content": system_prompt}]
        else:
            await message.reply_text("В базе знаний не найдено информации по вашему запросу. Пожалуйста, уточните вопрос или обратитесь к юристу.")
            return
    else:
        # Обработка договора через проверку
        await message.chat.send_action(action=ChatAction.TYPING)
        add_to_history(user.id, "user", text, MAX_HISTORY)
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + get_history(user.id)

    # Вызов LLM для генерации ответа
    try:
        reply = await call_groq(messages)
        if not is_question:
            add_to_history(user.id, "assistant", reply, MAX_HISTORY)
    except Exception as e:
        logging.error(f"LLM error: {e}")
        reply = "⚠️ Ошибка при вызове модели. Попробуйте позже."

    # Отправка ответа с разбивкой на части при необходимости
    if len(reply) > 4000:
        for i in range(0, len(reply), 4000):
            await message.reply_text(reply[i:i+4000])
    else:
        await message.reply_text(reply)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка файлов (PDF, DOCX) с проверкой размера и заглушкой антивируса"""
    message = update.message
    if message is None:
        return
    user = update.effective_user
    if user is None:
        await message.reply_text("Не удалось идентифицировать пользователя.")
        return
    
    document = message.document
    if document is None:
        return
    
    # 1. Проверка размера файла (если известен)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    if document.file_size is not None and document.file_size > MAX_FILE_SIZE:
        await message.reply_text("Файл слишком большой. Максимальный размер — 10 МБ.")
        return
    
    # 2. Заглушка для антивирусной проверки (в боевой среде раскомментировать и реализовать)
    # file_bytes = await document.download_as_bytearray()
    # if await is_infected(file_bytes):
    #     await message.reply_text("Файл содержит вредоносный код. Отправка отклонена.")
    #     return
    
    # 3. Индикатор "печатает" с защитой от ошибок сети
    try:
        await message.chat.send_action(action=ChatAction.TYPING)
    except Exception as e:
        logging.warning(f"Не удалось отправить typing action: {e}")
    
    await message.reply_text("Получил файл. Извлекаю текст...")
    
    # 4. Извлечение текста
    text, error = await extract_text_from_file(document)
    if error:
        await message.reply_text(error)
        return
    
    await message.reply_text(f"Текст из файла извлечён (длина: {len(text)} символов). Анализирую...")
    await process_text(user.id, text, message.reply_text)