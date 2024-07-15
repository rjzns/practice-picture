from flask import Flask, render_template, request
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'file_search'

# Поддерживаемые форматы файлов
SUPPORTED_FORMATS = ['.png', '.jpeg', '.jpg', '.pdf']

# Проверка наличия библиотек PyPDF2 и Pillow
try:
    from PyPDF2 import PdfReader, PdfWriter
except ModuleNotFoundError:
    print("Не найдена библиотека PyPDF2. Установите её с помощью 'pip install PyPDF2'.")

try:
    from PIL import Image
except ModuleNotFoundError:
    print("Не найдена библиотека Pillow. Установите её с помощью 'pip install Pillow'.")

@app.route('/', methods=['GET', 'POST'])
def compress_files():
    if request.method == 'POST':
        # Проверка наличия папки 
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            error = f"Папка {app.config['UPLOAD_FOLDER']} не найдена."
            return render_template('index.html', error=error)

        files = os.listdir(app.config['UPLOAD_FOLDER'])
        if not files:
            error = f"В папке {app.config['UPLOAD_FOLDER']} нет файлов для сжатия."
            return render_template('index.html', error=error)

        # Создание списка для сжатых файлов и переменной для ошибок
        compressed_files = []
        error = None

        # Функция для сжатия изображения с изменением размера
        def compress_image(file_path, output_path, quality=50):
            with Image.open(file_path) as img:
                new_size = (img.width // 2, img.height // 2)
                img = img.resize(new_size, Image.LANCZOS)
                img.save(output_path, quality=quality)

        # Функция для сжатия PDF
        def compress_pdf(file_path, output_path):
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                writer = PdfWriter()

                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    page.compress_content_streams()
                    writer.add_page(page)

                with open(output_path, 'wb') as f_out:
                    writer.write(f_out)

        # Обработка каждого файла
        for file in files:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
            file_ext = os.path.splitext(file)[1].lower()
            original_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'_orig_{file}')

            if file_ext in SUPPORTED_FORMATS:
                try:
                    # Переименование оригинального файла
                    os.rename(file_path, original_file_path)

                    # Сжатие файла
                    if file_ext == '.pdf':
                        compress_pdf(original_file_path, file_path)
                    else:
                        compress_image(original_file_path, file_path)
                except Exception as e:
                    error = f"Ошибка при сжатии файла {file}: {str(e)}"
                    break
                else:
                    compressed_files.append(file_path)

        # Отображение списка сжатых файлов или сообщения об ошибке
        if error:
            return render_template('index.html', error=error)
        else:
            return render_template('compressed.html', compressed_files=compressed_files)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)