# 👟 Shoe Store Management System

ระบบร้านขายรองเท้า (Shoe Store) สำหรับการศึกษาด้าน Flask และ SQLite

## 📋 โครงสร้างระบบ

### ฐานข้อมูล (Database Schema)
- **Brands**: เก็บข้อมูลแบรนด์ (brand_id, name, country)
- **Shoes**: เก็บข้อมูลรองเท้า (shoe_id, brand_id FK, model_name, category, base_price)
- **Variants**: เก็บข้อมูล ขนาด สี สต็อก (variant_id, shoe_id FK, size, color, stock)
- **Customers**: เก็บข้อมูลลูกค้า (customer_id, name, phone, email, fav_size)
- **Sales**: เก็บประวัติการขาย (sale_id, customer_id FK, variant_id FK, quantity, total_price, sale_date)

### ฟีเจอร์หลัก
1. ✅ Dashboard - แสดงสถิติและสินค้าใกล้หมด
2. ✅ รายการรองเท้า - ดูรองเท้าทั้งหมด (JOIN ข้อมูล)
3. ✅ เพิ่ม/แก้ไข/ลบ รองเท้า (CRUD)
4. ✅ ประวัติการขาย - ดูประวัติการขายทั้งหมด

## 🚀 วิธีการติดตั้งและรัน

### ขั้นตอนที่ 1: ติดตั้ง Python
ต้องมี Python 3.7+ ติดตั้งบนเครื่องของคุณ

### ขั้นตอนที่ 2: โคลน Repository
```bash
cd c:\Users\Orikame\OneDrive\Desktop\shoes
```

### ขั้นตอนที่ 3: ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### ขั้นตอนที่ 4: เพิ่มข้อมูลตัวอย่าง
```bash
python mock_data.py
```

### ขั้นตอนที่ 5: รัน Flask App
```bash
python app.py
```

### ขั้นตอนที่ 6: เปิด Browser
เปิด browser และเข้าไปที่: `http://localhost:5000`

## 📁 โครงสร้างไฟล์

```
shoes/
├── app.py                          # Flask application หลัก
├── mock_data.py                    # ข้อมูลตัวอย่าง
├── requirements.txt                # Dependencies
├── Procfile                        # สำหรับ PythonAnywhere
├── shoes.db                        # SQLite database (สร้างอัตโนมัติ)
└── templates/
    ├── base.html                   # Base template
    ├── index.html                  # Dashboard
    ├── shoes.html                  # รายการรองเท้า
    ├── add_shoe.html               # ฟอร์มเพิ่มรองเท้า
    ├── edit_shoe.html              # ฟอร์มแก้ไขรองเท้า
    ├── sales.html                  # ประวัติการขาย
    └── error.html                  # หน้า Error
```

## 📖 คำอธิบายโค้ด

### app.py
- `init_db()`: สร้างตารางทั้งหมดอัตโนมัติ
- `get_db()`: เชื่อมต่อ SQLite database
- Routes:
  - `/`: Dashboard
  - `/shoes`: แสดงรองเท้าทั้งหมด
  - `/add-shoe`: เพิ่มรองเท้าใหม่
  - `/edit-shoe/<id>`: แก้ไขรองเท้า
  - `/delete-shoe/<id>`: ลบรองเท้า
  - `/sales`: ประวัติการขาย
  - `/api/shoe/<id>`: API ดึงข้อมูล variants

### mock_data.py
- เพิ่มข้อมูลตัวอย่าง 10+ records ต่อตาราง
- ใช้ `random` module สำหรับสต็อกและข้อมูล

## 🔒 Error Handling
- ✅ ตรวจสอบว่างข้อมูล
- ✅ ตรวจสอบประเภทข้อมูล (เช่น ราคา = ตัวเลข)
- ✅ ไม่ลบรองเท้าที่มีประวัติการขาย
- ✅ Flash messages แจ้งให้ผู้ใช้ทราบ
- ✅ 404 และ 500 error handlers

## 🌐 การ Deploy บน PythonAnywhere

### ขั้นตอน:
1. สร้างบัญชี PythonAnywhere (pythonanywhere.com)
2. Upload ไฟล์ทั้งหมดขึ้น
3. สร้าง Web app ใหม่ (Flask 2.0, Python 3.X)
4. ตั้ง Working directory เป็นที่ที่เก็บไฟล์
5. Update WSGI file ให้ชี้ไปที่ `app.py`
6. Reload Web app
7. เข้า https://yourusername.pythonanywhere.com

## 📝 Technical Details
- **Framework**: Flask 2.0.3
- **Database**: SQLite3 (Built-in with Python)
- **Frontend**: Bootstrap 5 CDN
- **Python Version**: 3.7+
- **ไม่ใช้ ORM**: ใช้ raw SQL queries ตรงๆ เพื่อให้ผู้เรียนเข้าใจ

## 🎓 การเรียนรู้
โค้ดนี้ออกแบบมาเพื่อการศึกษา:
- เข้าใจ SQL queries
- Foreign Key relationships
- Flask routing
- HTML forms
- Error handling
- ข้อมูลตัวอย่างสำหรับทดสอบ

## 💡 ข้อเสนอแนะการพัฒนาต่อไป
- เพิ่ม Authentication (Login/Register)
- เพิ่ม Search functionality
- เพิ่ม Pagination สำหรับตาราง
- เพิ่ม Filters และ Sorting
- เพิ่ม Reports (PDF export)
- เพิ่ม API endpoints เพิ่มเติม

## ⚠️ หมายเหตุ
- ฐานข้อมูล `shoes.db` จะสร้างอัตโนมัติเมื่อรัน `app.py` ครั้งแรก
- ข้อมูลตัวอย่างสามารถเพิ่มได้โดยรัน `python mock_data.py`
- ทั้งหมดเป็นข้อมูลตัวอย่างสำหรับการศึกษา

---
**Made for Education** - 2026
