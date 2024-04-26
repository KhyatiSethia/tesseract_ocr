import os
import sys
from pathlib import Path
from src.pytesseract import pytesseract_pdf_to_string, pytesseract_pdf_with_tables_to_string

# Set paths
os.environ['TESSERACT_CMD'] = 'C:/Users/khyat/Documents/Khyati/PProjects/NLP/tesseract/build/bin/Debug/tesseract.exe'
os.environ['POPPLER_PATH'] = 'C:/Users/khyat/Documents/Khyati/Softwares/poppler-24.02.0/Library/bin'

tesseract_cmd = os.getenv('TESSERACT_CMD')
poppler_path = os.getenv('POPPLER_PATH')


def main():
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 7:
        print("Usage: python script.py <input_filepath> <page_no_first> <page_no_last> <lang> <output_file>")
        sys.exit(1)

    input_filepath = Path(sys.argv[1])
    page_no_first = int(sys.argv[2])
    page_no_last = int(sys.argv[3])
    lang = sys.argv[4]
    output_file = sys.argv[5]
    tables_present_in_pdf = sys.argv[6]

    # Check if input file exists
    if not input_filepath.is_file():
        print("Input file does not exist.")
        sys.exit(1)

    try:
        # Convert string argument to boolean
        if tables_present_in_pdf.lower() == 'true':
            pytesseract_pdf_with_tables_to_string(
                input_filepath, page_no_first, page_no_last, lang, output_file, tesseract_cmd, poppler_path, True)
        else:
            pytesseract_pdf_to_string(
                input_filepath, page_no_first, page_no_last, lang, output_file, tesseract_cmd, poppler_path)

        print("Text extracted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
