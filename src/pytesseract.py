
import os
import cv2
import numpy as np
import pdf2image
import pytesseract
from typing import List, Tuple


def extract_pages_from_pdf(pdf_file: str, page_no_first: int, page_no_last: int, poppler_path: str) -> np.ndarray:
    """
    Extracts pages from a PDF file.

    Args:
        pdf_file (str): Path to the PDF file.
        page_no_first (int): First page number to extract.
        page_no_last (int): Last page number to extract.
        poppler_path (str): Path to the Poppler binaries.

    Returns:
        np.ndarray: Images of the extracted pages.
    """
    images = np.array(pdf2image.convert_from_path(pdf_file,
                                                  first_page=page_no_first, last_page=page_no_last,
                                                  dpi=300, grayscale=True,
                                                  poppler_path=poppler_path))
    return images


def draw_and_visualize_contours(image: np.ndarray, contours: List[np.ndarray], output_file: str) -> None:
    """
    Draws contours on an image and saves it to a file.

    Args:
        image (np.ndarray): Input image.
        contours (List[np.ndarray]): List of contour arrays.
        output_file (str): Path to save the output image.
    """
    rgb_image = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2RGB)
    cv2.drawContours(rgb_image, contours, -1, (0, 255, 0), 2)
    cv2.imwrite(output_file, rgb_image)


def extract_text_from_image(image: np.ndarray, lang: str) -> str:
    """
    Extracts text from an image using pytesseract.

    Args:
        image (np.ndarray): Input image.
        lang (str): Language code for text recognition.

    Returns:
        str: Extracted text from the image.

    Notes:
        This function utilizes Tesseract's Optical Character Recognition (OCR) engine to extract text from the given image.
        It applies the Page Segmentation Mode (PSM) option '--psm 6' to instruct Tesseract to assume a single uniform
        block of text in the image. This mode is suitable for images containing plain, single-column text without
        significant formatting or structure.

        The language code specified by the 'lang' parameter determines the language used for text recognition.
        Ensure that Tesseract supports the specified language by installing the corresponding language data files.

        Any form feed characters ('\f') typically used for page breaks in text files are removed from the extracted text.
    """
    text = pytesseract.image_to_string(image, config='--psm 6', lang=lang)
    text = text.replace('\f', '')
    return text


def pytesseract_pdf_to_string(input_filepath: str, page_no_first: int, page_no_last: int, lang: str, output_file: str,
                              tesseract_cmd: str, poppler_path: str) -> None:
    """
    Extracts text from a PDF file using pytesseract and saves it to an output file.

    Args:
        input_filepath (str): Path to the input PDF file.
        page_no_first (int): First page number to extract.
        page_no_last (int): Last page number to extract.
        lang (str): Language code for text recognition.
        output_file (str): Path to the output text file.
        tesseract_cmd (str): Path to the Tesseract executable.
        poppler_path (str): Path to the Poppler binaries.
    """
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    # Create output file path
    output_file_path = os.path.join('outputs', output_file)

    full_text = []

    # Remove existing output file if present
    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    pages_sel = extract_pages_from_pdf(
        input_filepath, page_no_first, page_no_last, poppler_path)

    with open(output_file_path, 'a', encoding='utf-8') as f:
        page_num = page_no_first
        # Iterate over selected page range
        for page_sel in pages_sel:
            text = extract_text_from_image(page_sel, lang)
            f.write(text + '\n')
            page_num += page_num
            full_text.append(text)

    return full_text


def pytesseract_pdf_with_tables_to_string(input_filepath: str, page_no_first: int, page_no_last: int, lang: str, output_file: str,
                                          tesseract_cmd: str, poppler_path: str, visualize_steps: bool = False) -> None:
    """
    Extracts text from a PDF file using pytesseract and saves it to an output file.
    The pdf file has rectangles and tables in its pages.

    Args:
        input_filepath (str): Path to the input PDF file.
        page_no_first (int): First page number to extract.
        page_no_last (int): Last page number to extract.
        lang (str): Language code for text recognition.
        output_file (str): Path to the output text file.
        tesseract_cmd (str): Path to the Tesseract executable.
        poppler_path (str): Path to the Poppler binaries.
        visualize_steps (bool, optional): Whether to visualize intermediate steps. Defaults to False.
    """
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    # Create output file path
    output_file_path = os.path.join('outputs', output_file)

    full_text = []

    # Remove existing output file if present
    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    # Extract the current page from the PDF
    pages_sel = extract_pages_from_pdf(
        input_filepath, page_no_first, page_no_last, poppler_path)

    with open(output_file_path, 'a', encoding='utf-8') as f:
        page_num = page_no_first
        # Iterate over selected page range
        for page_sel in pages_sel:

            # Inverse binarize for contour finding
            thr = cv2.threshold(page_sel, 128, 255, cv2.THRESH_BINARY_INV)[1]

            # Find contours
            cnts = cv2.findContours(
                thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]

            # Filter contours for tables
            cnts_tables = [cnt for cnt in cnts if cv2.contourArea(cnt) > 10000]

            # Fill tables to remove text inside them
            no_tables = cv2.drawContours(
                thr.copy(), cnts_tables, -1, 0, cv2.FILLED)

            # Morphological closing to connect nearby text regions
            no_tables_morp = cv2.morphologyEx(
                no_tables, cv2.MORPH_CLOSE, np.full((21, 51), 255))

            cnts_no_tables = cv2.findContours(
                no_tables_morp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            cnts_no_tables = cnts_no_tables[0] if len(
                cnts_no_tables) == 2 else cnts_no_tables[1]

            # Find bounding rectangles of text regions outside of tables
            rects_out_tables = sorted([cv2.boundingRect(cnt)
                                       for cnt in cnts_no_tables], key=lambda r: r[1])
            # Find bounding rectangles of text regions inside tables
            rects_tables = sorted([cv2.boundingRect(cnt)
                                   for cnt in cnts_tables], key=lambda r: r[1])

            # Extract text from text regions outside of tables
            for (x, y, w, h) in rects_out_tables:
                text = extract_text_from_image(
                    page_sel[y:y+h, x:x+w], lang)
                f.write(text + '\n')
                full_text.append(text)

            # Extract text from text regions inside tables
            for i_r, (x, y, w, h) in enumerate(rects_tables, start=1):
                print('Extract texts inside table {}'.format(i_r))
                text = extract_text_from_image(
                    page_sel[y:y+h, x:x+w], lang)
                f.write(text + '\n')
                full_text.append(text)

            # Visualize intermediate steps if requested
            if visualize_steps:
                cv2.imwrite(
                    "outputs/threshold_image_page{}.png".format(page_num), thr)
                draw_and_visualize_contours(
                    thr, cnts, "outputs/contours_page{}.png".format(page_num))
                draw_and_visualize_contours(
                    thr, cnts_tables, "outputs/contours_tables_page{}.png".format(page_num))
                cv2.imwrite(
                    "outputs/no_tables_page{}.png".format(page_num), no_tables)
                cv2.imwrite(
                    "outputs/no_tables_morp_page{}.png".format(page_num), no_tables_morp)
                draw_and_visualize_contours(
                    thr, cnts_no_tables, "outputs/cnts2_page{}.png".format(page_num))

            page_num += page_num

    return full_text
