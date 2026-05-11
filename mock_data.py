"""
ข้อมูลตัวอย่างสำหรับการทดสอบระบบร้านขายรองเท้า
Mock Data Generator
"""

import sqlite3
from datetime import datetime, timedelta

DATABASE = 'shoes.db'

# Import init_db from app.py
import sys
import os
sys.path.append(os.path.dirname(__file__))
from app import init_db

def insert_mock_data():
    """เพิ่มข้อมูลตัวอย่างลงในฐานข้อมูล"""
    # สร้างตารางก่อน
    init_db()
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # ข้อมูลแบรนด์ (Brands) - 10 แบรนด์
    brands_data = [
        ('Nike', 'USA'),
        ('Adidas', 'Germany'),
        ('Puma', 'Germany'),
        ('New Balance', 'USA'),
        ('Converse', 'USA'),
        ('Vans', 'USA'),
        ('Asics', 'Japan'),
        ('Reebok', 'USA'),
        ('Skechers', 'USA'),
        ('Timberland', 'USA'),
    ]
    
    # บันทึกข้อมูลแบรนด์
    for brand_name, country in brands_data:
        try:
            cursor.execute('INSERT INTO brands (name, country) VALUES (?, ?)',
                         (brand_name, country))
        except sqlite3.IntegrityError:
            pass  # ถ้าแบรนด์มีอยู่แล้วให้ข้ามไป
    
    conn.commit()
    
    # ดึงข้อมูล brand_id สำหรับใช้ในการเพิ่มรองเท้า
    cursor.execute('SELECT brand_id, name FROM brands')
    brands = {row[1]: row[0] for row in cursor.fetchall()}
    
    # ข้อมูลรองเท้า (Shoes) - 15 รองเท้า
    shoes_data = [
        (brands['Nike'], 'Air Force 1', 'Casual', 3000),
        (brands['Nike'], 'Air Max 90', 'Sports', 4500),
        (brands['Nike'], 'Blazer Mid', 'Basketball', 3500),
        (brands['Adidas'], 'Stan Smith', 'Casual', 2800),
        (brands['Adidas'], 'Ultraboost 22', 'Running', 5000),
        (brands['Adidas'], 'NMD R1', 'Casual', 3800),
        (brands['Puma'], 'RS-X', 'Casual', 2500),
        (brands['New Balance'], '574', 'Running', 2900),
        (brands['New Balance'], '990v6', 'Running', 4200),
        (brands['Converse'], 'Chuck Taylor All Star', 'Casual', 1900),
        (brands['Vans'], 'Old Skool', 'Casual', 2200),
        (brands['Asics'], 'Gel-Lyte III', 'Running', 3600),
        (brands['Reebok'], 'Zig Kinetica', 'Running', 3400),
        (brands['Skechers'], 'Go Walk 5', 'Walking', 2100),
        (brands['Timberland'], '6-Inch Premium Boot', 'Boots', 5500),
    ]
    
    # บันทึกข้อมูลรองเท้า
    for brand_id, model_name, category, base_price in shoes_data:
        cursor.execute('''
            INSERT INTO shoes (brand_id, model_name, category, base_price)
            VALUES (?, ?, ?, ?)
        ''', (brand_id, model_name, category, base_price))
    
    conn.commit()
    
    # ดึงข้อมูล shoe_id สำหรับใช้ในการเพิ่ม variants
    cursor.execute('SELECT shoe_id FROM shoes ORDER BY shoe_id')
    shoe_ids = [row[0] for row in cursor.fetchall()]
    
    # ข้อมูล Variants (ขนาด สีและสต็อก)
    sizes = ['35', '36', '37', '38', '39', '40', '41', '42', '43', '44']
    colors = ['Black', 'White', 'Red', 'Blue', 'Gray', 'Navy', 'Green']
    
    variant_count = 0
    for shoe_id in shoe_ids:
        # สร้าง 10-15 variants ต่อรองเท้า
        import random
        num_variants = random.randint(10, 15)
        selected_sizes = random.sample(sizes, min(5, len(sizes)))
        selected_colors = random.sample(colors, min(3, len(colors)))
        
        for _ in range(num_variants):
            size = random.choice(selected_sizes)
            color = random.choice(selected_colors)
            stock = random.randint(0, 30)  # สต็อกอาจจะ 0-30
            
            cursor.execute('''
                INSERT INTO variants (shoe_id, size, color, stock)
                VALUES (?, ?, ?, ?)
            ''', (shoe_id, size, color, stock))
            variant_count += 1
    
    conn.commit()
    
    # ข้อมูลลูกค้า (Customers) - 15 ลูกค้า
    customers_data = [
        ('สมชาย สิริศักดิ์', '0812345678', 'somchai@email.com', '42'),
        ('สมหญิง สวรรค์', '0823456789', 'somying@email.com', '38'),
        ('กมล ปรีชา', '0834567890', 'kamol@email.com', '44'),
        ('ชนก มาสา', '0845678901', 'chanok@email.com', '36'),
        ('ปิยะ วิบูลย์', '0856789012', 'piya@email.com', '40'),
        ('ดารา จันทร์', '0867890123', 'dara@email.com', '37'),
        ('นรา ศรีสุข', '0878901234', 'nara@email.com', '39'),
        ('อมตา วรรณา', '0889012345', 'amata@email.com', '35'),
        ('กิจ สิทธิ์', '0890123456', 'kit@email.com', '43'),
        ('สิริ สุขศรี', '0801234567', 'siri@email.com', '41'),
        ('วิไล ถิรปัญญา', '0812345670', 'wilai@email.com', '37'),
        ('ประกาย วงศ์', '0823456780', 'prakay@email.com', '39'),
        ('นพ สวัสดิ์', '0834567891', 'nop@email.com', '42'),
        ('ชมพู มณี', '0845678902', 'chompu@email.com', '36'),
        ('ศรัญ ยศ', '0856789013', 'saran@email.com', '40'),
    ]
    
    # บันทึกข้อมูลลูกค้า
    for name, phone, email, fav_size in customers_data:
        try:
            cursor.execute('''
                INSERT INTO customers (name, phone, email, fav_size)
                VALUES (?, ?, ?, ?)
            ''', (name, phone, email, fav_size))
        except sqlite3.IntegrityError:
            pass  # ถ้ามี email ซ้ำให้ข้ามไป
    
    conn.commit()
    
    # ดึงข้อมูล customer_id และ variant_id สำหรับสร้างการขาย
    cursor.execute('SELECT customer_id FROM customers')
    customer_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT variant_id, stock FROM variants WHERE stock > 0')
    available_variants = cursor.fetchall()
    
    # ข้อมูลการขาย (Sales) - อย่างน้อย 20 รายการ
    if available_variants and customer_ids:
        import random
        for i in range(20):
            customer_id = random.choice(customer_ids)
            variant_id, stock = random.choice(available_variants)
            quantity = random.randint(1, min(3, stock))
            
            # ดึงราคาฐานจากรองเท้า
            cursor.execute('''
                SELECT base_price FROM shoes 
                WHERE shoe_id = (SELECT shoe_id FROM variants WHERE variant_id = ?)
            ''', (variant_id,))
            base_price = cursor.fetchone()[0]
            
            total_price = base_price * quantity
            
            # สร้างวันที่ขายในช่วง 30 วันที่แล้ว
            days_ago = random.randint(1, 30)
            sale_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
            
            cursor.execute('''
                INSERT INTO sales (customer_id, variant_id, quantity, total_price, sale_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (customer_id, variant_id, quantity, total_price, sale_date))
    
    conn.commit()
    conn.close()
    
    print("✓ เพิ่มข้อมูลตัวอย่างสำเร็จ!")
    print(f"  - แบรนด์: {len(brands_data)} แบรนด์")
    print(f"  - รองเท้า: {len(shoes_data)} รองเท้า")
    print(f"  - Variants: {variant_count} variants")
    print(f"  - ลูกค้า: {len(customers_data)} ลูกค้า")
    print(f"  - การขาย: 20 รายการ")

if __name__ == '__main__':
    insert_mock_data()
