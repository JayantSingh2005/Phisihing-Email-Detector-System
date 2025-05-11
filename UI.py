import tkinter as tk
from tkinter import messagebox
import requests

class PhishingDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phishing Email Detector")
        self.root.geometry("800x500")
        
        # Default theme is dark
        self.is_dark_mode = True
        
        # Initialize all widgets first
        self.initialize_widgets()

        # Apply theme after widget initialization
        self.set_theme()

    def initialize_widgets(self):
        # Frame for the main content and history log
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(side="left", fill="both", expand=True, padx=10, pady=20)

        self.history_frame = tk.Frame(self.root)
        self.history_frame.pack(side="right", fill="y", padx=10, pady=20)

        # Title Label
        self.title_label = tk.Label(self.main_frame, text="Email Phishing Detector", font=("Segoe UI", 18, "bold"))
        self.title_label.pack(pady=10)

        # Email Body Label
        self.label = tk.Label(self.main_frame, text="Enter Email Body:", font=("Segoe UI", 12))
        self.label.pack(pady=5)

        # Textbox for entering email body
        self.email_body = tk.Text(self.main_frame, height=10, width=45, font=("Segoe UI", 12), bd=0, wrap=tk.WORD)
        self.email_body.pack(pady=10)

        # Button to predict phishing
        self.predict_button = tk.Button(self.main_frame, text="Predict", font=("Segoe UI", 12), command=self.predict_phishing, relief="flat")
        self.predict_button.pack(pady=10)

        # Result Label
        self.result_label = tk.Label(self.main_frame, text="", font=("Segoe UI", 12))
        self.result_label.pack(pady=5)

        # Toggle Button for Dark/Light Mode
        self.toggle_button = tk.Button(self.main_frame, text="Toggle Mode", font=("Segoe UI", 12), command=self.toggle_mode, relief="flat")
        self.toggle_button.pack(pady=10)

        # History Label
        self.history_label = tk.Label(self.history_frame, text="Prediction History", font=("Segoe UI", 14, "bold"))
        self.history_label.pack(pady=10)

        # Scrollable history log area
        self.history_log = tk.Listbox(self.history_frame, height=15, width=50, font=("Segoe UI", 12), bd=0, selectmode=tk.SINGLE)
        self.history_log.pack(pady=5)

        # Add scrollbar to history log
        self.scrollbar = tk.Scrollbar(self.history_frame, orient="vertical", command=self.history_log.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.history_log.config(yscrollcommand=self.scrollbar.set)

    def set_theme(self):
        if self.is_dark_mode:
            self.bg_color = "#1e1e1e"  # Dark mode background color
            self.text_fg = "#ffffff"    # White text for dark mode
            self.title_fg = "#FF6347"   # Orange title color
            self.textbox_bg_color = "#333333"  # Darker text area background
            self.button_bg = "#FF6347"  # Button background color
        else:
            self.bg_color = "#f5f5f5"  # Light mode background color
            self.text_fg = "#000000"    # Black text for light mode
            self.title_fg = "#008CBA"   # Blue title color
            self.textbox_bg_color = "#ffffff"  # Light text area background
            self.button_bg = "#008CBA"  # Button background color

        # Apply the theme colors to all widgets
        self.root.configure(bg=self.bg_color)
        self.title_label.config(bg=self.bg_color, fg=self.title_fg)
        self.label.config(bg=self.bg_color, fg=self.text_fg)
        self.email_body.config(bg=self.textbox_bg_color, fg=self.text_fg)
        self.predict_button.config(bg=self.button_bg, fg=self.text_fg)
        self.result_label.config(bg=self.bg_color, fg=self.text_fg)
        self.history_label.config(bg=self.bg_color, fg=self.title_fg)
        self.history_log.config(bg=self.textbox_bg_color, fg=self.text_fg)
        self.scrollbar.config(bg=self.bg_color)

        # Update background color for frames
        self.main_frame.config(bg=self.bg_color)
        self.history_frame.config(bg=self.bg_color)

    def toggle_mode(self):
        # Toggle between dark and light mode
        self.is_dark_mode = not self.is_dark_mode
        self.set_theme()

    def predict_phishing(self):
        # Get email body text
        email_text = self.email_body.get("1.0", tk.END).strip()

        if not email_text:
            messagebox.showwarning("Input Error", "Please enter an email body.")
            return

        # Send POST request to backend API (ensure this endpoint is correct)
        try:
            response = requests.post(
                "http://localhost:8000/predict",  # Ensure FastAPI is running at this endpoint
                json={"body": email_text}
            )
            response_data = response.json()

            if response.status_code == 200:
                prediction = response_data['prediction']
                confidence = response_data['confidence']
                result_text = f"Prediction: {prediction}\nConfidence: {confidence * 100:.2f}%"

                # Update the result label with prediction
                self.result_label.config(text=result_text, fg="green" if prediction == 'legitimate' else "red")

                # Add result to history log
                self.history_log.insert(tk.END, f"Email: {email_text[:30]}... | {prediction} | {confidence * 100:.2f}%")

            else:
                messagebox.showerror("Error", "Failed to get prediction from the backend.")
        except Exception as e:
            messagebox.showerror("Network Error", f"Error connecting to backend: {e}")

# Set up Tkinter window
root = tk.Tk()
app = PhishingDetectorApp(root)
root.mainloop()