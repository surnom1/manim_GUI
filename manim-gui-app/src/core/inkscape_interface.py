import subprocess
import os

class InkscapeInterface:
    def __init__(self, inkscape_path="inkscape"):
        """
        Initialize the InkscapeInterface with path to Inkscape executable.
        Default is 'inkscape' (assumes it's in PATH)
        """
        self.inkscape_path = inkscape_path

    def pdf_to_svg(self, pdf_path, page_number, output_svg_path):
        """
        Convert a specific page of a PDF to SVG using Inkscape
        
        Args:
            pdf_path (str): Path to the PDF file
            page_number (int): Page number to convert (1-based)
            output_svg_path (str): Path where to save the SVG file
        
        Returns:
            bool: True if conversion was successful, False otherwise
        """
        try:
            command = [
                self.inkscape_path,
                "--export-type=svg",
                "--export-plain-svg",
                f"--pdf-page={page_number}",
                f"--export-filename={output_svg_path}",
                pdf_path
            ]
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            return True
        except Exception as e:
            print(f"Error converting PDF to SVG: {e}")
            return False
    
    def simplify_svg(self, input_svg_path, output_svg_path):
        """
        Simplify an SVG file by converting objects to paths
        
        Args:
            input_svg_path (str): Path to the input SVG file
            output_svg_path (str): Path where to save the simplified SVG file
            
        Returns:
            bool: True if simplification was successful, False otherwise
        """
        try:
            command = [
                self.inkscape_path,
                input_svg_path,
                f"--export-plain-svg={output_svg_path}",
                "--actions=select-all;object-to-path"
            ]
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            return True
        except Exception as e:
            print(f"Error simplifying SVG: {e}")
            return False
            
    def pdf_page_to_simplified_svg(self, pdf_path, page_number, temp_svg_path=None, output_svg_path=None):
        """
        Convert a PDF page to a simplified SVG in one go
        
        Args:
            pdf_path (str): Path to the PDF file
            page_number (int): Page number to convert
            temp_svg_path (str, optional): Path for temporary SVG. If None, uses "temp_output.svg"
            output_svg_path (str, optional): Path for final SVG. If None, uses "simplified_page_{page_number}.svg"
            
        Returns:
            bool: True if both operations were successful, False otherwise
        """
        # Set default paths if not provided
        if temp_svg_path is None:
            temp_svg_path = f"temp_output.svg"
        if output_svg_path is None:
            output_svg_path = f"simplified_page_{page_number}.svg"
            
        # Step 1: Convert PDF page to SVG
        if not self.pdf_to_svg(pdf_path, page_number, temp_svg_path):
            return False
            
        # Step 2: Simplify SVG
        result = self.simplify_svg(temp_svg_path, output_svg_path)
        
        # Clean up temporary file
        try:
            if os.path.exists(temp_svg_path):
                os.remove(temp_svg_path)
        except Exception as e:
            print(f"Warning: Could not remove temporary file {temp_svg_path}: {e}")
            
        return result