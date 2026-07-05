# SIAKAD - STMIK Amikom Surakarta
**Proyek Kelompok 6**

Aplikasi Sistem Informasi Akademik berbasis **Streamlit + SQLAlchemy (SQLite)**.

## Menjalankan
```bash
python -m pip install -r requirements.txt
python seed.py          # (opsional) memuat data dummy
streamlit run app.py
```

Aplikasi juga otomatis menjalankan seeder saat pertama kali dibuka.

## Akun Demo
| Peran      | Username     | Password  |
|------------|--------------|-----------|
| Admin      | admin        | admin123  |
| Dosen      | dosen1..3    | dosen123  |
| Mahasiswa  | mahasiswa1..5| mhs123    |

## Struktur
```
siakad/
├── app.py                 # Login + router utama
├── database.py            # Model SQLAlchemy + koneksi SQLite
├── seed.py                # Seeder data dummy
├── requirements.txt
└── pages/
    ├── _shared.py
    ├── 1_Admin_Dashboard.py
    ├── 2_Manage_Students.py
    ├── 3_Manage_Lecturers.py
    ├── 4_Manage_Courses.py
    ├── 5_Dosen_Dashboard.py
    ├── 6_Dosen_Attendance.py
    ├── 7_Dosen_Grades.py
    ├── 8_Mahasiswa_Dashboard.py
    ├── 9_Mahasiswa_KRS.py
    └── 10_Mahasiswa_KHS.py
```

## Fitur
- **RBAC** (Admin / Dosen / Mahasiswa) berbasis `st.session_state` + bcrypt.
- **Admin**: CRUD Mahasiswa, Dosen, Mata Kuliah.
- **Dosen**: melihat kelas, input presensi, input nilai akhir.
- **Mahasiswa**: jadwal, isi KRS (batas 24 SKS), KHS + IPK otomatis.
- Tema gelap dengan aksen biru `#0046FF`, tabel horizontal-scroll responsif.
- Error handling `try/except` di seluruh operasi DB & form.
