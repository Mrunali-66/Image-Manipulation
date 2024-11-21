import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QSlider, QComboBox
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image, ImageFilter, ImageEnhance


class ImageManipulationTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Manipulation Tool")
        self.setGeometry(100, 100, 1000, 700)

        # Main container
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        # Left side - Image Preview
        self.preview_layout = QVBoxLayout()
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.preview_layout.addWidget(self.image_label)

        # Right side - Controls
        self.controls_layout = QVBoxLayout()

        # Load Image Button
        load_btn = QPushButton("Load Image")
        load_btn.clicked.connect(self.load_image)
        self.controls_layout.addWidget(load_btn)

        # Resize Controls
        resize_layout = QHBoxLayout()
        self.width_slider = QSlider(Qt.Horizontal)
        self.width_slider.setRange(10, 2000)
        self.height_slider = QSlider(Qt.Horizontal)
        self.height_slider.setRange(10, 2000)

        resize_layout.addWidget(QLabel("Width:"))
        resize_layout.addWidget(self.width_slider)
        resize_layout.addWidget(QLabel("Height:"))
        resize_layout.addWidget(self.height_slider)
        self.controls_layout.addLayout(resize_layout)

        # Resize Button
        resize_btn = QPushButton("Resize Image")
        resize_btn.clicked.connect(self.resize_image)
        self.controls_layout.addWidget(resize_btn)

        # Filters Dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "No Filter",
            "Blur",
            "Contour",
            "Detail",
            "Edge Enhance",
            "Sharpen"
        ])
        self.controls_layout.addWidget(self.filter_combo)

        # Apply Filter Button
        filter_btn = QPushButton("Apply Filter")
        filter_btn.clicked.connect(self.apply_filter)
        self.controls_layout.addWidget(filter_btn)

        # Image Format Conversion
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "PNG",
            "JPEG",
            "BMP",
            "TIFF",
            "WebP"
        ])
        self.controls_layout.addWidget(self.format_combo)

        # Convert Format Button
        convert_btn = QPushButton("Convert Format")
        convert_btn.clicked.connect(self.convert_format)
        self.controls_layout.addWidget(convert_btn)

        # Brightness and Contrast Sliders
        brightness_layout = QHBoxLayout()
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(0, 200)
        self.brightness_slider.setValue(100)
        brightness_layout.addWidget(QLabel("Brightness:"))
        brightness_layout.addWidget(self.brightness_slider)
        self.controls_layout.addLayout(brightness_layout)

        contrast_layout = QHBoxLayout()
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(0, 200)
        self.contrast_slider.setValue(100)
        contrast_layout.addWidget(QLabel("Contrast:"))
        contrast_layout.addWidget(self.contrast_slider)
        self.controls_layout.addLayout(contrast_layout)

        # Adjust Button
        adjust_btn = QPushButton("Adjust Brightness/Contrast")
        adjust_btn.clicked.connect(self.adjust_image)
        self.controls_layout.addWidget(adjust_btn)

        # Save Button
        save_btn = QPushButton("Save Image")
        save_btn.clicked.connect(self.save_image)
        self.controls_layout.addWidget(save_btn)

        # Add layouts to main layout
        main_layout.addLayout(self.preview_layout)
        main_layout.addLayout(self.controls_layout)

        # Initialize variables
        self.original_image = None
        self.current_image = None

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image File",
            "",
            "Image Files (*.png *.jpg *.bmp *.tiff *.webp)"
        )

        if file_path:
            # Load with Pillow
            self.original_image = Image.open(file_path)
            self.current_image = self.original_image.copy()

            # Convert to Qt format for display
            self.display_image(self.current_image)

            # Set initial slider values
            self.width_slider.setValue(self.current_image.width)
            self.height_slider.setValue(self.current_image.height)

    def display_image(self, pil_image):
        # Convert PIL image to QPixmap
        img_rgb = pil_image.convert('RGB')
        data = img_rgb.tobytes('raw', 'RGB')
        qimg = QImage(data, pil_image.width, pil_image.height, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        # Scale pixmap to fit label while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            800, 600,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)

    def resize_image(self):
        if self.current_image:
            width = self.width_slider.value()
            height = self.height_slider.value()

            self.current_image = self.current_image.resize((width, height))
            self.display_image(self.current_image)

    def apply_filter(self):
        if self.current_image:
            filter_name = self.filter_combo.currentText()

            filter_map = {
                "No Filter": None,
                "Blur": ImageFilter.BLUR,
                "Contour": ImageFilter.CONTOUR,
                "Detail": ImageFilter.DETAIL,
                "Edge Enhance": ImageFilter.EDGE_ENHANCE,
                "Sharpen": ImageFilter.SHARPEN
            }

            filter_type = filter_map.get(filter_name)

            if filter_type:
                self.current_image = self.current_image.filter(filter_type)
                self.display_image(self.current_image)

    def convert_format(self):
        if self.current_image:
            format_ext = self.format_combo.currentText().lower()

            # Save dialog
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Image",
                f"converted_image.{format_ext}",
                f"{format_ext.upper()} Files (*.{format_ext})"
            )

            if save_path:
                self.current_image.save(save_path)

    def adjust_image(self):
        if self.current_image:
            # Get brightness and contrast values
            brightness_factor = self.brightness_slider.value() / 100
            contrast_factor = self.contrast_slider.value() / 100

            # Adjust brightness
            brightness_enhancer = ImageEnhance.Brightness(self.current_image)
            brightness_adjusted = brightness_enhancer.enhance(brightness_factor)

            # Adjust contrast
            contrast_enhancer = ImageEnhance.Contrast(brightness_adjusted)
            self.current_image = contrast_enhancer.enhance(contrast_factor)

            self.display_image(self.current_image)

    def save_image(self):
        if self.current_image:
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Image",
                "manipulated_image.png",
                "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
            )

            if save_path:
                self.current_image.save(save_path)


def main():
    app = QApplication(sys.argv)
    tool = ImageManipulationTool()
    tool.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()