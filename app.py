"""
ระบบร้านขายรองเท้า - Shoe Store Management System
Flask Application with SQLite3
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'shoe-store-secret-key-2026'

# กำหนด path ของไฟล์ database
DATABASE = 'shoes.db'

# ฟังก์ชันเชื่อมต่อ database
def get_db():
    """เชื่อมต่อกับ SQLite database"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ฟังก์ชันสร้างตารางอัตโนมัติ
def init_db():
    """สร้างตาราง database ทั้งหมด"""
    conn = get_db()
    cursor = conn.cursor()
    
    # ตาราง Brands - เก็บข้อมูลแบรนด์รองเท้า
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS brands (
            brand_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            country TEXT NOT NULL
        )
    ''')
    
    # ตาราง Shoes - เก็บข้อมูลรองเท้า
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shoes (
            shoe_id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_id INTEGER NOT NULL,
            model_name TEXT NOT NULL,
            category TEXT NOT NULL,
            base_price REAL NOT NULL,
            image_url TEXT,
            FOREIGN KEY (brand_id) REFERENCES brands(brand_id) ON DELETE CASCADE
        )
    ''')
    
    # ปรับ schema หากตารางเก่าไม่มีคอลัมน์รูปภาพ
    cursor.execute("PRAGMA table_info(shoes)")
    shoe_columns = [row[1] for row in cursor.fetchall()]
    if 'image_url' not in shoe_columns:
        cursor.execute('ALTER TABLE shoes ADD COLUMN image_url TEXT')
    
    # ตาราง Variants - เก็บข้อมูลขนาด สีและสต็อก
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS variants (
            variant_id INTEGER PRIMARY KEY AUTOINCREMENT,
            shoe_id INTEGER NOT NULL,
            size TEXT NOT NULL,
            color TEXT NOT NULL,
            stock INTEGER NOT NULL,
            FOREIGN KEY (shoe_id) REFERENCES shoes(shoe_id) ON DELETE CASCADE
        )
    ''')
    
    # ตาราง Customers - เก็บข้อมูลลูกค้า
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT UNIQUE,
            fav_size TEXT
        )
    ''')
    
    # ตาราง Sales - เก็บข้อมูลการขาย
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            variant_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
            FOREIGN KEY (variant_id) REFERENCES variants(variant_id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

# เรียกฟังก์ชันสร้างตาราง เมื่อเริ่มแอป
init_db()

# ======================== DASHBOARD ROUTE ========================

@app.route('/')
def dashboard():
    """หน้า Dashboard แสดงยอดขายรวมและสินค้าใกล้หมด"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # นับรวมรายได้จากการขายทั้งหมด
        cursor.execute('SELECT SUM(total_price) as total_revenue FROM sales')
        revenue = cursor.fetchone()['total_revenue'] or 0
        
        # นับจำนวนการขายทั้งหมด
        cursor.execute('SELECT COUNT(*) as total_sales FROM sales')
        total_sales_count = cursor.fetchone()['total_sales']
        
        # นับจำนวนรองเท้าทั้งหมด
        cursor.execute('SELECT COUNT(*) as total_shoes FROM shoes')
        total_shoes = cursor.fetchone()['total_shoes']
        
        # ค้นหาสินค้าที่เหลือน้อย (stock < 5)
        cursor.execute('''
            SELECT v.variant_id, s.model_name, b.name as brand_name, 
                   v.size, v.color, v.stock
            FROM variants v
            JOIN shoes s ON v.shoe_id = s.shoe_id
            JOIN brands b ON s.brand_id = b.brand_id
            WHERE v.stock < 5
            ORDER BY v.stock ASC
        ''')
        low_stock = cursor.fetchall()
        
        conn.close()
        
        return render_template('index.html', 
                             total_revenue=f"{revenue:.2f}",
                             total_sales_count=total_sales_count,
                             total_shoes=total_shoes,
                             low_stock=low_stock)
    except Exception as e:
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'danger')
        return render_template('index.html',
                            total_revenue=0,
                            total_sales_count=0,
                            total_shoes=0,
                            low_stock=[])

# ======================== SHOES LIST & DISPLAY ========================

@app.route('/shoes')
def shoes():
    """หน้าแสดงรายการรองเท้าทั้งหมด โดย JOIN ข้อมูลแบรนด์และ Variants"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # ดึงข้อมูลรองเท้า JOIN กับแบรนด์และ variants
        cursor.execute('''
            SELECT s.shoe_id, s.model_name, s.category, s.base_price,
                   b.name as brand_name, COUNT(v.variant_id) as total_variants,
                   SUM(v.stock) as total_stock
            FROM shoes s
            JOIN brands b ON s.brand_id = b.brand_id
            LEFT JOIN variants v ON s.shoe_id = v.shoe_id
            GROUP BY s.shoe_id
            ORDER BY s.shoe_id DESC
        ''')
        shoes_list = cursor.fetchall()
        
        conn.close()
        return render_template('shoes.html', shoes=shoes_list)
    except Exception as e:
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

# ======================== ADD SHOE ========================

@app.route('/add-shoe', methods=['GET', 'POST'])
def add_shoe():
    """หน้าเพิ่มรองเท้าใหม่"""
    try:
        if request.method == 'POST':
            brand_id = request.form.get('brand_id')
            model_name = request.form.get('model_name')
            category = request.form.get('category')
            base_price = request.form.get('base_price')
            
            # ตรวจสอบข้อมูลที่จำเป็น
            if not all([brand_id, model_name, category, base_price]):
                flash('กรุณากรอกข้อมูลทั้งหมด', 'warning')
                return redirect(url_for('add_shoe'))
            
            try:
                base_price = float(base_price)
                if base_price < 0:
                    flash('ราคาต้องเป็นจำนวนบวก', 'warning')
                    return redirect(url_for('add_shoe'))
            except ValueError:
                flash('ราคาต้องเป็นตัวเลข', 'warning')
                return redirect(url_for('add_shoe'))

            image_url = request.form.get('image_url', '').strip()
            
            conn = get_db()
            cursor = conn.cursor()
            
            # บันทึกรองเท้าใหม่
            cursor.execute('''
                INSERT INTO shoes (brand_id, model_name, category, base_price, image_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (brand_id, model_name, category, base_price, image_url))
            
            conn.commit()
            conn.close()
            
            flash('เพิ่มรองเท้าสำเร็จ!', 'success')
            return redirect(url_for('shoes'))
        
        # GET request - ดึงข้อมูลแบรนด์ทั้งหมด
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM brands ORDER BY name')
        brands = cursor.fetchall()
        conn.close()
        
        return render_template('add_shoe.html', brands=brands)
    except Exception as e:
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'danger')
        return redirect(url_for('shoes'))

# ======================== EDIT SHOE ========================

@app.route('/edit-shoe/<int:shoe_id>', methods=['GET', 'POST'])
def edit_shoe(shoe_id):
    """หน้าแก้ไขข้อมูลรองเท้า"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        if request.method == 'POST':
            brand_id = request.form.get('brand_id')
            model_name = request.form.get('model_name')
            category = request.form.get('category')
            base_price = request.form.get('base_price')
            
            # ตรวจสอบข้อมูลที่จำเป็น
            if not all([brand_id, model_name, category, base_price]):
                flash('กรุณากรอกข้อมูลทั้งหมด', 'warning')
                return redirect(url_for('edit_shoe', shoe_id=shoe_id))
            
            try:
                base_price = float(base_price)
                if base_price < 0:
                    flash('ราคาต้องเป็นจำนวนบวก', 'warning')
                    return redirect(url_for('edit_shoe', shoe_id=shoe_id))
            except ValueError:
                flash('ราคาต้องเป็นตัวเลข', 'warning')
                return redirect(url_for('edit_shoe', shoe_id=shoe_id))

            image_url = request.form.get('image_url', '').strip()
            
            # อัปเดตข้อมูลรองเท้า
            cursor.execute('''
                UPDATE shoes 
                SET brand_id = ?, model_name = ?, category = ?, base_price = ?, image_url = ?
                WHERE shoe_id = ?
            ''', (brand_id, model_name, category, base_price, image_url, shoe_id))
            
            conn.commit()
            conn.close()
            
            flash('อัปเดตข้อมูลรองเท้าสำเร็จ!', 'success')
            return redirect(url_for('shoes'))
        
        # GET request - ดึงข้อมูลรองเท้าที่ต้องแก้ไข
        cursor.execute('SELECT * FROM shoes WHERE shoe_id = ?', (shoe_id,))
        shoe = cursor.fetchone()
        
        if not shoe:
            flash('ไม่พบรองเท้านี้', 'danger')
            conn.close()
            return redirect(url_for('shoes'))
        
        # ดึงข้อมูลแบรนด์ทั้งหมด
        cursor.execute('SELECT * FROM brands ORDER BY name')
        brands = cursor.fetchall()
        
        conn.close()
        return render_template('edit_shoe.html', shoe=shoe, brands=brands)
    except Exception as e:
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'danger')
        return redirect(url_for('shoes'))

# ======================== DELETE SHOE ========================

@app.route('/delete-shoe/<int:shoe_id>', methods=['POST'])
def delete_shoe(shoe_id):
    """ลบข้อมูลรองเท้า"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # ตรวจสอบว่าหรือมีการขายสินค้านี้หรือไม่
        cursor.execute('''
            SELECT COUNT(*) as count FROM sales 
            WHERE variant_id IN (SELECT variant_id FROM variants WHERE shoe_id = ?)
        ''', (shoe_id,))
        
        if cursor.fetchone()['count'] > 0:
            flash('ไม่สามารถลบได้ - มีประวัติการขายของสินค้านี้', 'warning')
        else:
            # ลบรองเท้าและ variants ที่เกี่ยวข้อง
            cursor.execute('DELETE FROM shoes WHERE shoe_id = ?', (shoe_id,))
            conn.commit()
            flash('ลบรองเท้าสำเร็จ!', 'success')
        
        conn.close()
        return redirect(url_for('shoes'))
    except Exception as e:
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'danger')
        return redirect(url_for('shoes'))

# ======================== SALES HISTORY ========================

@app.route('/sales')
def sales():
    """หน้าแสดงประวัติการขายทั้งหมด"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # ดึงข้อมูลการขาย JOIN กับข้อมูลลูกค้า รองเท้า และสต็อก
        cursor.execute('''
            SELECT s.sale_id, c.name as customer_name, 
                   sh.model_name, b.name as brand_name,
                   v.size, v.color, s.quantity, s.total_price, 
                   s.sale_date
            FROM sales s
            JOIN customers c ON s.customer_id = c.customer_id
            JOIN variants v ON s.variant_id = v.variant_id
            JOIN shoes sh ON v.shoe_id = sh.shoe_id
            JOIN brands b ON sh.brand_id = b.brand_id
            ORDER BY s.sale_date DESC
        ''')
        sales_list = cursor.fetchall()
        
        conn.close()
        return render_template('sales.html', sales=sales_list)
    except Exception as e:
        flash(f'เกิดข้อผิดพลาด: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

# ======================== API ENDPOINTS FOR VARIANTS ========================

@app.route('/api/shoe/<int:shoe_id>')
def get_shoe_variants(shoe_id):
    """API เพื่อดึงข้อมูล variants ของรองเท้า (สำหรับใช้ใน JavaScript)"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT variant_id, size, color, stock
            FROM variants
            WHERE shoe_id = ?
            ORDER BY size, color
        ''', (shoe_id,))
        variants = cursor.fetchall()
        conn.close()
        
        return {
            'success': True,
            'variants': [dict(v) for v in variants]
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# ======================== ERROR HANDLERS ========================

@app.errorhandler(404)
def page_not_found(error):
    """จัดการหน้าไม่พบ"""
    return render_template('error.html', 
                         error_code=404,
                         error_message='ไม่พบหน้านี้'), 404

@app.errorhandler(500)
def internal_error(error):
    """จัดการข้อผิดพลาดภายในเซิร์ฟเวอร์"""
    return render_template('error.html',
                         error_code=500,
                         error_message='เกิดข้อผิดพลาดในเซิร์ฟเวอร์'), 500

# ======================== MAIN ========================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
