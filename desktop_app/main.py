import cv2
import os
import sys
from PIL import Image, ImageTk
import face_recognition
import datetime
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import tkinter.simpledialog as simpledialog
import json

# Import database config lokal
from desktop_database_config import DesktopDatabaseConfig

# Optional GFPGAN import dengan error handling
try:
    from gfpgan import GFPGANer
    GFPGAN_AVAILABLE = True
except ImportError:
    print("⚠️ GFPGAN not available - photos will not be enhanced")
    GFPGAN_AVAILABLE = False

class AbsensiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Absensi Face Recognition")
        self.root.geometry("900x700")

        # Inisialisasi GFPGAN jika tersedia
        if GFPGAN_AVAILABLE:
            try:
                self.gfpgan = GFPGANer(
                    model_path="https://github.com/TencentARC/GFPGAN/releases/download/v1.3.4/GFPGANv1.4.pth",
                    upscale=1,
                    arch="clean",
                    channel_multiplier=2,
                    bg_upsampler=None
                )
                print("✅ GFPGAN initialized")
            except Exception as e:
                print(f"⚠️ GFPGAN initialization failed: {e}")
                self.gfpgan = None
        else:
            self.gfpgan = None

        # Inisialisasi direktori
        self.data_dir = "data_wajah"
        self.log_dir = "log_absensi"
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

        # Inisialisasi database
        self.init_database()

        # Setup kamera
        self.cap = cv2.VideoCapture(0)

        # Video frame
        self.video_label = tk.Label(root)
        self.video_label.pack(pady=10)

        # Tombol-tombol kontrol
        self.create_buttons()

        # Face recognition setup
        self.known_face_encodings = []
        self.known_face_data = []  # Berisi nama, departemen, posisi
        self.load_known_faces()

        # Update video
        self.update_video()

    def init_database(self):
        """Inisialisasi koneksi database menggunakan desktop config"""
        try:
            self.conn, self.db_type = DesktopDatabaseConfig.get_connection()
            DesktopDatabaseConfig.init_tables(self.conn, self.db_type)
            print(f"✅ Database initialized: {self.db_type}")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Tidak dapat terhubung ke database: {e}")
            sys.exit(1)

    def create_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        daftar_button = tk.Button(
            button_frame, 
            text="Daftar Karyawan", 
            command=self.daftar_wajah,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12),
            padx=20
        )
        daftar_button.pack(side=tk.LEFT, padx=5)

        absensi_button = tk.Button(
            button_frame, 
            text="Absensi", 
            command=self.lakukan_absensi,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12),
            padx=20
        )
        absensi_button.pack(side=tk.LEFT, padx=5)

        # Info panel
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=10)
        
        info_label = tk.Label(
            info_frame, 
            text="Dashboard Web HR tersedia di: http://localhost:5000",
            font=("Arial", 10),
            fg="blue"
        )
        info_label.pack()

    def daftar_wajah(self):
        """Dialog pendaftaran karyawan dengan field tambahan"""
        dialog = EmployeeRegistrationDialog(self.root)
        if dialog.result:
            nama, departemen, posisi = dialog.result
            
            ret, frame = self.cap.read()
            if ret:
                face_locations = face_recognition.face_locations(frame)
                if face_locations:
                    top, right, bottom, left = face_locations[0]

                    # Perluasan bounding box
                    margin = 20
                    top = max(0, top - margin)
                    right = min(frame.shape[1], right + margin)
                    bottom = min(frame.shape[0], bottom + margin)
                    left = max(0, left - margin)

                    face_image = frame[top:bottom, left:right]
                    
                    # Simpan gambar wajah
                    image_path = os.path.join(self.data_dir, f"{nama}.jpg")
                    cv2.imwrite(image_path, face_image)
                    
                    # Dapatkan face encoding
                    face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
                    
                    # Simpan face encoding sebagai file
                    encoding_path = os.path.join(self.data_dir, f"{nama}_encoding.json")
                    with open(encoding_path, 'w') as f:
                        json.dump(face_encoding.tolist(), f)
                    
                    # Simpan ke database
                    try:
                        cursor = self.conn.cursor()
                        if self.db_type == 'postgresql':
                            cursor.execute('''
                                INSERT INTO karyawan (nama, departemen, posisi, face_encoding_path)
                                VALUES (%s, %s, %s, %s)
                            ''', (nama, departemen, posisi, encoding_path))
                        else:
                            cursor.execute('''
                                INSERT INTO karyawan (nama, departemen, posisi, face_encoding_path)
                                VALUES (?, ?, ?, ?)
                            ''', (nama, departemen, posisi, encoding_path))
                        
                        self.conn.commit()
                        messagebox.showinfo("Berhasil", f"Karyawan {nama} berhasil didaftarkan")
                        self.load_known_faces()
                        
                    except Exception as e:
                        messagebox.showerror("Database Error", f"Gagal menyimpan data: {e}")
                        
                else:
                    messagebox.showerror("Error", "Tidak ada wajah terdeteksi")

    def load_known_faces(self):
        """Load data wajah dan encoding dari database"""
        self.known_face_encodings = []
        self.known_face_data = []
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT nama, departemen, posisi, face_encoding_path FROM karyawan")
            employees = cursor.fetchall()
            
            for employee in employees:
                try:
                    if len(employee) == 4:  # PostgreSQL
                        nama, departemen, posisi, encoding_path = employee
                    else:  # SQLite fallback
                        nama, departemen, posisi, encoding_path = employee
                    
                    if encoding_path and os.path.exists(encoding_path):
                        with open(encoding_path, 'r') as f:
                            encoding = json.load(f)
                        
                        self.known_face_encodings.append(encoding)
                        self.known_face_data.append({
                            'nama': nama,
                            'departemen': departemen,
                            'posisi': posisi
                        })
                except Exception as e:
                    print(f"Error loading face for {employee[0]}: {e}")
                    
        except Exception as e:
            print(f"Error loading known faces: {e}")

    def lakukan_absensi(self):
        ret, frame = self.cap.read()
        if ret:
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                employee_data = None

                if True in matches:
                    first_match_index = matches.index(True)
                    employee_data = self.known_face_data[first_match_index]

                if employee_data:
                    tanggal = datetime.datetime.now().strftime("%Y-%m-%d")
                    jam = datetime.datetime.now().strftime("%H:%M:%S")

                    margin = 20
                    top = max(0, top - margin)
                    right = min(frame.shape[1], right + margin)
                    bottom = min(frame.shape[0], bottom + margin)
                    left = max(0, left - margin)

                    face_image = frame[top:bottom, left:right]

                    # Enhance dengan GFPGAN jika tersedia
                    if self.gfpgan:
                        try:
                            _, restored_faces, _ = self.gfpgan.enhance(face_image, has_aligned=False, only_center_face=True)
                            restored_face = restored_faces[0]
                            print("✅ Photo enhanced with GFPGAN")
                        except Exception as e:
                            restored_face = face_image
                            print(f"⚠️ GFPGAN enhancement failed: {e}")
                    else:
                        restored_face = face_image
                        print("📷 Using original photo (GFPGAN not available)")

                    log_image_path = os.path.abspath(os.path.join(
                        self.log_dir, 
                        f"{employee_data['nama']}_{tanggal}_{datetime.datetime.now().strftime('%H-%M-%S')}.jpg"
                    ))
                    cv2.imwrite(log_image_path, restored_face)

                    try:
                        cursor = self.conn.cursor()
                        if self.db_type == 'postgresql':
                            cursor.execute('''
                                INSERT INTO log_absensi (nama, departemen, posisi, tanggal, jam, path_gambar)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            ''', (
                                employee_data['nama'], 
                                employee_data['departemen'], 
                                employee_data['posisi'], 
                                tanggal, 
                                jam, 
                                log_image_path
                            ))
                        else:
                            cursor.execute('''
                                INSERT INTO log_absensi (nama, departemen, posisi, tanggal, jam, path_gambar)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (
                                employee_data['nama'], 
                                employee_data['departemen'], 
                                employee_data['posisi'], 
                                tanggal, 
                                jam, 
                                log_image_path
                            ))
                        
                        self.conn.commit()
                        
                    except Exception as e:
                        print(f"Database error: {e}")

                    messagebox.showinfo("Absensi", f"Absensi untuk {employee_data['nama']} berhasil")

    def update_video(self):
        ret, frame = self.cap.read()
        if ret:
            # Deteksi wajah dan gambar bounding box
            face_locations = face_recognition.face_locations(frame)
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((640, 480), Image.Resampling.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.root.after(10, self.update_video)

    def __del__(self):
        if hasattr(self, 'cap'):
            self.cap.release()
        if hasattr(self, 'conn'):
            self.conn.close()


class EmployeeRegistrationDialog:
    def __init__(self, parent):
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Pendaftaran Karyawan")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Pendaftaran Karyawan Baru", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Nama
        tk.Label(main_frame, text="Nama:", font=("Arial", 10)).pack(anchor="w")
        self.nama_entry = tk.Entry(main_frame, font=("Arial", 10), width=30)
        self.nama_entry.pack(pady=(0, 10), fill="x")
        
        # Departemen
        tk.Label(main_frame, text="Departemen:", font=("Arial", 10)).pack(anchor="w")
        self.departemen_var = tk.StringVar()
        departemen_combo = ttk.Combobox(main_frame, textvariable=self.departemen_var, 
                                       font=("Arial", 10), width=28)
        departemen_combo['values'] = ('IT', 'HR', 'Finance', 'Marketing', 'Operations', 'Sales')
        departemen_combo.pack(pady=(0, 10), fill="x")
        
        # Posisi
        tk.Label(main_frame, text="Posisi:", font=("Arial", 10)).pack(anchor="w")
        self.posisi_var = tk.StringVar()
        posisi_combo = ttk.Combobox(main_frame, textvariable=self.posisi_var, 
                                   font=("Arial", 10), width=28)
        posisi_combo['values'] = ('Manager', 'Senior Staff', 'Staff', 'Junior Staff', 'Intern')
        posisi_combo.pack(pady=(0, 20), fill="x")
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        cancel_btn = tk.Button(button_frame, text="Batal", command=self.cancel,
                              bg="#f44336", fg="white", font=("Arial", 10))
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        ok_btn = tk.Button(button_frame, text="Daftar", command=self.ok,
                          bg="#4CAF50", fg="white", font=("Arial", 10))
        ok_btn.pack(side=tk.RIGHT)
        
        # Focus on nama field
        self.nama_entry.focus()
    
    def ok(self):
        nama = self.nama_entry.get().strip()
        departemen = self.departemen_var.get().strip()
        posisi = self.posisi_var.get().strip()
        
        if not nama or not departemen or not posisi:
            messagebox.showerror("Error", "Semua field harus diisi!")
            return
        
        self.result = (nama, departemen, posisi)
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AbsensiApp(root)
    root.mainloop()
