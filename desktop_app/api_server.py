"""
Flask API for Face Recognition - untuk digunakan oleh Flutter Mobile App
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
from PIL import Image, ExifTags
import io
import os
from face_recognition_service import FaceRecognitionService
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'memacak-tanah-menjunjung-tinggi'  
CORS(app)
jwt = JWTManager(app)

# Initialize face recognition service
face_service = FaceRecognitionService()

def decode_base64_image(base64_string):
    """
    Decode base64 string menjadi numpy array image, auto-rotate sesuai EXIF
    """
    try:
        # Remove header jika ada (data:image/jpeg;base64,)
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(base64_string)
        
        # Convert ke PIL Image
        image = Image.open(io.BytesIO(image_data))

        # --- Tambahan: auto-rotate sesuai EXIF ---
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = image._getexif()
            if exif is not None:
                orientation_value = exif.get(orientation, None)
                if orientation_value == 3:
                    image = image.rotate(180, expand=True)
                elif orientation_value == 6:
                    image = image.rotate(270, expand=True)
                elif orientation_value == 8:
                    image = image.rotate(90, expand=True)
        except Exception:
            pass  # Jika tidak ada EXIF, lanjut saja

        # Convert ke numpy array (BGR untuk OpenCV)
        image_array = np.array(image)
        if len(image_array.shape) == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        return image_array
    except Exception as e:
        raise ValueError(f"Failed to decode image: {str(e)}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Face Recognition API is running',
        'version': '1.0.0'
    })

@app.route('/api/login', methods=['POST'])
def login():
    """
    Login user (karyawan)
    Request body:
    {
        "username": "string",
        "password": "string"
    }
    """
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'status': 'error', 'message': 'Username and password required'}), 400

        username = data['username']
        password = data['password']

        # Query user dari database
        cursor = face_service.conn.cursor()
        cursor.execute(
            "SELECT id, nama, departemen, posisi, password_hash FROM karyawan WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 401

        user_id, nama, departemen, posisi, password_hash = user

        # Verifikasi password
        if not check_password_hash(password_hash, password):
            return jsonify({'status': 'error', 'message': 'Invalid password'}), 401

        # Sukses login
        access_token = create_access_token(identity=username)
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'access_token': access_token,
            'data': {
                'id': user_id,
                'nama': nama,
                'departemen': departemen,
                'posisi': posisi,
                'username': username
            }
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Login failed: {str(e)}'}), 500
    

@app.route('/api/register', methods=['POST'])
def register_employee():
    """
    Register karyawan baru
    
    Request body:
    {
        "name": "string",
        "departemen": "string", 
        "posisi": "string",
        "image": "base64_string"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # Validasi required fields
        required_fields = ['name', 'departemen', 'posisi', 'image']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'status': 'error', 
                    'message': f'Field {field} is required'
                }), 400
        
        # Decode image
        try:
            image_array = decode_base64_image(data['image'])
        except ValueError as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400
        
        # Register employee
        result = face_service.register_employee(
            name=data['name'],
            departemen=data['departemen'],
            posisi=data['posisi'],
            image_data=image_array
        )
        
        if result['status'] == 'success':
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Registration failed: {str(e)}'
        }), 500

@app.route('/api/absensi', methods=['POST'])
@jwt_required()
def do_attendance():
    """
    Lakukan absensi berdasarkan foto wajah
    
    Request body:
    {
        "image": "base64_string"
    }
    """
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'status': 'error', 'message': 'Image required'}), 400

        username = get_jwt_identity()
        image = decode_base64_image(data['image'])

        # Panggil service dengan username
        result = face_service.do_absensi(image, username=username)
        if result.get('status') == 'success':
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/employees', methods=['GET'])
@jwt_required()
def get_employees():
    """
    Get daftar semua karyawan
    """
    try:
        employees = face_service.get_all_employees()
        return jsonify({
            'status': 'success',
            'data': employees,
            'count': len(employees)
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get employees: {str(e)}'
        }), 500

@app.route('/api/attendance-logs', methods=['GET'])
@jwt_required()
def get_attendance_logs():
    """
    Get log absensi
    
    Query parameters:
    - start_date: YYYY-MM-DD (optional)
    - end_date: YYYY-MM-DD (optional)
    """
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        logs = face_service.get_attendance_logs(start_date, end_date)
        
        return jsonify({
            'status': 'success',
            'data': logs,
            'count': len(logs)
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get attendance logs: {str(e)}'
        }), 500

@app.route('/api/reload-faces', methods=['POST'])
@jwt_required()
def reload_faces():
    """
    Reload known faces dari database
    """
    try:
        success = face_service.load_known_faces()
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Known faces reloaded successfully',
                'count': len(face_service.known_face_encodings)
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to reload known faces'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to reload faces: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'status': 'error',
        'message': 'Method not allowed'
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Face Recognition API...")
    print("📱 Flutter endpoints available:")
    print("   POST /api/register      - Register new employee")
    print("   POST /api/login       - Record attendance")
    print("   POST /api/absensi       - Record attendance")
    print("   GET  /api/employees     - Get all employees")
    print("   GET  /api/attendance-logs - Get attendance logs")
    print("   POST /api/reload-faces  - Reload known faces")
    print("   GET  /api/health        - Health check")
    print("\n🌐 Access from Flutter: http://YOUR_IP:5050")
    print("🔧 For LAN access, use: app.run(host='0.0.0.0', port=5050)")
    
    # Run server
    # Untuk development
    app.run(debug=True, host='0.0.0.0', port=5050)
    
    # Untuk production, gunakan gunicorn:
    # gunicorn -w 4 -b 0.0.0.0:5050 api_server:app
