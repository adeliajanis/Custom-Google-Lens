from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.core.window import Window
import webbrowser
import time
import os
import pyimgur
import io
import requests
from serpapi import GoogleSearch
from urllib.parse import quote

# === Konfigurasi ===
Window.size = (350, 400)
CLIENT_ID = "7b2e476a16d6132"
CLIENT_SECRET = "57d1deaffb170f412acbf68f0fa3e618a3f1c934"
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "a0bd45673d5baa5be277d388f6cfb8e432b3e895355e403ec9b7b9a7e8ac2a11")
KEYWORDS_FILE = "partname.txt"

# === Fungsi Utilitas ===
def load_keywords_from_file(file_path):
    """Memuat kata kunci dari file teks."""
    try:
        with open(file_path, 'r') as file:
            return {line.strip().lower() for line in file if line.strip()}
    except FileNotFoundError:
        print(f"File {file_path} tidak ditemukan. Pastikan file tersebut ada.")
        return set()

# Fungsi untuk mengekstrak kata kunci relevan
def extract_relevant_keyword(title, keywords):
    """Mengekstrak kata kunci yang relevan dari judul berdasarkan daftar kata kunci."""
    title_words = set(title.lower().split())
    matched_keywords = title_words.intersection(keywords)
    if matched_keywords:
        return " ".join(matched_keywords)
    return "Tidak ada kata kunci yang relevan ditemukan."

# Fungsi untuk membuat URL pencarian Google
def create_google_search_url(keyword):
    """Membuat URL pencarian Google dengan kata kunci tertentu."""
    encoded_keyword = quote(keyword)
    return f"https://www.google.com/search?q={encoded_keyword}%20united%20tractors%20connect"

# Fungsi untuk mengunggah gambar ke Imgur
def upload_to_imgur(image_stream, client_id, client_secret):
    """Mengunggah gambar ke Imgur dan mengembalikan URL."""
    try:
        im = pyimgur.Imgur(client_id, client_secret)
        uploaded_image = im.upload_image(image_stream)
        print(f"Gambar berhasil diunggah ke Imgur: {uploaded_image.link}")
        return uploaded_image.link
    except Exception as e:
        print(f"Terjadi kesalahan saat mengunggah gambar ke Imgur: {e}")
        return None

# Fungsi untuk mencari kata kunci menggunakan Google Lens
def find_keyword(image_url, api_key, keywords):
    """Melakukan pencarian Google Lens dan mengekstrak kata kunci yang relevan."""
    try:
        lens_search_params = {
            "engine": "google_lens",
            "url": image_url,
            "api_key": api_key,
        }
        lens_search = GoogleSearch(lens_search_params)
        lens_results = lens_search.get_dict().get("visual_matches", [])

        if lens_results:
            full_title = lens_results[0].get("title", "Tidak ada judul ditemukan")
            filter_keyword = extract_relevant_keyword(full_title, keywords)
            print("Kata Kunci yang Relevan:", filter_keyword)
            return filter_keyword
        else:
            print("Tidak ada hasil dari Google Lens.")
            return None
    except Exception as e:
        print(f"Terjadi kesalahan saat mencari keyword: {e}")
        return None

# Fungsi untuk melakukan pencarian di website
def search_in_website(search_url):
    """Melakukan pencarian di situs web berdasarkan URL."""
    try:
        response = requests.get(search_url, timeout=10)
        if response.status_code == 200:
            print("Hasil pencarian berhasil diambil.")
            print("URL:", search_url)
            webbrowser.open(search_url)
            print("URL dibuka di browser.")
        else:
            print("Gagal mengambil hasil pencarian. Status:", response.status_code)
    except requests.RequestException as e:
        print("Terjadi kesalahan saat melakukan pencarian di web:", e)

# Kelas aplikasi Kivy
class SimpleCameraApp(App):
    def build(self):
        # Layout utama
        layout = BoxLayout(orientation='vertical', padding=10, spacing=2)

        # Kamera
        self.camera = Camera(resolution=(640, 480), play=True, size_hint_y=0.8)
        layout.add_widget(self.camera)

        # Tombol untuk mengambil gambar dan mencari
        button = Button(text="Search", size_hint_y=0.1, background_color=(0, 0.5, 1, 1), color=(1, 1, 1, 1))
        button.bind(on_release=self.capture_photo)
        layout.add_widget(button)

        return layout

    def capture_photo(self, instance):
        # Capture image and save it to a temporary file
        filename = f"captured_image_{time.time()}.png"
        self.camera.export_to_png(filename)

        # Upload the image using the filename
        imgur_link = upload_to_imgur(filename, CLIENT_ID, CLIENT_SECRET)

        # Optionally, delete the temporary file after upload
        os.remove(filename)
        if imgur_link:
            # Muat kata kunci
            keywords = load_keywords_from_file(KEYWORDS_FILE)

            # Cari kata kunci relevan
            keyword = find_keyword(imgur_link, SERPAPI_KEY, keywords)
            if keyword and "Tidak ada kata kunci" not in keyword:
                # Buat URL pencarian dan buka di browser
                search_url = create_google_search_url(keyword)
                search_in_website(search_url)
            else:
                print("Tidak ada kata kunci yang relevan untuk pencarian.")
        else:
            print("Terjadi kesalahan dalam proses unggah gambar.")

if __name__ == "__main__":
    SimpleCameraApp().run()