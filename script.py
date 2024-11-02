import customtkinter as ctk
import requests
from bs4 import BeautifulSoup
import os
import urllib.request
from urllib.parse import urljoin
from tkinter import filedialog, messagebox, IntVar
import logging
import re
import threading

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set the appearance mode and color theme for customtkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Global variable to control cancellation
cancel_download = False

# Create the main GUI root
root = ctk.CTk()
root.title("Myrient Downloader")
root.geometry("800x250")

# Variable to control "Only USA" filter
only_usa_var = IntVar(root, value=0)  # 0 = unchecked, 1 = checked


def parse_file_size(size_str):
    size_str = size_str.strip().upper()
    match = re.match(r"(\d+(\.\d+)?)\s*(KIB|MIB|GIB|TIB|KI|MI|GI|TI|KB|MB|GB|TB)", size_str)
    if not match:
        logging.warning(f"Unknown size format: {size_str}")
        return 0
    size, _, unit = match.groups()
    size = float(size)

    if unit in ["KIB", "KB"]:
        return int(size * 1024)
    elif unit in ["MIB", "MB"]:
        return int(size * 1024 ** 2)
    elif unit in ["GIB", "GB"]:
        return int(size * 1024 ** 3)
    elif unit in ["TIB", "TB"]:
        return int(size * 1024 ** 4)

    return 0


def format_size(bytes_size):
    if bytes_size >= 1024 ** 4:
        size = bytes_size / (1024 ** 4)
        return f"{size:.2f} TiB"
    elif bytes_size >= 1024 ** 3:
        size = bytes_size / (1024 ** 3)
        return f"{size:.2f} GiB"
    elif bytes_size >= 1024 ** 2:
        size = bytes_size / (1024 ** 2)
        return f"{size:.2f} MiB"
    else:
        size = bytes_size / 1024
        return f"{size:.2f} KiB"


def crawl_page(page_url):
    logging.info("Crawling the page for files...")
    response = requests.get(page_url)
    if response.status_code != 200:
        messagebox.showerror("Error", "Failed to retrieve page.")
        logging.error(f"Failed to retrieve page: {page_url}")
        return [], 0

    soup = BeautifulSoup(response.text, 'html.parser')
    file_data = []
    total_size = 0
    for row in soup.find_all("tr"):
        link = row.find("a", href=True)

        # Skip rows without a valid link or with non-file text in the link
        if not link or "parent directory" in link.text.lower() or "file name" in link.text.lower():
            logging.info(f"Skipping non-file entry: {link.text if link else 'No link'}")
            continue

        filename = link.text.strip()

        # Skip files marked as BIOS, Beta, or Demo
        if "BETA" in filename.upper() or "BIOS" in filename.upper() or "DEMO" in filename.upper():
            logging.info(f"Skipping unwanted file: {filename}")
            continue

        # Apply the USA filter if the checkbox is checked
        if only_usa_var.get() == 1 and not re.search(r"\b(USA|US)\b", filename, re.IGNORECASE):
            logging.info(f"Skipping non-USA file: {filename}")
            continue

        file_url = urljoin(page_url, link['href'])
        size_td = link.find_next("td")
        if size_td:
            size_text = size_td.text.strip()
            size_in_bytes = parse_file_size(size_text)
            total_size += size_in_bytes
            file_data.append((filename, file_url, size_in_bytes))
            logging.info(f"Found file: {filename} - Size: {format_size(size_in_bytes)}")
        else:
            logging.warning(f"Could not find size for {filename}")

    logging.info(f"Total files found: {len(file_data)}")
    return file_data, total_size


def sanitize_filename(filename):
    # Replace invalid characters with underscores and ensure there are no trailing periods
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename).rstrip(". ")
    return sanitized


def download_file(file_url, download_dir, filename):
    if cancel_download:
        return 0, 0  # Return if download was canceled

    # Sanitize the filename to prevent issues with invalid characters
    safe_filename = sanitize_filename(filename)
    local_filename = os.path.join(download_dir, safe_filename)

    # Ensure the download directory exists
    os.makedirs(download_dir, exist_ok=True)

    # Download the file
    urllib.request.urlretrieve(file_url, local_filename)
    return os.path.getsize(local_filename), 0


def download_files(file_data, download_dir, progress_label):
    global cancel_download
    total_files = len(file_data)

    # Get the starting file index from the input (convert to zero-based index)
    try:
        start_index = int(start_entry.get()) - 1
        if start_index < 0 or start_index >= total_files:
            start_index = 0  # Reset if out of bounds
    except ValueError:
        start_index = 0  # Default to start from the beginning if input is invalid

    for index, (filename, file_url, file_size) in enumerate(file_data[start_index:], start=start_index + 1):
        if cancel_download:
            progress_label.configure(text="Download canceled")
            break

        current_file_label = f"Downloading: {filename} ({index}/{total_files})"
        progress_label.configure(text=current_file_label)

        download_file(file_url, download_dir, filename)

    if not cancel_download:
        progress_label.configure(text="Download Complete")

    enable_ui_elements()


def start_download_thread(file_data, download_dir, progress_label):
    global cancel_download
    cancel_download = False
    download_thread = threading.Thread(target=download_files, args=(file_data, download_dir, progress_label))
    download_thread.start()


def confirm_and_download():
    global cancel_download
    if scan_button.cget("text") == "Cancel":
        cancel_download = True
        progress_label.configure(text="Canceling download...")
        return

    page_url = url_entry.get().strip()
    download_dir = download_dir_entry.get().strip()

    if not page_url:
        messagebox.showerror("Error", "Please enter the page URL.")
        logging.error("No page URL provided.")
        return

    if not download_dir:
        messagebox.showerror("Error", "Please select a download directory.")
        logging.error("No download directory selected.")
        return

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    file_data, total_size = crawl_page(page_url)
    file_count = len(file_data)

    if file_count == 0:
        messagebox.showinfo("No Files", "No matching files found on the page.")
        logging.info("No matching files found on the page.")
        return

    readable_size = format_size(total_size)
    logging.info(f"Number of files to be downloaded: {file_count}")
    logging.info(f"Total size of all files: {readable_size}")

    confirm = messagebox.askyesno(
        "Confirm Download",
        f"Number of files: {file_count}\nTotal size of files: {readable_size}\n\nDo you want to start the download?"
    )

    if confirm:
        disable_ui_elements()
        progress_label.configure(text="Starting download...")
        scan_button.configure(text="Cancel")
        start_download_thread(file_data, download_dir, progress_label)


def disable_ui_elements():
    url_entry.configure(state="disabled")
    download_dir_entry.configure(state="disabled")
    browse_button.configure(state="disabled")
    usa_only_checkbox.configure(state="disabled")


def enable_ui_elements():
    url_entry.configure(state="normal")
    download_dir_entry.configure(state="normal")
    browse_button.configure(state="normal")
    usa_only_checkbox.configure(state="normal")
    scan_button.configure(text="Scan Page")


def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        download_dir_entry.delete(0, ctk.END)
        download_dir_entry.insert(0, directory)


# Frame for URL entry and directory selection
frame = ctk.CTkFrame(root)
frame.pack(padx=20, pady=10, fill="both", expand=True)

# URL Entry
url_label = ctk.CTkLabel(frame, text="Page URL:")
url_label.grid(row=0, column=0, sticky="e", padx=(10, 5), pady=(10, 5))
url_entry = ctk.CTkEntry(frame, width=600)
url_entry.grid(row=0, column=1, padx=(0, 10), pady=(10, 5), columnspan=2)

# Directory selection
download_dir_label = ctk.CTkLabel(frame, text="Download Directory:")
download_dir_label.grid(row=1, column=0, sticky="e", padx=(10, 5), pady=(0, 5))
download_dir_entry = ctk.CTkEntry(frame, width=500)
download_dir_entry.grid(row=1, column=1, padx=(0, 10), pady=(0, 5))
browse_button = ctk.CTkButton(frame, text="Browse...", command=select_directory, width=90)
browse_button.grid(row=1, column=2, padx=(0, 10), pady=(0, 5))

# USA Only Checkbox
usa_only_checkbox = ctk.CTkCheckBox(root, text="Download only USA games", variable=only_usa_var)
usa_only_checkbox.pack(pady=5)

# Progress label
progress_label = ctk.CTkLabel(root, text="Progress: Waiting to start")
progress_label.pack(pady=5)

# Scan Page / Cancel button
scan_button = ctk.CTkButton(root, text="Scan Page", command=confirm_and_download, width=300)
scan_button.pack(pady=10)

# Starting file number entry
start_label = ctk.CTkLabel(frame, text="Start from file number:")
start_label.grid(row=2, column=0, sticky="e", padx=(10, 5), pady=(0, 5))
start_entry = ctk.CTkEntry(frame, width=100)
start_entry.grid(row=2, column=1, padx=(0, 10), pady=(0, 5), sticky="w")
start_entry.insert(0, "1")  # Default to 1


# Start the GUI loop
root.mainloop()
