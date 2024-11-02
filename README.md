# Myrient Downloader

**Myrient Downloader** is a Python-based application that allows users to effortlessly download ROM files from [Myrient](https://myrient.erista.me/). Built with a sleek, modern GUI using CustomTkinter, this program supports various file types and filters to enhance your downloading experience, providing granular control over which files to download.

---

## 🚀 Features

- **Universal File Support**: Download files of any type.
- **USA-Only Filter**: Enable an option to download only files marked `(USA)` or `(US)`.
- **Skip BIOS Files**: Automatically skips files labeled `[BIOS]` or `(BIOS)` by default, focusing only on ROMs.
- **Intuitive GUI**: User-friendly interface built with CustomTkinter.
- **Progress Tracking**: Track the downloading progress, including the current file and the total number of files.
- **Cancel Downloads**: Option to cancel the download process anytime during the download.

## 📋 Prerequisites

Ensure you have the following dependencies installed:
- **Python 3.7+**
- **CustomTkinter**
- **Requests**
- **BeautifulSoup4**

To install the required packages, run:
```
pip install customtkinter requests beautifulsoup4
```

## 🖥️ Usage

1. **Enter the URL**: Copy and paste the URL of the Myrient page containing the ROMs you want to download.
2. **Choose a Download Directory**: Select where you’d like the files to be saved.
3. **Filter Options**:
   - Enable "Download only USA games" if you want to download only files marked `(USA)` or `(US)`.
   - BIOS files marked `[BIOS]` or `(BIOS)` are automatically skipped.
4. **Scan and Confirm**: Click "Scan Page" to see the total number of files and their size, then confirm to start the download.
5. **Monitor Progress**: Track download progress, cancel if necessary, and view status updates.

## 📄 License

This project is licensed under the MIT License.

---

Happy downloading! If you encounter any issues or have suggestions, please feel free to open an issue or contribute to the project.