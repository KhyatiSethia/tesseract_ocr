# User Guide


## 1. Visual Studio 2022 Community

- Download and install Visual Studio 2022 Community from [here](https://visualstudio.microsoft.com/vs/).
- During installation, make sure to include the following Workloads and Individual Components:
  - **Workloads:**
    - Desktop development with C++
      - MSVC v143 - VS 2022 C++
      - Windows 11 SDK
      - C++ CMake tools for Windows
      - vcpkg package manager
  - **Individual Components:**
    - .NET Framework 4.8.1 SDK
    - Windows Universal CRT SDK
    - Git for Windows


## 2. Software Network Client

- Download the Software Network Client from [here](https://software-network.org/client/).
- Extract the downloaded `sw-master-windows_x86_64-client.zip` file.
- Add the path to the extracted folder (`../sw-master-windows_x86_64-client`) to the System variables in Environment variables.
- Run the following command in the command prompt:

Run following in cmd
sw setup
sw build org.sw.demo.google.tesseract.tesseract

## 3. Tesseract Installation

- Clone the Tesseract repository:
```bash
git clone https://github.com/tesseract-ocr/tesseract tesseract
```

- Open the Developer Command Prompt for Visual Studio 2022.
- Navigate to the cloned Tesseract repository (`cd tesseract`).
- Create a build directory and navigate into it:
```bash
mkdir build && cd build
cmake ..
```

- Set the path for Tesseract executable in your Python script:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = '../tesseract/build/bin/Debug/tesseract.exe'
```

## 4. Anaconda Environment Setup

- Install Anaconda and add its path to the System variables.
- Create a new Conda environment named myenv, activate it and install the modules:
```bash
conda create --name myenv
conda activate myenv
pip install -r requirements.txt
```

## 5. Poppler Installation
- Download Poppler from [here](https://github.com/oschwartz10612/poppler-windows/releases/).
- Extract the downloaded `Release-24.02.0-0.zip` file.
- Set the Poppler path in your Python script:
```python
poppler_path = "../poppler-24.02.0/Library/bin"
```

## 5. Download languages
- Download languages from [here](https://github.com/tesseract-ocr/tessdata/tree/main/script) or [here](https://github.com/tesseract-ocr/tessdata).
- Place the languages to this folder "../tesseract/build/bin/Debug/tessdata"

## 6. Example usage

- tables_present_in_pdf - if tables are present in the the pdf pages.

Usage: python script.py <input_filepath> <page_no_first> <page_no_last> <lang> <output_file> <tables_present_in_pdf>
```python
python main.py data/2024-EROLLGEN-S20-46-FinalRoll-Revision1-HIN-258-WI.pdf 3 4 Devanagari out1.txt True
python main.py data/2024-EROLLGEN-S20-46-FinalRoll-Revision1-HIN-258-WI.pdf 3 4 Devanagari out1.txt False
```