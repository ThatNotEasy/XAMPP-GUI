import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from functools import partial
from PIL import Image, ImageTk, ImageDraw
import configparser

class XAMPPControlPanel:
    ICON_SIZE = (40, 40)

    def __init__(self, master, config_file="config.ini"):
        self.master = master
        master.title("XAMPP Control Panel")
        master.geometry("700x600")

        # Read configuration from config.ini
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self.bg_original_image = Image.open("icons/bg.jpg")
        self.bg_image = self.resize_bg_image()
        self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)

        self.canvas = tk.Canvas(master, width=self.bg_width, height=self.bg_height)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image_tk, tags="bg_image")

        self.style = ttk.Style()
        self.style.configure("Custom.TFrame", background="#F0F0F0")

        self.circular_icons = {
            "Apache": self.create_circular_icon("icons/apache.png"),
            "Nginx": self.create_circular_icon("icons/nginx.png"),
            "FileZilla": self.create_circular_icon("icons/filezilla.png"),
            "Tomcat": self.create_circular_icon("icons/tomcat.png"),
            "MySQL": self.create_circular_icon("icons/mysql.png"),
        }

        self.create_widgets()

        master.bind("<Configure>", self.on_window_resize)

    def start_component(self, component):
        command = self.config[component]["start_command"].split()
        self.execute_command(component, command, True, f"{component} started successfully.")

    def stop_component(self, component):
        command = self.config[component]["stop_command"].split()
        self.execute_command(component, command, False, f"{component} stopped successfully.")

    def execute_command(self, component, command, running, success_message):
        try:
            subprocess.run(command, check=True)
            self.update_status(component, running)
            self.update_global_status()
            self.show_message(success_message)
        except subprocess.CalledProcessError:
            self.show_message(f"Failed to {'' if running else 'stop '} {component}.")

    def create_circular_icon(self, img_path):
        img = Image.open(img_path).resize(self.ICON_SIZE, Image.LANCZOS)
        mask = Image.new("L", self.ICON_SIZE, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, *self.ICON_SIZE), fill=255)
        img.putalpha(mask)
        return ImageTk.PhotoImage(img)

    def create_widgets(self):
        self.create_title_label()
        components = ["Apache", "Nginx", "FileZilla", "Tomcat", "MySQL"]
        self.create_component_widgets(components)

    def create_title_label(self):
        title_label = ttk.Label(self.master, text="XAMPP Status", font=("Arial", 20, "bold"))
        title_label.place(relx=0.5, rely=0.05, anchor="center")

    def create_component_widgets(self, components):
        self.status_labels = {}

        for i, component_name in enumerate(components):
            frame = self.create_component_frame(i)
            icon_label = self.create_icon_label(frame, component_name)
            label = self.create_component_label(frame, component_name)
            status_label = self.create_status_label(frame)
            btn_start, btn_stop = self.create_buttons(frame, component_name)

            self.status_labels[component_name] = status_label

    def create_component_frame(self, i):
        frame = ttk.Frame(self.master, padding="10", style="Custom.TFrame")
        frame.place(relx=0.1, rely=0.2 + i * 0.15, anchor="w")
        return frame

    def create_icon_label(self, frame, component_name):
        icon_label = ttk.Label(frame, image=self.circular_icons[component_name])
        icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 10))
        return icon_label

    def create_component_label(self, frame, component_name):
        label = ttk.Label(frame, text=component_name, font=("Arial", 14), style="Transparent.TLabel")
        label.grid(row=0, column=1, sticky="w")
        return label

    def create_status_label(self, frame):
        status_label = ttk.Label(frame, text="Stopped", foreground="red", font=("Arial", 12))
        status_label.grid(row=0, column=2, sticky="w", padx=10)
        return status_label

    def create_buttons(self, frame, component_name):
        btn_start = ttk.Button(frame, text="Start", command=partial(self.start_component, component_name), style="Start.TButton")
        btn_start.grid(row=1, column=1, pady=5, padx=(0, 5))

        btn_stop = ttk.Button(frame, text="Stop", command=partial(self.stop_component, component_name), style="Stop.TButton")
        btn_stop.grid(row=1, column=2, pady=5)

        return btn_start, btn_stop

    def update_status(self, component, running):
        self.status_labels[component].config(text="Running" if running else "Stopped", foreground="green" if running else "red")

    def update_global_status(self):
        all_statuses = [self.status_labels[component]["text"] for component in self.status_labels]
        title = "XAMPP Control Panel - " + ("Stopped" if "Stopped" in all_statuses else "Running")
        self.master.title(title)

    def show_message(self, message):
        messagebox.showinfo("XAMPP Control Panel", message)

    def on_window_resize(self, event):
        self.bg_image = self.resize_bg_image()
        self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)
        self.canvas.config(width=self.bg_width, height=self.bg_height)
        self.canvas.itemconfig(self.canvas.find_withtag("bg_image")[0], image=self.bg_image_tk)

    def resize_bg_image(self):
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        return self.bg_original_image.resize((width, height), Image.LANCZOS)

    @property
    def bg_width(self):
        return self.bg_image.width

    @property
    def bg_height(self):
        return self.bg_image.height

def main():
    root = tk.Tk()
    app = XAMPPControlPanel(root)

    root.iconbitmap("icons/xampp.ico")

    root.style = ttk.Style()
    root.style.configure("Start.TButton", background="green", foreground="white", font=("Arial", 10))
    root.style.configure("Stop.TButton", background="red", foreground="white", font=("Arial", 10))
    root.style.configure("Transparent.TLabel", background="#F0F0F0")

    root.mainloop()

if __name__ == "__main__":
    main()
