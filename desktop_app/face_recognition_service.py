"""
Face Recognition Service
Core functions untuk face recognition tanpa kode UI/Tkinter
"""
import cv2
import os
import face_recognition
import datetime
import json
import numpy as np
from typing import Optional, List, Dict, Tuple
from desktop_database_config import DesktopDatabaseConfig


class FaceRecognitionService:
    def __init__(self):
        """Initialize face recognition service"""
        # Inisialisasi direktori
        self.data_dir = "data_wajah"
        self.log_dir = "log_absensi"
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Inisialisasi database
        self.conn, self.db_type = DesktopDatabaseConfig.get_connection()
        DesktopDatabaseConfig.init_tables(self.conn, self.db_type)
        
        # Face recognition data
        self.known_face_encodings = []
        self.known_face_data = []
        self.load_known_faces()
    
    def register_employee(self, name: str, departemen: str, posisi: str, image_data) -> Dict:
        """
        Register employee dengan wajah baru
        
        Args:
            name: Nama karyawan
            departemen: Departemen karyawan
            posisi: Posisi karyawan
            image_data: Data gambar (numpy array atau path file)
            
        Returns:
            Dict dengan status dan message
        """
        try:
            # Convert image data ke numpy array jika diperlukan
            if isinstance(image_data, str):
                # Jika path file
                frame = cv2.imread(image_data)
            elif isinstance(image_data, np.ndarray):
                # Jika numpy array
                frame = image_data
            else:
                return {"status": "error", "message": "Invalid image format"}
            
            if frame is None:
                return {"status": "error", "message": "Cannot read image"}
            
            # Deteksi wajah
            face_locations = face_recognition.face_locations(frame)
            if not face_locations:
                return {"status": "error", "message": "No face detected in image"}
            
            # Ambil wajah pertama yang terdeteksi
            top, right, bottom, left = face_locations[0]
            
            # Perluasan bounding box
            margin = 20
            height, width = frame.shape[:2]
            top = max(0, top - margin)
            right = min(width, right + margin)
            bottom = min(height, bottom + margin)
            left = max(0, left - margin)
            
            face_image = frame[top:bottom, left:right]
            
            # Simpan gambar wajah
            image_path = os.path.join(self.data_dir, f"{name}.jpg")
            cv2.imwrite(image_path, face_image)
            
            # Dapatkan face encoding
            face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
            
            # Simpan face encoding sebagai file
            encoding_path = os.path.join(self.data_dir, f"{name}_encoding.json")
            with open(encoding_path, 'w') as f:
                json.dump(face_encoding.tolist(), f)
            
            # Simpan ke database
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO karyawan (nama, departemen, posisi, face_encoding_path)
                VALUES (%s, %s, %s, %s)
            ''', (name, departemen, posisi, encoding_path))
            
            self.conn.commit()
            
            # Reload known faces
            self.load_known_faces()
            
            return {
                "status": "success", 
                "message": f"Employee {name} registered successfully",
                "data": {
                    "name": name,
                    "departemen": departemen,
                    "posisi": posisi,
                    "image_path": image_path
                }
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Registration failed: {str(e)}"}
    
    def do_absensi(self, image_data) -> Dict:
        """
        Lakukan absensi berdasarkan gambar wajah
        
        Args:
            image_data: Data gambar (numpy array atau path file)
            
        Returns:
            Dict dengan hasil absensi
        """
        try:
            # Convert image data ke numpy array jika diperlukan
            if isinstance(image_data, str):
                frame = cv2.imread(image_data)
            elif isinstance(image_data, np.ndarray):
                frame = image_data
            else:
                return {"status": "error", "message": "Invalid image format"}
            
            if frame is None:
                return {"status": "error", "message": "Cannot read image"}
            
            # Deteksi wajah
            face_locations = face_recognition.face_locations(frame)
            if not face_locations:
                return {"status": "error", "message": "No face detected in image"}
            
            face_encodings = face_recognition.face_encodings(frame, face_locations)
            
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Compare dengan wajah yang dikenal
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.45)
                employee_data = None
                
                if True in matches:
                    first_match_index = matches.index(True)
                    employee_data = self.known_face_data[first_match_index]
                
                if employee_data:
                    # Generate timestamp
                    now = datetime.datetime.now()
                    tanggal = now.strftime("%Y-%m-%d")
                    jam = now.strftime("%H:%M:%S")
                    
                    # Simpan gambar absensi
                    margin = 20
                    height, width = frame.shape[:2]
                    top = max(0, top - margin)
                    right = min(width, right + margin)
                    bottom = min(height, bottom + margin)
                    left = max(0, left - margin)
                    
                    face_image = frame[top:bottom, left:right]
                    
                    filename = f"{employee_data['nama']}_{tanggal}_{now.strftime('%H-%M-%S')}.jpg"
                    local_path = os.path.join(self.log_dir, filename)
                    cv2.imwrite(local_path, face_image)
                    rel_path = f"images/{filename}"
                    
                    # Simpan ke database
                    cursor = self.conn.cursor()
                    cursor.execute('''
                        INSERT INTO log_absensi (nama, departemen, posisi, tanggal, jam, path_gambar)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (
                        employee_data['nama'], 
                        employee_data['departemen'], 
                        employee_data['posisi'], 
                        tanggal, 
                        jam, 
                        rel_path
                    ))
                    
                    self.conn.commit()
                    
                    return {
                        "status": "success",
                        "message": f"Attendance recorded for {employee_data['nama']}",
                        "data": {
                            "nama": employee_data['nama'],
                            "departemen": employee_data['departemen'],
                            "posisi": employee_data['posisi'],
                            "tanggal": tanggal,
                            "jam": jam,
                            "image_path": local_path
                        }
                    }
            
            return {"status": "error", "message": "Face not recognized"}
            
        except Exception as e:
            return {"status": "error", "message": f"Attendance failed: {str(e)}"}
    
    def load_known_faces(self) -> bool:
        """
        Load data wajah dan encoding dari database
        
        Returns:
            bool: True jika berhasil load
        """
        try:
            self.known_face_encodings = []
            self.known_face_data = []
            
            cursor = self.conn.cursor()
            cursor.execute("SELECT nama, departemen, posisi, face_encoding_path FROM karyawan")
            employees = cursor.fetchall()
            
            for employee in employees:
                try:
                    if len(employee) == 4:
                        nama, departemen, posisi, encoding_path = employee
                    else:
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
            
            print(f"Loaded {len(self.known_face_encodings)} known faces")
            return True
            
        except Exception as e:
            print(f"Error loading known faces: {e}")
            return False
    
    def get_all_employees(self) -> List[Dict]:
        """
        Get semua data karyawan
        
        Returns:
            List karyawan
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, nama, departemen, posisi FROM karyawan ORDER BY nama")
            employees = cursor.fetchall()
            
            result = []
            for emp in employees:
                if self.db_type == 'postgresql':
                    result.append({
                        "id": emp[0],
                        "nama": emp[1],
                        "departemen": emp[2],
                        "posisi": emp[3]
                    })
                else:
                    result.append({
                        "id": emp[0],
                        "nama": emp[1],
                        "departemen": emp[2],
                        "posisi": emp[3]
                    })
            
            return result
            
        except Exception as e:
            print(f"Error getting employees: {e}")
            return []
    
    def get_attendance_logs(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        Get log absensi
        
        Args:
            start_date: Tanggal mulai (YYYY-MM-DD)
            end_date: Tanggal akhir (YYYY-MM-DD)
            
        Returns:
            List log absensi
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, nama, departemen, posisi FROM karyawan ORDER BY nama")
            employees = cursor.fetchall()
            
            result = []
            for emp in employees:
                if self.db_type == 'postgresql':
                    result.append({
                        "id": emp[0],
                        "nama": emp[1],
                        "departemen": emp[2],
                        "posisi": emp[3]
                    })
                else:
                    result.append({
                        "id": emp[0],
                        "nama": emp[1],
                        "departemen": emp[2],
                        "posisi": emp[3]
                    })
            
            return result
            
        except Exception as e:
            print(f"Error getting employees: {e}")
            return []
    
    def get_attendance_logs(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        Get log absensi
        
        Args:
            start_date: Tanggal mulai (YYYY-MM-DD)
            end_date: Tanggal akhir (YYYY-MM-DD)
            
        Returns:
            List log absensi
        """
        try:
            cursor = self.conn.cursor()
            
            if start_date and end_date:
                cursor.execute('''
                    SELECT nama, departemen, posisi, tanggal, jam, path_gambar 
                    FROM log_absensi 
                    WHERE tanggal BETWEEN %s AND %s 
                    ORDER BY tanggal DESC, jam DESC
                ''', (start_date, end_date))
            else:
                cursor.execute('''
                    SELECT nama, departemen, posisi, tanggal, jam, path_gambar 
                    FROM log_absensi 
                    ORDER BY tanggal DESC, jam DESC
                ''')
            
            logs = cursor.fetchall()
            
            result = []
            for log in logs:
                result.append({
                    "nama": log[0],
                    "departemen": log[1],
                    "posisi": log[2],
                    "tanggal": log[3],
                    "jam": log[4],
                    "path_gambar": log[5]
                })
            
            return result
            
        except Exception as e:
            print(f"Error getting attendance logs: {e}")
            return []
    
    def __del__(self):
        """Cleanup saat object dihapus"""
        if hasattr(self, 'conn'):
            self.conn.close()


# Utility functions untuk kompatibilitas dengan kode lama
def register_employee(name: str, departemen: str, posisi: str, image_data) -> Dict:
    """Wrapper function untuk register employee"""
    service = FaceRecognitionService()
    return service.register_employee(name, departemen, posisi, image_data)


def do_absensi(image_data) -> Dict:
    """Wrapper function untuk absensi"""
    service = FaceRecognitionService()
    return service.do_absensi(image_data)


def load_known_faces() -> bool:
    """Wrapper function untuk load known faces"""
    service = FaceRecognitionService()
    return service.load_known_faces()
