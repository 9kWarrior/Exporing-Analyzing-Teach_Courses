import pickle
import joblib
import logging
from secret_data import TOKEN
import numpy as np
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from keras.models import load_model

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Загрузка компонентов модели
def load_model_components():
    try:
        with open('features_list.pkl', 'rb') as f:
            features = pickle.load(f)
        preprocessor = joblib.load('full_preprocessor.joblib')
        model = load_model('lstm_model.keras')
        scaler_y = joblib.load('scaler_y.joblib')
        return model, preprocessor, scaler_y, features
    except Exception as e:
        logger.error(f"Ошибка загрузки модели: {e}")
        raise


# Инициализация модели при старте
model, preprocessor, scaler_y, features = load_model_components()


# Функция предсказания
def predict_cost(input_dict, model, preprocessor, scaler_y, features):
    try:
        input_df = pd.DataFrame([input_dict])[features]
        X_processed = preprocessor.transform(input_df)
        if hasattr(X_processed, 'toarray'):
            X_processed = X_processed.toarray()

        if X_processed.shape[1] != model.input_shape[2]:
            raise ValueError(
                f"Несоответствие размеров: модель ожидает {model.input_shape[2]} признаков, "
                f"получено {X_processed.shape[1]}. Проверьте препроцессор."
            )

        X_reshaped = np.expand_dims(X_processed, axis=1)
        y_pred = scaler_y.inverse_transform(model.predict(X_reshaped))
        return y_pred[0][0]
    except Exception as e:
        logger.error(f"Ошибка предсказания: {e}")
        return None


# Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['/predict']]
    await update.message.reply_text(
        "Привет! Я бот для предсказания стоимости обучения.\n"
        "Нажми /predict чтобы начать",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )


async def predict_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите данные в формате:\n"
        "Год: 2025\n"
        "Месяц: 6\n"
        "День: 1\n"
        "Проходной балл: 85\n"
        "Бюджетные места: 20\n"
        "Программа: Информатика\n"
        "Вуз: МГУ"
    )


async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Парсинг ввода
        input_dict = {}
        for line in update.message.text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                input_dict[key.strip()] = value.strip()

        # Преобразование типов
        input_dict['Год'] = int(input_dict['Год'])
        input_dict['Месяц'] = int(input_dict['Месяц'])
        input_dict['День'] = int(input_dict['День'])
        input_dict['Проходной балл'] = int(input_dict['Проходной балл'])
        input_dict['Бюджетные места'] = int(input_dict['Бюджетные места'])

        # Предсказание
        prediction = predict_cost(input_dict, model, preprocessor, scaler_y, features)

        if prediction is not None:
            await update.message.reply_text(f"Предсказанная стоимость: {prediction:.2f} руб.")
        else:
            await update.message.reply_text("Не удалось сделать предсказание. Проверьте ввод.")

    except Exception as e:
        logger.error(f"Ошибка обработки ввода: {e}")
        await update.message.reply_text("Ошибка формата ввода. Используйте формат:\nГод: 2025\nМесяц: 6\n...")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f'Update {update} caused error {context.error}')
    if isinstance(update, Update):
        await update.message.reply_text('Произошла ошибка. Попробуйте позже.')


# def main():
    # Создаем Application вместо Updater
application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("predict", predict_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
application.add_error_handler(error_handler)

    # Запускаем бота
application.run_polling()


# if __name__ == "__main__":
#     main()