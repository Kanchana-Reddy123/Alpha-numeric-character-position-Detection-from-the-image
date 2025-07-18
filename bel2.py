from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import pytesseract
import math

# === Set path to tesseract.exe (for Windows users only) ===
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# === GUI Setup ===
root = Tk()
root.title("Alphanumeric Character Position Detection")
root.geometry("800x600")

img_label = Label(root)
img_label.pack()

img_cv = None  # Global variable to hold the image

# === Direction Calculation Function ===
def get_direction(angle):
    if 22.5 <= angle < 67.5:
        return "North-East"
    elif 67.5 <= angle < 112.5:
        return "North"
    elif 112.5 <= angle < 157.5:
        return "North-West"
    elif 157.5 <= angle < 202.5:
        return "West"
    elif 202.5 <= angle < 247.5:
        return "South-West"
    elif 247.5 <= angle < 292.5:
        return "South"
    elif 292.5 <= angle < 337.5:
        return "South-East"
    else:
        return "East"

# === Upload Image Function ===
def upload_image():
    global img_cv
    file_path = filedialog.askopenfilename()
    if not file_path:
        return
    img_cv = cv2.imread(file_path)
    if img_cv is None:
        print("Failed to load image.")
        return

    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_pil.thumbnail((500, 500))
    img_tk = ImageTk.PhotoImage(img_pil)
    img_label.configure(image=img_tk)
    img_label.image = img_tk

# === Analyze Image Function ===
def analyze_image():
    global img_cv
    if img_cv is None:
        print("Please upload an image first.")
        return

    h, w, _ = img_cv.shape
    center_x, center_y = w // 2, h // 2

    # Convert to grayscale and apply preprocessing
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Get bounding boxes from Tesseract (with proper config)
    custom_config = r'--oem 3 --psm 6'
    boxes = pytesseract.image_to_boxes(thresh, config=custom_config)
    lines = boxes.strip().splitlines()

    if not lines:
        print("No characters detected.")
        return

    # Create result window
    result_window = Toplevel(root)
    result_window.title("Character Position Analysis")
    result_window.geometry("500x400")
    text = Text(result_window, wrap=WORD)
    text.pack(expand=True, fill=BOTH)

    for b in lines:
        parts = b.split()
        if len(parts) < 6:
            continue
        char = parts[0]
        x1, y1, x2, y2 = int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])

        # Adjust y-coordinates because pytesseract origin is bottom-left
        y1 = h - y1
        y2 = h - y2
        mid_x = (x1 + x2) // 2
        mid_y = (y1 + y2) // 2

        dx = mid_x - center_x
        dy = center_y - mid_y  # Y-axis inversion for screen

        angle = math.degrees(math.atan2(dy, dx)) % 360
        direction = get_direction(angle)

        if char.isalnum():
            result = f"Character: {char} | Direction: {direction} | Angle: {round(angle, 2)}°\n"
            print(result.strip())
            text.insert(END, result)

# === Buttons ===
upload_btn = Button(root, text="Upload Image", command=upload_image, font=("Arial", 12), bg="lightblue")
upload_btn.pack(pady=10)

analyze_btn = Button(root, text="Analyze", command=analyze_image, font=("Arial", 12), bg="lightgreen")
analyze_btn.pack(pady=10)

# === Mainloop ===
root.mainloop()


