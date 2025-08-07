-- Initialize database schema for absensi system

-- Create karyawan table
CREATE TABLE IF NOT EXISTS karyawan (
    id SERIAL PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    departemen VARCHAR(100) NOT NULL,
    posisi VARCHAR(100) NOT NULL,
    face_encoding_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create log_absensi table
CREATE TABLE IF NOT EXISTS log_absensi (
    id SERIAL PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    departemen VARCHAR(100),
    posisi VARCHAR(100),
    tanggal DATE NOT NULL,
    jam TIME NOT NULL,
    path_gambar TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_log_absensi_tanggal ON log_absensi(tanggal);
CREATE INDEX IF NOT EXISTS idx_log_absensi_nama ON log_absensi(nama);
CREATE INDEX IF NOT EXISTS idx_log_absensi_departemen ON log_absensi(departemen);
CREATE INDEX IF NOT EXISTS idx_karyawan_nama ON karyawan(nama);

-- Insert sample data for testing (optional)
-- INSERT INTO karyawan (nama, departemen, posisi) VALUES 
-- ('John Doe', 'IT', 'Manager'),
-- ('Jane Smith', 'HR', 'Senior Staff'),
-- ('Bob Johnson', 'Finance', 'Staff');

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
