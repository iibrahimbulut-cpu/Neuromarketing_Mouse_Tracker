import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from PIL import Image, ImageTk
import numpy as np
import cv2
import matplotlib.pyplot as plt
import google.generativeai as genai
import os
import time
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

MODEL_NAME = "gemini-flash-latest" 
API_KEY = "api key"
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    print(f"API Hatası: {e}")

class GuPie_App:
    def __init__(self, root):
        self.root = root
        self.root.title("GuPie v4.3 - Insight Explorer")
        self.root.geometry("480x550")
        
        try: self.root.iconbitmap("gupie.ico")
        except: pass
        
        self.image_queue = [] 
        self.current_index = 0 
        self.results_data = [] 
        self.generated_files = [] 
        
        self.current_mouse_data = []
        self.current_click_data = []
        self.is_recording = False
        self.original_image = None
        self.current_img_w = 0
        self.current_img_h = 0
        self.user_window = None

        tk.Label(root, text="GuPie v4.3", font=("Arial", 22, "bold"), fg="#D32F2F").pack(pady=10)
        tk.Label(root, text="GurmePack Insight Explorer", font=("Arial", 10, "bold"), fg="green").pack()
        
        f1 = tk.Frame(root, pady=5); f1.pack()
        self.btn_open_screen = tk.Button(f1, text="1. Kullanıcı Ekranını Başlat", command=self.open_user_screen, bg="#ddd", width=35)
        self.btn_open_screen.pack()
        
        f2 = tk.Frame(root, pady=5); f2.pack()
        self.btn_load = tk.Button(f2, text="2. Görselleri Yükle", command=self.load_images, width=35)
        self.btn_load.pack()
        self.lbl_count = tk.Label(f2, text="Seçilen: 0", fg="blue"); self.lbl_count.pack()
        
        f3 = tk.Frame(root, pady=5); f3.pack()
        self.btn_start = tk.Button(f3, text="3. Testi Başlat", command=self.start_sequence, state=tk.DISABLED, bg="green", fg="white", width=35)
        self.btn_start.pack()
        
        self.btn_analyze = tk.Button(root, text="4. GuPie Analizi Yap", command=self.analyze_all, state=tk.DISABLED, bg="#1976D2", fg="white", width=40, height=2)
        self.btn_analyze.pack(pady=20)
        
        self.lbl_status = tk.Label(root, text="Hazır.", fg="gray", wraplength=400)
        self.lbl_status.pack(side=tk.BOTTOM, pady=10)

    def open_user_screen(self):
        if self.user_window: return
        self.user_window = Toplevel(self.root)
        self.user_window.title("GuPie - Kullanıcı Ekranı")
        self.user_window.configure(bg="white")
        try: self.user_window.iconbitmap("gupie2.ico")
        except: pass
        
        w = self.user_window.winfo_screenwidth()
        h = self.user_window.winfo_screenheight()
        try: self.user_window.geometry(f"{w}x{h}+{w}+0") 
        except: self.user_window.geometry(f"{w}x{h}+0+0")
        self.user_window.attributes('-fullscreen', True)
        
        self.lbl_display = tk.Label(self.user_window, bg="white", cursor="cross")
        self.lbl_display.place(relx=0.5, rely=0.5, anchor="center") 
        self.lbl_display.bind("<Motion>", self.record_mouse)
        self.lbl_display.bind("<Button-1>", self.record_click) 
        
        self.btn_next = tk.Button(self.user_window, text="SONRAKİ >", command=self.finish_current_image, 
                                    font=("Arial", 12, "bold"), bg="#f0f0f0", fg="black", padx=15, pady=8)
        self.btn_next.place_forget() 
        self.lbl_status.config(text="Kullanıcı ekranı açıldı.")

    def load_images(self):
        paths = filedialog.askopenfilenames(filetypes=[("Görseller", "*.jpg;*.png;*.jpeg")])
        if paths:
            self.image_queue = list(paths)
            self.current_index = 0
            self.results_data = [] 
            self.btn_start.config(state=tk.NORMAL)
            self.lbl_count.config(text=f"Seçilen: {len(paths)} adet")
            self.lbl_status.config(text="Görseller yüklendi.")

    def start_sequence(self):
        if not self.user_window:
            messagebox.showerror("Hata", "Önce Kullanıcı Ekranını Açın!")
            return
        self.current_index = 0
        self.results_data = [] 
        self.prepare_next_image()

    def prepare_next_image(self):
        if self.current_index >= len(self.image_queue):
            self.end_whole_test()
            return
        self.lbl_display.config(image="")
        self.btn_next.place_forget() 
        self.is_recording = False
        self.lbl_status.config(text=f"Sıradaki: {self.current_index + 1}/{len(self.image_queue)} (3sn Bekleme Süresi Başlatıldı)")
        self.root.update()
        self.user_window.configure(cursor="watch") 
        self.root.after(3000, self.show_image) 

    def show_image(self):
        self.user_window.configure(cursor="arrow") 
        path = self.image_queue[self.current_index]
        self.original_image = Image.open(path)
        screen_w = self.user_window.winfo_screenwidth()
        screen_h = self.user_window.winfo_screenheight()
        img = self.original_image.copy()
        img.thumbnail((screen_w, screen_h), Image.Resampling.LANCZOS)
        
        self.current_img_w, self.current_img_h = img.size
        self.tk_image = ImageTk.PhotoImage(img)
        self.lbl_display.config(image=self.tk_image)
        self.btn_next.place(relx=1.0, rely=0.0, x=-30, y=30, anchor="ne")
        
        self.current_mouse_data = []
        self.current_click_data = []
        self.is_recording = True
        self.lbl_status.config(text=f"Gösteriliyor: {os.path.basename(path)}")

    def record_mouse(self, event):
        if self.is_recording and 0 <= event.x < self.current_img_w and 0 <= event.y < self.current_img_h:
            self.current_mouse_data.append((event.x, event.y))

    def record_click(self, event):
        if self.is_recording and 0 <= event.x < self.current_img_w and 0 <= event.y < self.current_img_h:
            self.current_click_data.append((event.x, event.y))

    def finish_current_image(self):
        self.is_recording = False
        data = {
            "path": self.image_queue[self.current_index],
            "points": self.current_mouse_data,
            "clicks": self.current_click_data,
            "orig_size": self.original_image.size,
            "disp_size": (self.current_img_w, self.current_img_h)
        }
        self.results_data.append(data)
        self.current_index += 1
        self.prepare_next_image()

    def end_whole_test(self):
        self.lbl_display.config(image="")
        self.btn_next.place_forget()
        self.lbl_status.config(text="Görseller işleniyor...")
        self.root.update()
        
        self.generated_files = [] 
        
        for item in self.results_data:
            path = item["path"]
            points = item["points"]
            clicks = item["clicks"]
            w_orig, h_orig = item["orig_size"]
            w_disp, h_disp = item["disp_size"]
            scale_x = w_orig / w_disp
            scale_y = h_orig / h_disp
            
            pil_img = Image.open(path).convert('RGB')
            orig_cv = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            real_points = [(int(x*scale_x), int(y*scale_y)) for x, y in points]
            real_clicks = [(int(x*scale_x), int(y*scale_y)) for x, y in clicks]

            heatmap_matrix = np.zeros((h_orig, w_orig), dtype=np.float32)
            for rx, ry in real_points:
                if 0 <= rx < w_orig and 0 <= ry < h_orig: heatmap_matrix[ry, rx] += 1
            if len(real_points) > 0:
                sigma = int(max(w_orig, h_orig) / 45) | 1
                heatmap_matrix = cv2.GaussianBlur(heatmap_matrix, (0, 0), sigmaX=sigma, sigmaY=sigma)
                heatmap_matrix = cv2.normalize(heatmap_matrix, None, 0, 255, cv2.NORM_MINMAX)
            hmap_color = cv2.applyColorMap(np.uint8(heatmap_matrix), cv2.COLORMAP_JET)
            if orig_cv.shape[:2] != hmap_color.shape[:2]:
                 hmap_color = cv2.resize(hmap_color, (orig_cv.shape[1], orig_cv.shape[0]))
            final_heatmap = cv2.addWeighted(orig_cv, 0.6, hmap_color, 0.4, 0)
            for cx, cy in real_clicks:
                cv2.drawMarker(final_heatmap, (cx, cy), (0, 255, 0), markerType=cv2.MARKER_TILTED_CROSS, markerSize=40, thickness=3)

            gaze_img = orig_cv.copy()
            gaze_img = cv2.addWeighted(gaze_img, 0.7, np.zeros_like(gaze_img), 0.3, 0)
            sampled = real_points[::15]
            for i in range(1, len(sampled)):
                cv2.line(gaze_img, sampled[i-1], sampled[i], (0, 255, 255), 2)
                cv2.circle(gaze_img, sampled[i], 10, (255, 0, 0), -1)
                cv2.putText(gaze_img, str(i), (sampled[i][0]-5, sampled[i][1]+5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            base = os.path.splitext(os.path.basename(path))[0]
            h_name = f"heatmap_{base}.jpg"
            g_name = f"gaze_{base}.jpg"
            cv2.imwrite(h_name, final_heatmap)
            cv2.imwrite(g_name, gaze_img)
            self.generated_files.append((h_name, g_name, base))

        self.lbl_status.config(text="Dosyalar hazır. Analiz bekleniyor.")
        self.btn_analyze.config(state=tk.NORMAL)
        messagebox.showinfo("Bitti", "Görseller işlendi. Analize başlayabilirsiniz.")

    def analyze_all(self):
        self.lbl_status.config(text="GuPie analizi başlatılıyor...")
        self.root.update()
        
        report = "--- GuPie v4.3 ANALİZ RAPORU ---\n\n"
        model = genai.GenerativeModel(MODEL_NAME)
        
        for h_path, g_path, name in self.generated_files:
            retry_count = 0
            success = False
            
            while retry_count < 5 and not success:
                try:
                    img = Image.open(h_path)
                    prompt = f"""
                    Sen uzman bir nöropazarlamacısın. Görsel: "{name}".
                    Sana bu ürünün "Heatmap" (Sıcaklık Haritası) görselini veriyorum.
                    
                    Analiz:
                    1. Odak Noktası: Müşteri en çok nereye bakmış?
                    2. Marka: Logo fark edilmiş mi?
                    3. Tavsiye: Tasarımı iyileştirmek için 1 öneri.
                    """
                    response = model.generate_content([prompt, img], safety_settings=safety_settings)
                    
                    report += f"### {name.upper()} ###\n"
                    if response.parts:
                        report += response.text
                    else:
                        report += "Boş yanıt alındı."
                    
                    report += "\n" + ("-"*40) + "\n\n"
                    success = True
                    self.lbl_status.config(text=f"{name} tamamlandı.")
                    self.root.update()
                    time.sleep(3)
                    
                except Exception as e:
                    # 429 = Hız Sınırı (Rate Limit)
                    if "429" in str(e):
                        wait_time = 20 
                        self.lbl_status.config(text=f"Hız sınırı! {wait_time}sn bekleniyor... ({name})")
                        self.root.update()
                        time.sleep(wait_time)
                        retry_count += 1
                    else:
                        report += f"{name} TEKNİK HATA: {e}\n\n"
                        success = True # Başka hataysa döngüyü kır
            
            if not success:
                report += f"### {name.upper()} ###\nANALİZ BAŞARISIZ (Çok fazla deneme yapıldı).\n\n"

        win = Toplevel(self.root)
        win.title("GuPie - Sonuç Raporu")
        win.geometry("700x600")
        try: win.iconbitmap("gupie.ico")
        except: pass
        txt = tk.Text(win, wrap=tk.WORD, padx=10, pady=10, font=("Arial", 11))
        scr = tk.Scrollbar(win, command=txt.yview); txt.configure(yscrollcommand=scr.set)
        scr.pack(side=tk.RIGHT, fill=tk.Y); txt.pack(expand=True, fill='both')
        txt.insert(tk.END, report)
        self.lbl_status.config(text="Analiz bitti.")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = GuPie_App(root)
        root.mainloop()
    except Exception as e:
        print(f"HATA: {e}")
        input()