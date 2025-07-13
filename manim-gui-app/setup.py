from setuptools import setup, find_packages

setup(
    name='manim-gui-app',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A GUI application for creating Manim slides from PDF files.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'PyQt5==5.15.10',
        'PyMuPDF==1.23.14',
        'Pillow==10.2.0',
        'manim-slides==5.1.7',
    ],
    entry_points={
        'console_scripts': [
            'manim-gui-app=main:main',  # Assuming main.py has a main function to start the app
        ],
    },
)