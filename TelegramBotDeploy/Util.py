import pickle
import joblib
import logging
from secret_data import TOKEN
import numpy as np
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from keras.models import load_model
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sem_model import find_okso_code, find_exact_match

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
        semantic_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        return model, preprocessor, scaler_y, features, semantic_model
    except Exception as e:
        logger.error(f"Ошибка загрузки модели: {e}")
        raise


def load_model_components_v2():
    try:
        with open('features_list.pkl', 'rb') as f:
            features = pickle.load(f)
        preprocessor = joblib.load('full_preprocessor.joblib')
        model = load_model('lstm_model.keras')
        scaler_y = joblib.load('scaler_y.joblib')
        semantic_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        return model, preprocessor, scaler_y, features, semantic_model
    except Exception as e:
        logger.error(f"Ошибка загрузки модели: {e}")
        raise


# Инициализация модели при старте
model, preprocessor, scaler_y, features, semantic_model = load_model_components()
model_v2, preprocessor_v2, scaler_y_v2, features_v2, semantic_model_v2 = load_model_components_v2()

def find_closest_match(query: str, options: list, model, threshold=0.7) -> str:
    if not options:
        print("No opytions")
        return query
    # Кодируем все варианты и запрос
    options_embeddings = model.encode(options, convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Вычисляем схожесть
    similarities = cosine_similarity(
        query_embedding.reshape(1, -1),
        options_embeddings
    )[0]

    best_match_idx = np.argmax(similarities)
    best_match_score = similarities[best_match_idx]

    if best_match_score >= threshold:
        print("returning this ", options[best_match_idx])
        return options[best_match_idx]
    return query
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
        # Парсинг ввода пользователя
        input_dict = {}
        for line in update.message.text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                input_dict[key.strip()] = value.strip()

        # Проверка обязательных полей
        required_fields = ['Год', 'Месяц', 'День', 'Проходной балл', 'Бюджетные места', 'Программа', 'Вуз']
        for field in required_fields:
            if field not in input_dict:
                await update.message.reply_text(f"Отсутствует обязательное поле: {field}")
                return

        # Преобразование числовых полей
        try:
            input_dict['Год'] = int(input_dict['Год'])
            input_dict['Месяц'] = int(input_dict['Месяц'])
            input_dict['День'] = int(input_dict['День'])
            input_dict['Проходной балл'] = int(input_dict['Проходной балл'])
            input_dict['Бюджетные места'] = int(input_dict['Бюджетные места'])
        except ValueError:
            await update.message.reply_text(
                "Ошибка в числовых полях. Убедитесь, что год, месяц, день, балл и места - целые числа.")
            return

        # Загрузка списка программ из CSV
        try:
            programs_df = pd.read_csv('programs_names_data.csv')
            PROGRAMS = programs_df['Программа'].tolist()  # Предполагаем столбец 'Название'
        except Exception as e:
            logger.error(f"Ошибка загрузки файла программ: {e}")
            PROGRAMS = ["Информатика", "Математика", "Физика"]  # Fallback список

        # Загрузка списка вузов из CSV
        try:
            universities_df = pd.read_csv('university_names_data.csv')
            UNIVERSITIES = universities_df['Вуз'].tolist()  # Предполагаем столбец 'Название'
        except Exception as e:
            logger.error(f"Ошибка загрузки файла вузов: {e}")
            UNIVERSITIES = ["МГУ", "ВШЭ", "МФТИ"]  # Fallback список

        # Получаем модель для семантического поиска из контекста
        semantic_model = context.bot_data["semantic_model"]

        # Корректируем название программы
        original_program = input_dict["Программа"]
        corrected_program = find_closest_match(
            original_program,
            PROGRAMS,
            semantic_model,
            threshold=0.95
        )

        # Корректируем название вуза
        original_university = input_dict["Вуз"]
        corrected_university = find_closest_match(
            original_university,
            UNIVERSITIES,
            semantic_model,
            threshold=0.9
        )
        university_exists = corrected_university in UNIVERSITIES
        programm_exists = corrected_program in PROGRAMS
        # Уведомляем пользователя об исправлениях
        corrections = []
        if corrected_program != original_program:
            corrections.append(f"Программа: '{original_program}' → '{corrected_program}'")
            input_dict["Программа"] = corrected_program

        if corrected_university != original_university:
            corrections.append(f"Вуз: '{original_university}' → '{corrected_university}'")
            input_dict["Вуз"] = corrected_university

        if corrections:
            await update.message.reply_text("Автоматические исправления:\n" + "\n".join(corrections))

        if not university_exists or not programm_exists:
            print(input_dict)
            input_dict['Программа'] = find_okso_code(input_dict['Программа'])
            print(input_dict)
            prediction = predict_cost(input_dict,
                                      context.bot_data["model_v2"],
                                      context.bot_data["preprocessor_v2"],
                                      context.bot_data["scaler_y_v2"],
                                      context.bot_data["features_v2"])
        else:
            print("Существует в списке и оксо код не нужен ", input_dict)
            prediction = predict_cost(input_dict,
                                      context.bot_data["model"],
                                      context.bot_data["preprocessor"],
                                      context.bot_data["scaler_y"],
                                      context.bot_data["features"])


        if prediction is not None:
            await update.message.reply_text(f"Предсказанная стоимость: {prediction:.2f} руб.")
        else:
            await update.message.reply_text("Не удалось сделать предсказание. Пожалуйста, проверьте введённые данные.")

    except Exception as e:
        logger.error(f"Ошибка обработки ввода: {e}", exc_info=True)
        await update.message.reply_text(
            "Ошибка обработки запроса. Пожалуйста, введите данные в формате:\n\n"
            "Год: 2025\n"
            "Месяц: 6\n"
            "День: 1\n"
            "Проходной балл: 85\n"
            "Бюджетные места: 20\n"
            "Программа: Информатика\n"
            "Вуз: МГУ\n\n"
            "Ошибка: " + str(e)
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f'Update {update} caused error {context.error}')
    if isinstance(update, Update):
        await update.message.reply_text('Произошла ошибка. Попробуйте позже.')


# def main():

application = Application.builder().token(TOKEN).build()
application.bot_data["model"] = model
application.bot_data["preprocessor"] = preprocessor
application.bot_data["scaler_y"] = scaler_y
application.bot_data["features"] = features
application.bot_data["semantic_model"] = semantic_model
application.bot_data["model_v2"] = model_v2
application.bot_data["preprocessor_v2"] = preprocessor_v2
application.bot_data["scaler_y_v2"] = scaler_y_v2
application.bot_data["features_v2"] = features_v2


application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("predict", predict_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
application.add_error_handler(error_handler)


application.run_polling()


# if __name__ == "__main__":
#     main()