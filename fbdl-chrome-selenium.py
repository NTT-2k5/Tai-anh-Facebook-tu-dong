#nuitka --standalone --onefile --enable-plugin=tk-inter --windows-console-mode=disable --include-data-dir=ttkthemes=ttkthemes
import os
import re
import io
import zipfile
import subprocess
import platform
import requests
import time
import winreg
import threading
import queue

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from ttkthemes import ThemedTk

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs

# ----------------- LANGUAGE STRINGS -----------------
LANG_TEXT = {
    'en': {
        'window_title': "Facebook Bulk Image Downloader",
        'language_label': "Select language:",
        'config_frame_title': "Configuration",
        'permalink_label': "Enter first image's Permalink URL here:",
        'save_check_label': "Save images to disk",
        'folder_label': "Folder Name:",
        'browse_button': "Browse...",
        'manual_login_label': "Manual Login",
        'manual_login_explanation': "Select \"Manual Login\" to download from private or friends-only posts. A browser will open for you to log in.\nFor public posts, you should leave it unchecked to avoid the risk of getting your Facebook account banned, program will run in headless mode (no visible browser).",
        'start_button_text': "  Start Download!  ",
        'stop_button_text': "  Stop Download!  ",
        'log_frame_title': "Activity Log",
        'status_ready': "Ready.",
        'chrome_not_found_title': "Google Chrome Not Found",
        'chrome_not_found_msg': "Google Chrome is not installed or could not be found.\n\nThis application requires Google Chrome to function.",
        'error_title': "Error",
        'url_empty_error': "Permalink URL cannot be empty.",
        'invalid_url_title': "Invalid URL Format",
        'invalid_url_msg': "The permalink URL is not in the expected format.\n\n"
                           "Below are two accepted formats:\n"
                           "https://www.facebook.com/photo/?fbid=*&set=pcb.*\n"
                           "https://www.facebook.com/photo/?fbid=*&set=pb.*.-*\n"
                           "(with asterisks stand for numbers)\n\n"
                           "Please copy the link of a single photo from an album or multi-photo post.",
        'status_starting': "Starting download process...",
        'login_dialog_title': "Manual Login Required",
        'login_dialog_msg': "A browser window has been opened.\n\nPlease log in to your Facebook account now.\n\nAfter you have successfully logged in, click 'OK' on this dialog to begin downloading.",
        'status_stopping': "Stopping...",
        'status_aborted': "Download aborted. Ready.",
        'status_finished': "Finished. Ready for next download.",
        'quit_dialog_title': "Quit",
        'quit_dialog_msg': "A download is in progress. Are you sure you want to quit?",
        # --- Downloader Process Strings ---
        'status_initializing_driver': "Initializing Google Chrome driver...",
        'log_headless_mode': "Running in headless mode (no browser window).",
        'log_headed_mode': "Running in headed mode for manual login.",
        'status_waiting_for_login': "Waiting for you to log in…",
        'log_login_prompt': "Please use the browser window to log in to Facebook.",
        'log_login_confirmed': "Login confirmation received. Continuing process…",
        'log_stop_requested': "Stop requested. Exiting.",
        'log_no_login_selected': "No login selected. Only public posts will be accessible.",
        'status_starting_scrape': "Starting scrape from {url}...",
        'log_saving_to_folder': "Saving images to folder: {folder}",
        'log_image_found': "\nImage {index}: {url}",
        'log_image_saved': "Saved {filename}",
        'status_navigating_next': "Navigating to next image... (Image {index})",
        'log_wrong_image_retry': "Wrong image, retrying...",
        'log_no_new_image': "No new image found; stopping.",
        'log_loop_detected': "Loop detected; download complete.",
        'log_pause_rate_limit': "Pausing for 3 seconds to avoid rate-limiting...",
        'log_error_occurred': "ERROR: {error_type} - {error_message}",
        'log_traceback': "Traceback:\n{traceback_data}",
        'log_post_not_available': "Post not available. It might not exist, or might be deleted or private, or you may need to log in to view it.",
    },
    'vi': {
        'window_title': "Chương trình Tải hàng loạt ảnh Facebook",
        'language_label': "Chọn ngôn ngữ:",
        'config_frame_title': "Thiết lập chương trình",
        'permalink_label': "Nhập link ảnh đầu tiên vào đây (URL):",
        'save_check_label': "Lưu ảnh vào máy tính",
        'folder_label': "Tên thư mục:",
        'browse_button': "Chọn...",
        'manual_login_label': "Đăng nhập thủ công",
        'manual_login_explanation': "Chọn \"Đăng nhập thủ công\" để tải bài đăng ở chế độ riêng tư hoặc bạn bè. Trình duyệt sẽ mở Facebook ra để bạn đăng nhập. Đối với bài đăng công khai thì không nên chọn để tránh nguy cơ bị khóa tài khoản Facebook, chương trình sẽ chạy ở chế độ ẩn cửa sổ trình duyệt.",
        'start_button_text': "  Bắt đầu tải ảnh!  ",
        'stop_button_text': "  Dừng tải ảnh!  ",
        'log_frame_title': "Nhật ký hoạt động (Log)",
        'status_ready': "Đang chờ thao tác...",
        'chrome_not_found_title': "Không tìm thấy Google Chrome",
        'chrome_not_found_msg': "Google Chrome chưa được cài đặt hoặc không thể tìm thấy.\n\nChương trình này yêu cầu Google Chrome để hoạt động.",
        'error_title': "Lỗi",
        'url_empty_error': "URL của ảnh không được để trống!",
        'invalid_url_title': "Định dạng link (URL) không hợp lệ!",
        'invalid_url_msg': "Link không đúng định dạng yêu cầu.\n\n"
                           "Dưới đây là hai định dạng hợp lệ:\n"
                           "https://www.facebook.com/photo/?fbid=*&set=pcb.*\n"
                           "https://www.facebook.com/photo/?fbid=*&set=pb.*.-*\n"
                           "(thay các dấu sao bằng dãy số)\n\n"
                           "Hãy sao chép liên kết của ảnh đầu tiên từ album hoặc bài đăng nhiều ảnh.",
        'status_starting': "Đang bắt đầu quá trình tải xuống...",
        'login_dialog_title': "Yêu cầu đăng nhập thủ công",
        'login_dialog_msg': "Đã mở cửa sổ trình duyệt.\n\nHãy đăng nhập vào tài khoản Facebook của bạn.\n\nSau khi đăng nhập thành công, hãy bấm vào 'OK' để bắt đầu quá trình tải xuống.",
        'status_stopping': "Đang dừng...",
        'status_aborted': "Đã hủy quá trình tải xuống. Sẵn sàng cho lần tải tiếp theo.",
        'status_finished': "Hoàn thành tải xuống. Sẵn sàng cho lần tải tiếp theo.",
        'quit_dialog_title': "Thoát chương trình",
        'quit_dialog_msg': "Quá trình tải xuống đang diễn ra. Bạn có chắc chắn muốn thoát không?",
        # --- Downloader Process Strings ---
        'status_initializing_driver': "Đang khởi tạo trình điều khiển Google Chrome...",
        'log_headless_mode': "Chạy ở chế độ ẩn (không có cửa sổ trình duyệt).",
        'log_headed_mode': "Chạy ở chế độ có cửa sổ để đăng nhập thủ công.",
        'status_waiting_for_login': "Đang chờ đăng nhập...",
        'log_login_prompt': "Hãy sử dụng cửa sổ trình duyệt để đăng nhập vào Facebook.",
        'log_login_confirmed': "Đã nhận được xác nhận đăng nhập. Tiếp tục...",
        'log_stop_requested': "Đã yêu cầu dừng. Đang thoát.",
        'log_no_login_selected': "Đã chọn không đăng nhập. Chỉ có thể truy cập các bài đăng công khai.",
        'status_starting_scrape': "Bắt đầu quét từ {url}...",
        'log_saving_to_folder': "Đang lưu ảnh vào thư mục: {folder}",
        'log_image_found': "\nẢnh số {index}: {url}",
        'log_image_saved': "Đã lưu {filename}",
        'status_navigating_next': "Đang chuyển đến ảnh tiếp theo... (Ảnh số {index})",
        'log_wrong_image_retry': "Sai ảnh, đang thử lại...",
        'log_no_new_image': "Không tìm thấy ảnh mới; đang dừng.",
        'log_loop_detected': "Phát hiện lặp lại ảnh đầu - tải xuống hoàn tất!",
        'log_pause_rate_limit': "Tạm dừng 3 giây để tránh quá tải...",
        'log_error_occurred': "ERROR: {error_type} - {error_message}",
        'log_traceback': "Traceback:\n{traceback_data}",
        'log_post_not_available': "Không thể truy cập bài đăng. Có thể bài đăng này đã bị xoá, hoặc không tồn tại, hoặc ở chế độ riêng tư, hoặc cần phải đăng nhập để xem.",
    }
}


# ----------------- AUXILIARY -----------------

MIN_IMAGE_WIDTH = 100

def get_fbid_from_url(url):
    parsed = urlparse(url)
    q = parse_qs(parsed.query)
    return q.get("fbid", [None])[0]
    
def is_chrome_installed():
    """Checks if Google Chrome is installed on the system."""
    if platform.system() == "Windows":
        # More robustly check the registry for Chrome's installation path
        try:
            for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                try:
                    key = winreg.OpenKey(hive, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
                    path, _ = winreg.QueryValueEx(key, None)
                    winreg.CloseKey(key)
                    if os.path.exists(path):
                        return True
                except OSError:
                    continue
            return False
        except Exception:
            return False # Return false if any error occurs during registry access
            
    elif platform.system() == "Darwin":  # macOS
        return os.path.exists("/Applications/Google Chrome.app")
        
    elif platform.system() == "Linux":
        import shutil
        return shutil.which("google-chrome") is not None
        
    return False

# ----------------- INTERFACE CLASS -----------------

class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("700x600") # Increased height for language selector
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.msg_queue = queue.Queue()
        self.driver = None
        self.download_thread = None
        self.login_event = None
        self.stop_event = threading.Event() # Stop anytime I want
        self.is_downloading = False

        # --- Language Support ---
        self.current_lang_code = tk.StringVar(value='en')
        self.texts = LANG_TEXT[self.current_lang_code.get()]

        # --- Style ---
        style = ttk.Style(self.root)
        # style.configure("TFrame", background="#efefef")
        # style.configure("TLabel", background="#efefef")
        # style.theme_use('clam')

        # --- Widgets ---
        self.create_widgets()
        self.change_language() # Set initial text
        
        self.root.after(100, self.process_queue)

    def change_language(self, event=None):
        """Updates the UI text based on the selected language."""
        selected_lang = self.lang_combo.get()
        #print(f"{selected_lang}")
        self.current_lang_code.set('vi' if selected_lang == "Tiếng Việt" else 'en')
        self.texts = LANG_TEXT[self.current_lang_code.get()]
        self.update_ui_text()

    def update_ui_text(self):
        """Applies the current language strings to all relevant widgets."""
        self.root.title(self.texts['window_title'])
        self.lang_label.config(text=self.texts['language_label'])
        self.input_frame.config(text=self.texts['config_frame_title'])
        self.url_label.config(text=self.texts['permalink_label'])
        self.save_check.config(text=self.texts['save_check_label'])
        self.folder_label.config(text=self.texts['folder_label'])
        self.browse_button.config(text=self.texts['browse_button'])
        self.manual_login_check.config(text=self.texts['manual_login_label'])
        self.explanation_label.config(text=self.texts['manual_login_explanation'])
        self.log_frame.config(text=self.texts['log_frame_title'])
        self.set_status(self.texts['status_ready'])
        
        # Update button text based on its current command
        if not self.is_downloading:
             self.start_button.config(text=self.texts['start_button_text'])
        else:
             self.start_button.config(text=self.texts['stop_button_text'])


    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Language Frame ---
        lang_frame = ttk.Frame(main_frame)
        lang_frame.pack(fill=tk.X, pady=(0, 10))
        self.lang_label = ttk.Label(lang_frame, text="Language:")
        self.lang_label.pack(side=tk.LEFT, padx=(0, 5))
        self.lang_combo = ttk.Combobox(lang_frame, values=["Tiếng Việt", "English"], state="readonly", width=12)
        # self.lang_combo.set("English")
        self.lang_combo.current(0)
        self.lang_combo.pack(side=tk.LEFT)
        self.lang_combo.bind("<<ComboboxSelected>>", self.change_language)

        # --- Input Frame ---
        self.input_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        self.input_frame.pack(fill=tk.X, pady=5)
        self.input_frame.grid_columnconfigure(1, weight=1) # Makes the entry box expand

        # 1. Permalink URL
        self.url_label = ttk.Label(self.input_frame, text="Permalink URL:")
        self.url_label.grid(row=0, column=0, columnspan=3, sticky="w", padx=5, pady=2)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(self.input_frame, textvariable=self.url_var, width=60)
        self.url_entry.grid(row=1, column=0, columnspan=3, sticky="we", padx=5, pady=(0, 10))
        
        # 2. Save images to disk
        self.save_var = tk.BooleanVar(value=True)
        self.save_check = ttk.Checkbutton(self.input_frame, text="Save images to disk", variable=self.save_var, command=self.toggle_folder_entry)
        self.save_check.grid(row=2, column=0, columnspan=3, sticky='w', padx=5, pady=2)

        # 3. Folder Name and Browse Button
        self.folder_label = ttk.Label(self.input_frame, text="Folder Name:")
        self.folder_label.grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.folder_var = tk.StringVar(value="facebook_images")
        self.folder_entry = ttk.Entry(self.input_frame, textvariable=self.folder_var)
        self.folder_entry.grid(row=3, column=1, sticky="we", padx=5, pady=2)
        self.browse_button = ttk.Button(self.input_frame, text="Browse...", command=self.browse_folder)
        self.browse_button.grid(row=3, column=2, padx=(5, 0), pady=2)

        # 4. Manual Login
        self.manual_login_var = tk.BooleanVar(value=False)
        self.manual_login_check = ttk.Checkbutton(self.input_frame, text="Manual Login", variable=self.manual_login_var)
        self.manual_login_check.grid(row=5, column=0, columnspan=3, sticky='w', padx=5, pady=(10,0))

        # 5. Explanation
        self.explanation_label = ttk.Label(self.input_frame, wraplength=600, justify=tk.LEFT)
        self.explanation_label.grid(row=6, column=0, columnspan=3, sticky='w', padx=5, pady=5)

        # --- Control Frame ---
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        self.start_button = ttk.Button(control_frame, text="Start Download", command=self.start_download)
        # self.start_button.place(x=435, y=300,width=230,height=50)
        self.start_button.pack()

        # --- Log Frame ---
        self.log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_area = scrolledtext.ScrolledText(self.log_frame, state='disabled', wrap=tk.WORD, height=1, font = ("Consolas",10))
        self.log_area.pack(fill=tk.BOTH, expand=True)

        # --- Status Bar ---
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w', padding=5)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def browse_folder(self):
        """Open a dialog to choose a folder and update the entry."""
        directory = filedialog.askdirectory(title=self.texts['folder_label'], initialdir=os.getcwd())
        if directory: # If the user selected a folder and didn't cancel
            self.folder_var.set(directory)
            
    def toggle_folder_entry(self):
        """Enable or disable the folder entry based on the checkbox."""
        new_state = 'normal' if self.save_var.get() else 'disabled'
        self.folder_entry.config(state=new_state)
        self.browse_button.config(state=new_state)
        
    def stop_download(self):
        """Signals the download thread to stop."""
        if self.download_thread and self.download_thread.is_alive():
            self.log("\nTermination signal sent to download process...\nĐã gửi tín hiệu dừng đến tiến trình tải xuống...")
            self.set_status(self.texts['status_stopping'])
            self.stop_event.set()
            self.start_button.config(state='disabled')
        
    def log(self, message):
        """Append a message to the log area."""
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + '\n')
        self.log_area.config(state='disabled')
        self.log_area.see(tk.END)

    def set_status(self, message):
        """Update the status bar."""
        self.status_var.set(message)

    def start_download(self):
        self.is_downloading = True
        if not is_chrome_installed():
            messagebox.showerror(
                self.texts['chrome_not_found_title'],
                self.texts['chrome_not_found_msg']
            )
            return
        
        url = self.url_var.get().strip()
        pattern = r"^https:\/\/(www\.)?facebook\.com\/photo\/?\?fbid=\d+&set=(?:pcb\.\d+|pb\.\d+\.-?\d+|gm\.\d+)(?:&[^=]+=[^&]*)*$"

        if not re.match(pattern, url):
            messagebox.showerror(
                self.texts['invalid_url_title'],
                self.texts['invalid_url_msg']
            )
            self.is_downloading = False
            return
        
        save_images = self.save_var.get()
        manual_login = self.manual_login_var.get()
        folder_name = self.folder_var.get().strip() if save_images else ""
        
        self.start_button.config(text=self.texts['stop_button_text'], command=self.stop_download)
        self.set_status(self.texts['status_starting'])
        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END) # Clear previous log
        self.log_area.config(state='disabled')

        self.login_event = threading.Event()

        self.stop_event.clear()
        self.download_thread = threading.Thread(
            target=run_download_process,
            # Pass the `texts` dictionary to the thread
            args=(url, save_images, folder_name, manual_login, self.login_event, self.stop_event, self.msg_queue, self.texts),
            daemon=True
        )
        self.download_thread.start()

    def show_login_dialog(self):
        """Show a blocking dialog and set the event when it's closed."""
        messagebox.showinfo(
            self.texts['login_dialog_title'],
            self.texts['login_dialog_msg']
        )
        self.login_event.set() # Signal the worker thread to continue

    def process_queue(self):
        """Process messages from the worker thread's queue."""
        try:
            message = self.msg_queue.get_nowait()
            if message.startswith("log:"):
                self.log(message[4:])
            elif message.startswith("status:"):
                self.set_status(message[7:])
            elif message == "show_login_dialog":
                self.show_login_dialog()
            elif message == "DONE":
                self.is_downloading = False
                # Check if the process was stopped by the user
                if self.stop_event.is_set():
                    self.set_status(self.texts['status_aborted'])
                else:
                    self.set_status(self.texts['status_finished'])
                # Reset the button to its original "Start Download" state
                self.start_button.config(
                    text=self.texts['start_button_text'],
                    command=self.start_download,
                    state='normal'
                )
                self.driver = None # Clear driver reference
            elif message.startswith("driver:"):
                # This is not used anymore for quit, but kept for potential future use
                self.driver = message.split(":", 1)[1]

        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)

    def on_closing(self):
        """Handle the window closing event."""
        if self.download_thread and self.download_thread.is_alive():
            if messagebox.askokcancel(self.texts['quit_dialog_title'], self.texts['quit_dialog_msg']):
                self.stop_event.set()
                self.download_thread.join(timeout=5)
                self.root.destroy()
        else:
            self.root.destroy()


# ----------------- DOWNLOAD PROCESS -----------------

def run_download_process(first_link, save, folder, manual_login, login_event, stop_event, msg_queue, texts):
    """
    This function contains the core Selenium logic and is executed in a separate thread.
    It communicates with the GUI via the message queue using language-neutral keys.
    """
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager

    driver = None
    try:
        # Use the `texts` dictionary for messages
        msg_queue.put(f"status:{texts['status_initializing_driver']}")
        
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("ignore-certificate-errors")
        
        # Conditionally enable headless mode
        if not manual_login:
            msg_queue.put(f"log:{texts['log_headless_mode']}")
            chrome_options.add_argument("--headless")
        else:
            msg_queue.put(f"log:{texts['log_headed_mode']}")
            
        #chrome_options.add_argument("--window-size=1920,1080")
        if stop_event.is_set():
            return
        
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options
        )

        wait = WebDriverWait(driver, 20)
        if stop_event.is_set():
            return
            
        # Handle login flow
        if manual_login:
            msg_queue.put(f"status:{texts['status_waiting_for_login']}")
            msg_queue.put(f"log:{texts['log_login_prompt']}")
            driver.get("https://www.facebook.com")
            msg_queue.put("show_login_dialog")

            # ---- replace single-blocking wait with a loop ----
            while True:
                if login_event.wait(timeout=0.2):
                    msg_queue.put(f"log:{texts['log_login_confirmed']}")
                    break
                if stop_event.is_set():
                    msg_queue.put(f"log:{texts['log_stop_requested']}")
                    return
        else:
            msg_queue.put(f"log:{texts['log_no_login_selected']}")
            # Visiting the page once can help with setting initial state/cookies
            driver.get("https://www.facebook.com") 

        # --- Image Scraping Logic ---
        msg_queue.put(f"status:{texts['status_starting_scrape'].format(url=first_link[:30])}")
        if save:
            folder = folder.replace('"','')
            os.makedirs(folder, exist_ok=True)
            msg_queue.put(f"log:{texts['log_saving_to_folder'].format(folder=folder)}")

        driver.get(first_link)
        if stop_event.is_set():
            return
        time.sleep(2)
        
        error_containers = driver.find_elements(By.CSS_SELECTOR, "div.x78zum5.xdt5ytf.x4cne27.xifccgj")
        if error_containers:
            error_phrase_en = "isn't available"
            error_phrase_vi = "hiển thị"

            for container in error_containers:
                container_text = container.text
                #print(f"{container_text}")
                if error_phrase_en in container_text or error_phrase_vi in container_text:
                    msg_queue.put(f"log:{texts['log_post_not_available']}")
                    return

        def remove_login_banner():
            try:
                banner_close_buttons = driver.find_elements(By.CSS_SELECTOR, "div[aria-label='Close'], i[class*='close']")
                if banner_close_buttons:
                    banner_close_buttons[0].click()
                    time.sleep(0.5)
            except Exception: pass
            try:
                driver.execute_script("var el = document.querySelector('div.__fb-light-mode.x1n2onr6.xzkaem6'); if(el) el.remove();")
                time.sleep(0.5)
            except Exception: pass

        def get_main_image_src():
            try:
                # Find the main content area of the image viewer.
                main_area = driver.find_element(By.CSS_SELECTOR, 'div[role="main"]')
                imgs = main_area.find_elements(By.CSS_SELECTOR, 'img[src*="fbcdn"]')
                if not imgs: 
                    return None
                img_sizes = [(img, driver.execute_script("return arguments[0].naturalWidth;", img)) for img in imgs]
                large_imgs = [(img, w) for img, w in img_sizes if w >= MIN_IMAGE_WIDTH]
                candidates = large_imgs if large_imgs else img_sizes
                return max(candidates, key=lambda p: p[1])[0].get_attribute('src') if candidates else None
            except Exception:
                return None

        def download_image(url, index, dl_folder):
            r = requests.get(url, stream=True)
            r.raise_for_status()
            fname = f"{index:03}.jpg"
            path = os.path.join(dl_folder, fname)
            with open(path, 'wb') as f:
                for chunk in r.iter_content(1024): f.write(chunk)
            msg_queue.put(f"log:{texts['log_image_saved'].format(filename=fname)}")

        remove_login_banner()
        seen, idx, prev_src = set(), 1, None
        
        time.sleep(1)
        curr_src = get_main_image_src()
        if stop_event.is_set():
            return
        if curr_src:
            seen.add(get_fbid_from_url(driver.current_url))
            msg_queue.put(f"log:{texts['log_image_found'].format(index=idx, url=curr_src)}")
            if save: download_image(curr_src, idx, folder)
            prev_src = curr_src
            idx += 1
        
        while True:
            if stop_event.is_set():
                break
            msg_queue.put(f"status:{texts['status_navigating_next'].format(index=idx)}")
            
            next_button_locator = (By.CSS_SELECTOR, 'div[aria-label*="Next"], div[aria-label*="next"]')
            btn = wait.until(EC.element_to_be_clickable(next_button_locator))
            driver.execute_script("arguments[0].click();", btn)

            time.sleep(0.5)
            remove_login_banner()
            
            new_src, timeout = None, time.time() + 10
            while time.time() < timeout:
                src = get_main_image_src()
                if src and src != prev_src:
                    if '.php' not in src:
                        new_src = src
                        break
                    else:
                         msg_queue.put(f"log:{texts['log_wrong_image_retry']}")
                time.sleep(0.5)
            
            if not new_src:
                msg_queue.put(f"log:{texts['log_no_new_image']}")
                break

            fbid = get_fbid_from_url(driver.current_url)
            if fbid in seen:
                msg_queue.put(f"log:{texts['log_loop_detected']}")
                break
            
            seen.add(fbid)
            prev_src = new_src
            msg_queue.put(f"log:{texts['log_image_found'].format(index=idx, url=new_src)}")
            if save: download_image(new_src, idx, folder)
            idx += 1
            if (idx - 1) % 5 == 0:
                if stop_event.is_set():
                    break
                msg_queue.put(f"log:{texts['log_pause_rate_limit']}")
                time.sleep(3)

    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        msg_queue.put(f"log:{texts['log_error_occurred'].format(error_type=error_type, error_message=error_message)}")
        import traceback
        traceback_data = traceback.format_exc()
        msg_queue.put(f"log:{texts['log_traceback'].format(traceback_data=traceback_data)}")
    finally:
        if driver:
            driver.quit()
        msg_queue.put("DONE")


# ----------------- PROGRAM LAUNCH -----------------
if __name__ == '__main__':
    root = ThemedTk(theme="plastik", gif_override=True)
    app = DownloaderApp(root)
    root.mainloop()