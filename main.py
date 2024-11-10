import os
import yaml
from tkinter import Tk, Canvas, Button, filedialog, Frame
from pathlib import Path
from PIL import Image, ImageTk

class ImageCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Cropper")
        
        # Set desired crop size (fixed)
        self.target_width = 700
        self.target_height = 900

        # Initialize attributes for dragging
        self.rect = None
        self.image = None
        self.tk_image = None
        self.rect_start_x = self.rect_start_y = 0  # Offset within the rectangle during dragging

        # Load configuration
        self.output_folder = self.load_config()

        # Frame to hold the canvas and buttons
        self.main_frame = Frame(root)
        self.main_frame.pack(fill="both", expand=True)
        
        # Create and configure canvas
        self.canvas = Canvas(self.main_frame, cursor="cross", bg="gray")
        self.canvas.pack(fill="both", expand=True, side="top")

        # Frame for buttons at the bottom
        self.button_frame = Frame(root)
        self.button_frame.pack(side="bottom", fill="x", pady=10)

        # Add buttons for loading image and cropping
        self.load_button = Button(self.button_frame, text="Load Image", command=self.load_image)
        self.load_button.pack(side="left", padx=10, pady=10)
        
        self.crop_button = Button(self.button_frame, text="Crop and Save", command=self.crop_and_save, state="disabled")
        self.crop_button.pack(side="right", padx=10, pady=10)

        # Bind mouse events for dragging the rectangle
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.root.bind("<Configure>", self.resize_image)

    def load_config(self):
        # Load configuration from config.yaml
        config_path = Path("config.yaml")
        if config_path.is_file():
            with open(config_path, "r") as file:
                config = yaml.safe_load(file)
            output_folder = config.get("output_folder")
            if output_folder:
                return Path(output_folder)
        # Default to Downloads folder if not specified
        return Path.home() / "Downloads"

    def load_image(self):
        # Open file dialog to select an image
        file_path = filedialog.askopenfilename(title="Select an Image",
                                               filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
        if not file_path:
            return

        # Open the image and save the original dimensions
        self.image = Image.open(file_path)
        self.original_image = self.image.copy()
        self.update_image_display()

        # Enable crop button
        self.crop_button.config(state="normal")

        # Draw fixed-size rectangle (700x900) at the top-left corner
        self.rect_start_x, self.rect_start_y = 0, 0
        self.rect = self.canvas.create_rectangle(
            self.rect_start_x, self.rect_start_y, 
            self.rect_start_x + self.target_width, self.rect_start_y + self.target_height, 
            outline="red", width=2
        )

    def resize_image(self, event):
        # Resize the image to fit within the canvas dimensions while maintaining aspect ratio
        if self.image:
            canvas_width, canvas_height = self.canvas.winfo_width(), self.canvas.winfo_height()
            self.image = self.original_image.copy()
            self.image.thumbnail((canvas_width, canvas_height), Image.LANCZOS)
            self.update_image_display()

    def update_image_display(self):
        # Update the canvas with the resized image
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.delete("all")  # Clear canvas before redrawing image and rectangle
        self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")
        
        # Redraw the selection rectangle in the top-left with fixed 700x900 dimensions
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.rect_start_x, self.rect_start_y, 
            self.rect_start_x + self.target_width, self.rect_start_y + self.target_height, 
            outline="red", width=2
        )

    def on_button_press(self, event):
        # Record the starting position of the click relative to the rectangle's top-left corner
        x0, y0, x1, y1 = self.canvas.coords(self.rect)
        self.rect_start_x = x0
        self.rect_start_y = y0
        self.offset_x = event.x - x0
        self.offset_y = event.y - y0

    def on_mouse_drag(self, event):
        # Calculate the new position based on the initial offset
        new_x0 = event.x - self.offset_x
        new_y0 = event.y - self.offset_y

        # Limit rectangle movement to within canvas bounds
        new_x0 = max(0, min(self.canvas.winfo_width() - self.target_width, new_x0))
        new_y0 = max(0, min(self.canvas.winfo_height() - self.target_height, new_y0))

        # Update the rectangle's coordinates
        self.canvas.coords(self.rect, new_x0, new_y0, new_x0 + self.target_width, new_y0 + self.target_height)

    def crop_and_save(self):
        # Get the coordinates of the selection rectangle
        x0, y0, x1, y1 = map(int, self.canvas.coords(self.rect))

        # Scale coordinates back to the original image size
        scale_x = self.original_image.width / self.image.width
        scale_y = self.original_image.height / self.image.height
        x0, y0, x1, y1 = int(x0 * scale_x), int(y0 * scale_y), int(x1 * scale_x), int(y1 * scale_y)

        # Crop the selected region from the original image
        cropped_img = self.original_image.crop((x0, y0, x1, y1))

        # Resize the cropped image to the target dimensions using LANCZOS
        resized_img = cropped_img.resize((self.target_width, self.target_height), Image.LANCZOS)

        # Save the image to the configured output folder
        save_path = self.output_folder / "cropped_image.png"
        resized_img.show()
        resized_img.save(save_path)
        print(f"Image saved as '{save_path}'.")

# Run the GUI application
root = Tk()
app = ImageCropper(root)
root.mainloop()
