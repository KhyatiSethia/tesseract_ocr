from flask import Flask, render_template, request, redirect, send_file, url_for
from werkzeug.utils import secure_filename
import os
import sys
from pathlib import Path
from src.pytesseract import pytesseract_pdf_to_string, pytesseract_pdf_with_tables_to_string
import subprocess

app = Flask(__name__)

# Set paths
os.environ['TESSERACT_CMD'] = 'C:/Users/set0013/Downloads/Projects_all/nlp/tesseract/build/bin/Debug/tesseract.exe'
os.environ['POPPLER_PATH'] = 'C:/Users/set0013/Downloads/Projects_all/softwares/poppler-24.02.0/Library/bin'

tesseract_cmd = os.getenv('TESSERACT_CMD')
poppler_path = os.getenv('POPPLER_PATH')
os.environ['PATH'] += os.pathsep + os.path.dirname(tesseract_cmd)

UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'outputs'

ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

parent_directory = os.path.dirname(__file__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_available_languages():
    try:
        # Run the command to list languages
        result = subprocess.run([tesseract_cmd, '--list-langs'], capture_output=True, text=True)
        if result.returncode == 0:
            # Parse the output to extract language codes
            languages = result.stdout.strip().split('\n')[1:]
            return languages
        else:
            print("Error:", result.stderr)
            return []
    except Exception as e:
        print("An error occurred:", e)
        return []

@app.route('/', methods=["POST", "GET"])
def sample():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Check if the file already exists and delete it
            if os.path.exists(upload_path):
                os.remove(upload_path)

            file.save(upload_path)

            page_no_first = int(request.form['page_no_first'])
            page_no_last = int(request.form['page_no_last'])
            lang = request.form['language']
            tables_present_in_pdf = 'tables_present_in_pdf' in request.form
            output_filename = f"{Path(filename).stem}_text.txt"

            try:
                if tables_present_in_pdf:
                    full_text = pytesseract_pdf_with_tables_to_string(
                        upload_path, page_no_first, page_no_last, lang, output_filename, tesseract_cmd, poppler_path, False)
                else:
                    full_text = pytesseract_pdf_to_string(
                        upload_path, page_no_first, page_no_last, lang, output_filename, tesseract_cmd, poppler_path)

                return render_template('index.html', sample_output=full_text, download_url=url_for('download_file', filename=output_filename))

            except Exception as e:
                return f"An error occurred: {e}"
        else:
            return redirect(request.url)
    
    elif request.method == 'GET':
        languages = get_available_languages()
        return render_template("index.html", languages=languages)


@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], filename), as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
