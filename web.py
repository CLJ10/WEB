import streamlit as st
import os
import subprocess
from datetime import datetime
import hashlib
import matplotlib.pyplot as plt
import io
import numpy as np
import string
import re
from collections import Counter

# Шлях до папки з лабораторними роботами
LABS_FOLDER = "labs"
# Шлях до файлу для збереження відгуків
FEEDBACK_FILE = "feedbacks.txt"

# Логування нового користувача в консоль
print(f"[{datetime.now()}] Новий користувач приєднався")


# Функція для отримання списку лабораторних робіт
def get_lab_list(folder):
    labs = []
    for item in os.listdir(folder):
        item_path = os.path.join(folder, item)
        if os.path.isdir(item_path):
            readme_path = os.path.join(item_path, "README.md")
            description = "Опис відсутній"
            if os.path.exists(readme_path):
                with open(readme_path, "r", encoding="utf-8") as file:
                    description = file.read().strip()
            labs.append({"name": item, "path": item_path, "description": description})
    return labs


# Функція для запуску лабораторної роботи
def run_lab(lab_path, script_name, params):
    script_to_run = os.path.join(lab_path, script_name)
    result = subprocess.run(["python", script_to_run] + params, capture_output=True, text=True)
    return result.stdout, result.stderr


# Функція для хешування даних
def hash_data(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


# Функція для збереження відгуків
def save_feedback(name, feedback):
    hashed_name = hash_data(name)  # Хешуємо ім'я для конфіденційності
    with open(FEEDBACK_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{datetime.now()}] {hashed_name}: {feedback}\n")


# Функція для перегляду всіх відгуків
def read_feedbacks():
    if not os.path.exists(FEEDBACK_FILE):
        return "Немає залишених відгуків."
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as file:
        return file.read()


# Функція для створення і відображення графіку
def create_and_show_plot():
    # Декілька даних для графіку
    x = np.linspace(0, 10, 100)
    y = x ** np.sin(10 * x)

    plt.plot(x, y)
    plt.xlabel("x")
    plt.ylabel("Y(x)")
    plt.title(r"Графік функції $Y(x) = x^{\sin(10x)}$", fontsize=14)  # Використання сирого рядка для LaTeX
    plt.grid(True)

    # Збереження графіка в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return buf


# Нова функція для побудови гістограми частоти літер з файлу
def plot_letter_frequency_from_file(filename):
    # Зчитування тексту з файлу
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()
    except FileNotFoundError:
        return None, f"Файл {filename} не знайдено."
    except Exception as e:
        return None, f"Помилка при читанні файлу: {e}"

    # Очищаємо текст від непотрібних символів і переводимо в нижній регістр
    cleaned_text = ''.join([char.lower() for char in text if char in string.ascii_letters])

    # Рахуємо частоту кожної літери
    letter_counts = Counter(cleaned_text)

    # Сортуємо літери за абеткою
    sorted_letters = sorted(letter_counts.items(), key=lambda x: x[0])
    letters, counts = zip(*sorted_letters) if sorted_letters else ([], [])

    # Побудова гістограми
    plt.figure(figsize=(12, 6))
    plt.bar(letters, counts, color='skyblue', edgecolor='navy')
    plt.title('Частота появи літер у тексті', fontsize=15)
    plt.xlabel('Літери', fontsize=12)
    plt.ylabel('Кількість', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Збереження графіку в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close()

    return buf, None


# Нова функція для аналізу типів речень
def plot_sentence_type_frequency(text):
    # Розділення тексту на речення
    sentences = re.findall(r'[^.!?…]+[.!?…]', text)

    # Підрахунок типів речень
    sentence_types = {
        'Звичайні': 0,
        'Питальні': 0,
        'Окличні': 0,
        'З трикрапкою': 0
    }

    for sentence in sentences:
        sentence = sentence.strip()
        if sentence.endswith('…'):
            sentence_types['З трикрапкою'] += 1
        elif sentence.endswith('?'):
            sentence_types['Питальні'] += 1
        elif sentence.endswith('!'):
            sentence_types['Окличні'] += 1
        else:
            sentence_types['Звичайні'] += 1

    # Створення гістограми
    plt.figure(figsize=(10, 6))
    types = list(sentence_types.keys())
    counts = list(sentence_types.values())

    plt.bar(types, counts, color=['skyblue', 'lightgreen', 'salmon', 'orange'])
    plt.title('Частота типів речень у тексті', fontsize=15)
    plt.xlabel('Типи речень', fontsize=12)
    plt.ylabel('Кількість', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Додавання значень на стовпчики
    for i, count in enumerate(counts):
        plt.text(i, count, str(count), ha='center', va='bottom')

    # Збереження графіку в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    plt.close()

    return buf, sentence_types


# Головна сторінка
st.set_page_config(page_title="Лабораторні роботи", page_icon=":mortar_board:")
st.title("Лабораторні роботи")

labs = get_lab_list(LABS_FOLDER)

if not labs:
    st.warning("Немає доступних лабораторних робіт.")
else:
    lab_names = [lab["name"] for lab in labs]
    selected_lab_name = st.selectbox("Оберіть лабораторну роботу", ["---"] + lab_names)

    if selected_lab_name != "---":
        selected_lab = next(lab for lab in labs if lab["name"] == selected_lab_name)
        st.subheader(f"{selected_lab['name']}")
        st.markdown(f"**Опис:** {selected_lab['description']}")

        python_files = [f for f in os.listdir(selected_lab["path"]) if f.endswith(".py")]

        if python_files:
            selected_script = st.selectbox("Оберіть скрипт для запуску", python_files)

            if selected_script:
                params_input = st.text_area("Введіть параметри для скрипта через пробіл:")

                if st.button("Запустити лабораторну роботу"):
                    with st.spinner("Виконання лабораторної роботи..."):
                        params = params_input.split() if params_input else []
                        stdout, stderr = run_lab(selected_lab["path"], selected_script, params)
                        if stdout:
                            st.success("Результат виконання:")
                            st.code(stdout)
                        if stderr:
                            st.error("Помилки:")
                            st.code(stderr)
        else:
            st.warning("Жодного .py файлу не знайдено в папці лабораторної роботи.")

# Додаткові сторінки
with st.sidebar:
    st.header("Навігація")
    nav_option = st.radio("Перейти до", [
        "Головна", "Про мене", "Зворотній зв'язок",
        "Перегляд відгуків", "Графік",
        "Аналіз частоти літер", "Аналіз типів речень"
    ])

    if nav_option == "Про мене":
        st.subheader("Про мене")
        st.markdown("Цей веб-інтерфейс розроблено для запуску лабораторних робіт. Автором є Грушка Дмитро")

    elif nav_option == "Зворотній зв'язок":
        st.subheader("Зворотній зв'язок")
        name = st.text_input("Ваше ім'я")
        feedback = st.text_area("Ваш відгук")
        if st.button("Відправити"):
            if name and feedback:
                save_feedback(name, feedback)
                st.success("Дякуємо за ваш відгук!")
            else:
                st.warning("Будь ласка, заповніть усі поля.")

    elif nav_option == "Перегляд відгуків":
        st.subheader("Відгуки користувачів")
        feedbacks = read_feedbacks()
        st.text_area("Всі відгуки", feedbacks, height=300, disabled=True)

    elif nav_option == "Графік":
        st.subheader("Графік")
        st.write("Ось графік, що демонструє функцію x^2:")
        plot_buf = create_and_show_plot()
        st.image(plot_buf, caption="Графік функції $Y(x) = x^{\sin(10x)}$", use_column_width=True)

    elif nav_option == "Аналіз частоти літер":
        st.subheader("Аналіз частоти літер з файлу")

        # Отримання списку txt файлів у поточній директорії
        txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]

        if txt_files:
            selected_file = st.selectbox("Оберіть текстовий файл", txt_files)

            if st.button("Побудувати гістограму"):
                plot_buf, error = plot_letter_frequency_from_file(selected_file)

                if error:
                    st.error(error)
                elif plot_buf:
                    st.image(plot_buf, caption=f"Гістограма частоти літер для {selected_file}", use_column_width=True)
        else:
            st.warning("Немає доступних текстових файлів у поточній директорії.")

    elif nav_option == "Аналіз типів речень":
        st.subheader("Аналіз типів речень")

        # Текстове поле для введення тексту
        text_input = st.text_area("Введіть текст для аналізу типів речень:")

        if st.button("Побудувати гістограму"):
            if text_input:
                try:
                    plot_buf, sentence_stats = plot_sentence_type_frequency(text_input)

                    # Відображення графіку
                    st.image(plot_buf, caption="Гістограма типів речень", use_column_width=True)

                    # Додаткова статистика
                    st.subheader("Статистика типів речень:")
                    for sentence_type, count in sentence_stats.items():
                        st.write(f"{sentence_type}: {count}")

                except Exception as e:
                    st.error(f"Помилка при аналізі тексту: {e}")
            else:
                st.warning("Будь ласка, введіть текст для аналізу.")