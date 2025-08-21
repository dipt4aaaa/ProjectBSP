"""
Refactored Tkinter Application - menggunakan FaceRecognitionService
Aplikasi Tkinter tetap berjalan seperti biasa, tapi sekarang menggunakan service layer
"""
import cv2
import os
import sys
from PIL import Image, ImageTk
import datetime
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import tkinter.simpledialog as simpledialog

# Import service layer baru
from face_recognition_service import FaceRecognitionService

class AbsensiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Absensi Face Recognition")
        self.root.geometry("900x700")

        # Initialize face recognition service
        try:
            self.face_service = FaceRecognitionService()
            print("✅ Face Recognition Service initialized")
        except Exception as e:
            messagebox.showerror("Service Error", f"Tidak dapat menginisialisasi service: {e}")
            sys.exit(1)

        # Setup kamera
        self.cap = cv2.VideoCapture(0)

        # Video frame
        self.video_label = tk.Label(root)
        self.video_label.pack(pady=10)

        # Tombol-tombol kontrol
        self.create_buttons()

        # Update video
        self.update_video()

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

        # Tombol reload faces
        reload_button = tk.Button(
            button_frame, 
            text="Reload Faces", 
            command=self.reload_faces,
            bg="#FF9800",
            fg="white",
            font=("Arial", 12),
            padx=20
        )
        reload_button.pack(side=tk.LEFT, padx=5)

        # Info panel
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=10)
        
        info_label = tk.Label(
            info_frame, 
            text="API Server tersedia di: http://localhost:5050\nGunakan untuk integrasi dengan Flutter Mobile App",
            font=("Arial", 10),
            fg="blue",
            justify="center"
        )
        info_label.pack()

        # Status panel
        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(pady=5)
        
        self.status_label = tk.Label(
            self.status_frame, 
            text=f"Known faces loaded: {len(self.face_service.known_face_encodings)}",
            font=("Arial", 9),
            fg="green"
        )
        self.status_label.pack()

    def daftar_wajah(self):
        """Dialog pendaftaran karyawan menggunakan service"""
        dialog = EmployeeRegistrationDialog(self.root)
        if dialog.result:
            nama, departemen, posisi = dialog.result
            
            ret, frame = self.cap.read()
            if ret:
                # Gunakan service untuk register employee
                result = self.face_service.register_employee(nama, departemen, posisi, frame)
                
                if result['status'] == 'success':
                    messagebox.showinfo("Berhasil", result['message'])
                    # Update status
                    self.update_status()
                else:
                    messagebox.showerror("Error", result['message'])
            else:
                messagebox.showerror("Error", "Tidak dapat mengambil gambar dari kamera")

    def lakukan_absensi(self):
        """Lakukan absensi menggunakan service"""
        ret, frame = self.cap.read()
        if ret:
            # Gunakan service untuk absensi
            result = self.face_service.do_absensi(frame)
            
            if result['status'] == 'success':
                data = result['data']
                messagebox.showinfo(
                    "Absensi Berhasil", 
                    f"Absensi untuk {data['nama']} berhasil!\n"
                    f"Departemen: {data['departemen']}\n"
                    f"Posisi: {data['posisi']}\n"
                    f"Waktu: {data['tanggal']} {data['jam']}"
                )
            else:
                messagebox.showerror("Absensi Gagal", result['message'])
        else:
            messagebox.showerror("Error", "Tidak dapat mengambil gambar dari kamera")

    def reload_faces(self):
        """Reload known faces dari database"""
        try:
            success = self.face_service.load_known_faces()
            if success:
                self.update_status()
                messagebox.showinfo("Berhasil", "Known faces berhasil direload")
            else:
                messagebox.showerror("Error", "Gagal reload known faces")
        except Exception as e:
            messagebox.showerror("Error", f"Error saat reload: {str(e)}")

    def update_status(self):
        """Update status label"""
        self.status_label.config(
            text=f"Known faces loaded: {len(self.face_service.known_face_encodings)}"
        )

    def update_video(self):
        """Update video display dengan face detection"""
        ret, frame = self.cap.read()
        if ret:
            # Deteksi wajah dan gambar bounding box
            try:
                import face_recognition
                face_locations = face_recognition.face_locations(frame)
                for (top, right, bottom, left) in face_locations:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            except ImportError:
                # Jika face_recognition tidak tersedia, skip face detection
                pass

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
        departemen_combo['values'] = ('Finance & ICT', 'Human Capital', 'Supply Chain', 'Exploration', 'Exploitation', 'Internal Affairs', 'External Audit', 'Production')
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


def main():
    """Main function untuk menjalankan aplikasi Tkinter"""
    print("🖥️  Starting Tkinter Desktop Application...")
    print("📊 Database and Face Recognition Service will be initialized")
    print("🎯 This app now uses service layer for better separation of concerns")
    
    root = tk.Tk()
    app = AbsensiApp(root)
    
    print("✅ Desktop application is running")
    print("💡 To run API server for Flutter, execute: python api_server.py")
    
    root.mainloop()


if __name__ == "__main__":
    main()
