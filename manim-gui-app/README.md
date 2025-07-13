# Manim GUI Application

This project is a Python GUI application designed for creating and managing slides using PDF files and generating animations with Manim. The application features a dual PDF viewer, a slide list, and a slide editor, allowing users to navigate and edit slides efficiently.

## Features

- **Dual PDF Viewers**: Scroll through the same PDF document at different locations.
- **Slide List**: A list similar to PowerPoint for easy navigation between slides.
- **Slide Editor**: Display and edit the selected slide.
- **Toolbar**: Select animations and other actions related to slide generation.
- **Inkscape Integration**: Use Inkscape commands to capture PDF pages and generate Manim slide code.

## Installation

To install the required dependencies, run:

```
pip install -r requirements.txt
```

## Usage

To start the application, run the following command:

```
python src/main.py
```

## Project Structure

```
manim-gui-app
├── src
│   ├── main.py                # Entry point of the application
│   ├── gui                    # GUI components
│   ├── core                   # Core functionalities
│   ├── models                 # Data models
│   └── utils                  # Utility functions
├── resources                  # Resources like icons and templates
├── tests                      # Unit tests for the application
├── requirements.txt           # Project dependencies
├── setup.py                   # Setup script for the project
└── README.md                  # Project documentation
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.