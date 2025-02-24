# Answer Sheet Grading System

A modern Python-based application for automated grading of answer sheets using OCR technology. This application provides an intuitive GUI interface for processing and grading multiple-choice answer sheets efficiently.

## 🌟 Features

- Modern, user-friendly GUI interface
- Automated answer detection using OCR (Optical Character Recognition)
- Manual verification and correction of detected answers
- Customizable answer key management
- Detailed grading results with score calculation
- Support for various image formats (PNG, JPG, JPEG, BMP)
- GPU acceleration support (when available)

## 📋 Prerequisites

- Python 3.7 or higher
- GPU (optional but recommended for faster processing)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/atik666/grading.git
cd grading
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

Required packages include:
- tkinter
- Pillow
- opencv-python
- easyocr
- numpy
- torch

## 🚀 Usage

1. Run the application:
```bash
python modern_gui.py
```

2. Using the application:
   - Click "Select Folder" to choose a directory containing answer sheet images
   - Select an image from the file browser to preview
   - Click "Grade Selected" to process the selected image
   - Verify and correct the detected answers in the popup window
   - View detailed results in the results panel

3. Managing the Answer Key:
   - Click "Edit Answer Key" to modify the answer key
   - Add or remove questions as needed
   - Enter correct answers (A-Z) for each question
   - Click "Save Changes" to update the answer key

## 📝 Answer Sheet Requirements

For optimal results, ensure answer sheets:
- Are well-lit and clearly photographed
- Have answers marked in format: "1. A", "2. B", etc.
- Are free from excessive markings or damage
- Have good contrast between text and background

### Example Answer Sheet Format:

```
1. B    6. A
2. E    7. A
3. C    8. A
4. B    9. E
5. G    10. D
```

The answers should be clearly written or typed, with each answer on a new line or properly spaced. 
The system can handle both vertical and horizontal layouts as long as the question number and answer are clearly associated (e.g., "1. B" or "1) B" or "1-B".

## ⚙️ Configuration

The application saves the answer key in `answer_key.txt` in the application directory. Default answer key is provided if the file doesn't exist.

## 🔧 Troubleshooting

Common issues and solutions:
1. OCR not detecting answers properly:
   - Ensure good image quality
   - Check image lighting and contrast
   - Verify answer format matches requirements

2. Performance issues:
   - Enable GPU support if available
   - Reduce image resolution if necessary
   - Close other resource-intensive applications

## 👨‍💻 Developer Information

Developed by: Atik Faysal
Email: faysal24@rowan.edu

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request