import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'petclinic.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # --- DDL ---
    c.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS owners (
        owner_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name  TEXT NOT NULL,
        last_name   TEXT NOT NULL,
        phone       TEXT NOT NULL,
        email       TEXT UNIQUE NOT NULL,
        address     TEXT
    );

    CREATE TABLE IF NOT EXISTS pets (
        pet_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id    INTEGER NOT NULL,
        name        TEXT NOT NULL,
        species     TEXT NOT NULL,
        breed       TEXT,
        birth_date  TEXT,
        FOREIGN KEY (owner_id) REFERENCES owners(owner_id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS vets (
        vet_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name  TEXT NOT NULL,
        last_name   TEXT NOT NULL,
        specialty   TEXT NOT NULL,
        phone       TEXT NOT NULL,
        email       TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS appointments (
        appt_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_id      INTEGER NOT NULL,
        vet_id      INTEGER NOT NULL,
        appt_date   TEXT NOT NULL,
        reason      TEXT NOT NULL,
        status      TEXT NOT NULL DEFAULT 'Scheduled',
        notes       TEXT,
        FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON DELETE CASCADE,
        FOREIGN KEY (vet_id) REFERENCES vets(vet_id)
    );

    CREATE TABLE IF NOT EXISTS treatments (
        treat_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        appt_id     INTEGER NOT NULL,
        description TEXT NOT NULL,
        medication  TEXT,
        cost        REAL NOT NULL DEFAULT 0.0,
        FOREIGN KEY (appt_id) REFERENCES appointments(appt_id) ON DELETE CASCADE
    );
    """)

    # --- Seed Data ---
    owners = [
        ('สมชาย', 'ใจดี', '081-111-0001', 'somchai@email.com', '10 ถ.พหลโยธิน กรุงเทพฯ'),
        ('วิภา', 'รักสัตว์', '081-111-0002', 'wipa@email.com', '25 ถ.สุขุมวิท กรุงเทพฯ'),
        ('นภา', 'ศรีสวัสดิ์', '081-111-0003', 'napa@email.com', '7 ถ.เพชรบุรี กรุงเทพฯ'),
        ('ธนา', 'มั่นคง', '081-111-0004', 'thana@email.com', '33 ถ.รัชดา กรุงเทพฯ'),
        ('จิรา', 'พงษ์ดี', '081-111-0005', 'jira@email.com', '15 ถ.ลาดพร้าว กรุงเทพฯ'),
        ('อารีย์', 'สุขใส', '081-111-0006', 'aree@email.com', '88 ถ.งามวงศ์วาน นนทบุรี'),
        ('ปิยะ', 'ทองดี', '081-111-0007', 'piya@email.com', '44 ถ.แจ้งวัฒนะ ปทุมธานี'),
        ('กนกวรรณ', 'เพชรงาม', '081-111-0008', 'kanok@email.com', '12 ถ.ติวานนท์ นนทบุรี'),
        ('สุรชัย', 'ไพบูลย์', '081-111-0009', 'surachai@email.com', '3 ถ.บางนา กรุงเทพฯ'),
        ('มาลี', 'วงศ์สวัสดิ์', '081-111-0010', 'malee@email.com', '99 ถ.รามคำแหง กรุงเทพฯ'),
    ]
    c.executemany("INSERT OR IGNORE INTO owners (first_name,last_name,phone,email,address) VALUES (?,?,?,?,?)", owners)

    pets = [
        (1, 'ขาว', 'Dog', 'Shih Tzu', '2020-03-15'),
        (1, 'ดำ', 'Cat', 'Scottish Fold', '2021-06-01'),
        (2, 'มะม่วง', 'Dog', 'Golden Retriever', '2019-11-20'),
        (3, 'บัตเตอร์', 'Rabbit', 'Holland Lop', '2022-01-10'),
        (4, 'ลูกหมาก', 'Dog', 'Poodle', '2021-08-05'),
        (5, 'ส้ม', 'Cat', 'Persian', '2020-04-22'),
        (6, 'เมฆ', 'Dog', 'Beagle', '2018-07-14'),
        (7, 'น้ำตาล', 'Cat', 'Siamese', '2023-02-28'),
        (8, 'พริก', 'Bird', 'Cockatiel', '2022-09-01'),
        (9, 'วานิลลา', 'Dog', 'Maltese', '2020-12-25'),
        (10, 'ช็อกโกแลต', 'Dog', 'Labrador', '2017-05-18'),
        (2, 'ครีม', 'Rabbit', 'Angora', '2023-04-10'),
    ]
    c.executemany("INSERT OR IGNORE INTO pets (owner_id,name,species,breed,birth_date) VALUES (?,?,?,?,?)", pets)

    vets = [
        ('อรุณ', 'แสงธรรม', 'General Practice', '02-555-0001', 'arun@petclinic.com'),
        ('สุภา', 'นามสกุล', 'Surgery', '02-555-0002', 'supa@petclinic.com'),
        ('ชาญ', 'วิทยา', 'Dermatology', '02-555-0003', 'chan@petclinic.com'),
        ('นุช', 'ดีงาม', 'Dentistry', '02-555-0004', 'nuch@petclinic.com'),
        ('วรรณ', 'พรหมดี', 'Exotic Animals', '02-555-0005', 'wan@petclinic.com'),
    ]
    c.executemany("INSERT OR IGNORE INTO vets (first_name,last_name,specialty,phone,email) VALUES (?,?,?,?,?)", vets)

    appointments = [
        (1, 1, '2024-11-01', 'Annual checkup', 'Completed', 'สุขภาพดี น้ำหนักปกติ'),
        (2, 3, '2024-11-05', 'Skin allergy', 'Completed', 'ผื่นบริเวณท้อง'),
        (3, 1, '2024-11-10', 'Vaccination', 'Completed', 'วัคซีนครบตามกำหนด'),
        (4, 5, '2024-11-12', 'Dental cleaning', 'Completed', None),
        (5, 2, '2024-11-15', 'Neutering', 'Completed', 'ผ่าตัดสำเร็จ'),
        (6, 1, '2024-11-20', 'Annual checkup', 'Completed', 'น้ำหนักเกิน แนะนำอาหาร'),
        (7, 3, '2024-12-01', 'Eye infection', 'Completed', 'ตาแดง มีขี้ตา'),
        (8, 5, '2024-12-05', 'Wing trim', 'Completed', None),
        (9, 1, '2024-12-10', 'Vaccination', 'Scheduled', None),
        (10, 2, '2024-12-15', 'Arthritis follow-up', 'Scheduled', None),
        (11, 4, '2024-12-18', 'Spaying', 'Scheduled', None),
        (12, 1, '2024-12-20', 'Annual checkup', 'Scheduled', None),
    ]
    c.executemany("INSERT OR IGNORE INTO appointments (pet_id,vet_id,appt_date,reason,status,notes) VALUES (?,?,?,?,?,?)", appointments)

    treatments = [
        (1, 'ตรวจร่างกายทั่วไป', None, 500.0),
        (1, 'เจาะเลือดตรวจ CBC', None, 800.0),
        (2, 'ฉีดยาแก้แพ้', 'Chlorpheniramine', 600.0),
        (2, 'ยาทาผิวหนัง', 'Betamethasone cream', 350.0),
        (3, 'วัคซีน 5 โรค', None, 900.0),
        (4, 'ขูดหินปูน', None, 1200.0),
        (5, 'ผ่าตัดทำหมัน', None, 3500.0),
        (5, 'ยาปฏิชีวนะหลังผ่าตัด', 'Amoxicillin', 400.0),
        (6, 'ตรวจร่างกายทั่วไป', None, 500.0),
        (7, 'ยาหยอดตา', 'Tobramycin eye drops', 450.0),
        (7, 'ยาต้านเชื้อ', 'Doxycycline', 380.0),
        (8, 'ตัดขนปีก', None, 300.0),
    ]
    c.executemany("INSERT OR IGNORE INTO treatments (appt_id,description,medication,cost) VALUES (?,?,?,?)", treatments)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == '__main__':
    init_db()
