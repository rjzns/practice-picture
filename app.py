from flask import Flask, render_template, request
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'file_search'
app.config['COMPRESSED_FOLDER'] = 'compressed_images'

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

        # Создание папки для сжатых файлов, если её нет
        compressed_folder = app.config['COMPRESSED_FOLDER']
        if not os.path.exists(compressed_folder):
            try:
                os.makedirs(compressed_folder)
            except OSError:
                error = f"Не удалось создать папку {compressed_folder}"
                return render_template('index.html', error=error)

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

            if file_ext in SUPPORTED_FORMATS:
                # Путь для сохранения сжатого файла
                output_path = os.path.join(compressed_folder, f'compressed_{file}')

                try:
                    if file_ext == '.pdf':
                        compress_pdf(file_path, output_path)
                    else:
                        compress_image(file_path, output_path)
                except Exception as e:
                    error = f"Ошибка при сжатии файла {file}: {str(e)}"
                    break
                else:
                    compressed_files.append(output_path)

        # Отображение списка сжатых файлов или сообщения об ошибке
        if error:
            return render_template('index.html', error=error)
        else:
            return render_template('compressed.html', compressed_files=compressed_files)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)