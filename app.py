from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
from init_db import init_db, DB_PATH

app = Flask(__name__)
app.secret_key = 'petclinic-cs104-secret'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ────────────── HOME ──────────────
@app.route('/')
def index():
    db = get_db()
    stats = {
        'owners': db.execute("SELECT COUNT(*) FROM owners").fetchone()[0],
        'pets':   db.execute("SELECT COUNT(*) FROM pets").fetchone()[0],
        'vets':   db.execute("SELECT COUNT(*) FROM vets").fetchone()[0],
        'appointments': db.execute("SELECT COUNT(*) FROM appointments").fetchone()[0],
    }
    recent = db.execute("""
        SELECT a.appt_id, p.name AS pet_name, o.first_name||' '||o.last_name AS owner,
               v.first_name||' '||v.last_name AS vet, a.appt_date, a.reason, a.status
        FROM appointments a
        JOIN pets p ON p.pet_id = a.pet_id
        JOIN owners o ON o.owner_id = p.owner_id
        JOIN vets v ON v.vet_id = a.vet_id
        ORDER BY a.appt_date DESC LIMIT 5
    """).fetchall()
    db.close()
    return render_template('index.html', stats=stats, recent=recent)


# ════════════ OWNERS ════════════
@app.route('/owners')
def owners():
    db = get_db()
    q = request.args.get('q', '')
    if q:
        rows = db.execute("""SELECT o.*, COUNT(p.pet_id) AS pet_count FROM owners o
            LEFT JOIN pets p ON p.owner_id = o.owner_id
            WHERE o.first_name LIKE ? OR o.last_name LIKE ? OR o.email LIKE ?
            GROUP BY o.owner_id""", (f'%{q}%', f'%{q}%', f'%{q}%')).fetchall()
    else:
        rows = db.execute("""SELECT o.*, COUNT(p.pet_id) AS pet_count FROM owners o
            LEFT JOIN pets p ON p.owner_id = o.owner_id GROUP BY o.owner_id""").fetchall()
    db.close()
    return render_template('owners.html', owners=rows, q=q)

@app.route('/owners/new', methods=['GET', 'POST'])
def owner_new():
    if request.method == 'POST':
        db = get_db()
        try:
            db.execute("INSERT INTO owners (first_name,last_name,phone,email,address) VALUES (?,?,?,?,?)",
                (request.form['first_name'], request.form['last_name'],
                 request.form['phone'], request.form['email'], request.form['address']))
            db.commit()
            flash('เพิ่มเจ้าของสำเร็จ', 'success')
            return redirect(url_for('owners'))
        except sqlite3.IntegrityError:
            flash('อีเมลนี้มีอยู่แล้วในระบบ', 'error')
        finally:
            db.close()
    return render_template('owner_form.html', owner=None)

@app.route('/owners/<int:oid>/edit', methods=['GET', 'POST'])
def owner_edit(oid):
    db = get_db()
    owner = db.execute("SELECT * FROM owners WHERE owner_id=?", (oid,)).fetchone()
    if request.method == 'POST':
        try:
            db.execute("UPDATE owners SET first_name=?,last_name=?,phone=?,email=?,address=? WHERE owner_id=?",
                (request.form['first_name'], request.form['last_name'],
                 request.form['phone'], request.form['email'], request.form['address'], oid))
            db.commit()
            flash('แก้ไขข้อมูลสำเร็จ', 'success')
            return redirect(url_for('owners'))
        except sqlite3.IntegrityError:
            flash('อีเมลนี้มีอยู่แล้วในระบบ', 'error')
        finally:
            db.close()
    else:
        db.close()
    return render_template('owner_form.html', owner=owner)

@app.route('/owners/<int:oid>/delete', methods=['POST'])
def owner_delete(oid):
    db = get_db()
    db.execute("DELETE FROM owners WHERE owner_id=?", (oid,))
    db.commit()
    db.close()
    flash('ลบเจ้าของสำเร็จ', 'success')
    return redirect(url_for('owners'))


# ════════════ PETS ════════════
@app.route('/pets')
def pets():
    db = get_db()
    q = request.args.get('q', '')
    if q:
        rows = db.execute("""SELECT p.*, o.first_name||' '||o.last_name AS owner_name
            FROM pets p JOIN owners o ON o.owner_id=p.owner_id
            WHERE p.name LIKE ? OR p.species LIKE ? OR p.breed LIKE ?""",
            (f'%{q}%', f'%{q}%', f'%{q}%')).fetchall()
    else:
        rows = db.execute("""SELECT p.*, o.first_name||' '||o.last_name AS owner_name
            FROM pets p JOIN owners o ON o.owner_id=p.owner_id""").fetchall()
    owners = db.execute("SELECT owner_id, first_name||' '||last_name AS name FROM owners").fetchall()
    db.close()
    return render_template('pets.html', pets=rows, owners=owners, q=q)

@app.route('/pets/new', methods=['GET', 'POST'])
def pet_new():
    db = get_db()
    if request.method == 'POST':
        db.execute("INSERT INTO pets (owner_id,name,species,breed,birth_date) VALUES (?,?,?,?,?)",
            (request.form['owner_id'], request.form['name'],
             request.form['species'], request.form['breed'], request.form['birth_date']))
        db.commit()
        db.close()
        flash('เพิ่มสัตว์เลี้ยงสำเร็จ', 'success')
        return redirect(url_for('pets'))
    owners = db.execute("SELECT owner_id, first_name||' '||last_name AS name FROM owners").fetchall()
    db.close()
    return render_template('pet_form.html', pet=None, owners=owners)

@app.route('/pets/<int:pid>/edit', methods=['GET', 'POST'])
def pet_edit(pid):
    db = get_db()
    pet = db.execute("SELECT * FROM pets WHERE pet_id=?", (pid,)).fetchone()
    if request.method == 'POST':
        db.execute("UPDATE pets SET owner_id=?,name=?,species=?,breed=?,birth_date=? WHERE pet_id=?",
            (request.form['owner_id'], request.form['name'],
             request.form['species'], request.form['breed'], request.form['birth_date'], pid))
        db.commit()
        db.close()
        flash('แก้ไขข้อมูลสัตว์เลี้ยงสำเร็จ', 'success')
        return redirect(url_for('pets'))
    owners = db.execute("SELECT owner_id, first_name||' '||last_name AS name FROM owners").fetchall()
    db.close()
    return render_template('pet_form.html', pet=pet, owners=owners)

@app.route('/pets/<int:pid>/delete', methods=['POST'])
def pet_delete(pid):
    db = get_db()
    db.execute("DELETE FROM pets WHERE pet_id=?", (pid,))
    db.commit()
    db.close()
    flash('ลบสัตว์เลี้ยงสำเร็จ', 'success')
    return redirect(url_for('pets'))


# ════════════ VETS ════════════
@app.route('/vets')
def vets():
    db = get_db()
    rows = db.execute("SELECT * FROM vets").fetchall()
    db.close()
    return render_template('vets.html', vets=rows)

@app.route('/vets/new', methods=['GET', 'POST'])
def vet_new():
    if request.method == 'POST':
        db = get_db()
        try:
            db.execute("INSERT INTO vets (first_name,last_name,specialty,phone,email) VALUES (?,?,?,?,?)",
                (request.form['first_name'], request.form['last_name'],
                 request.form['specialty'], request.form['phone'], request.form['email']))
            db.commit()
            flash('เพิ่มสัตวแพทย์สำเร็จ', 'success')
            return redirect(url_for('vets'))
        except sqlite3.IntegrityError:
            flash('อีเมลนี้มีอยู่แล้วในระบบ', 'error')
        finally:
            db.close()
    return render_template('vet_form.html', vet=None)

@app.route('/vets/<int:vid>/edit', methods=['GET', 'POST'])
def vet_edit(vid):
    db = get_db()
    vet = db.execute("SELECT * FROM vets WHERE vet_id=?", (vid,)).fetchone()
    if request.method == 'POST':
        try:
            db.execute("UPDATE vets SET first_name=?,last_name=?,specialty=?,phone=?,email=? WHERE vet_id=?",
                (request.form['first_name'], request.form['last_name'],
                 request.form['specialty'], request.form['phone'], request.form['email'], vid))
            db.commit()
            flash('แก้ไขข้อมูลสัตวแพทย์สำเร็จ', 'success')
            return redirect(url_for('vets'))
        except sqlite3.IntegrityError:
            flash('อีเมลนี้มีอยู่แล้วในระบบ', 'error')
        finally:
            db.close()
    else:
        db.close()
    return render_template('vet_form.html', vet=vet)

@app.route('/vets/<int:vid>/delete', methods=['POST'])
def vet_delete(vid):
    db = get_db()
    db.execute("DELETE FROM vets WHERE vet_id=?", (vid,))
    db.commit()
    db.close()
    flash('ลบสัตวแพทย์สำเร็จ', 'success')
    return redirect(url_for('vets'))


# ════════════ APPOINTMENTS ════════════
@app.route('/appointments')
def appointments():
    db = get_db()
    status_filter = request.args.get('status', '')
    q = "SELECT a.*, p.name AS pet_name, o.first_name||' '||o.last_name AS owner_name, v.first_name||' '||v.last_name AS vet_name FROM appointments a JOIN pets p ON p.pet_id=a.pet_id JOIN owners o ON o.owner_id=p.owner_id JOIN vets v ON v.vet_id=a.vet_id"
    if status_filter:
        rows = db.execute(q + " WHERE a.status=? ORDER BY a.appt_date DESC", (status_filter,)).fetchall()
    else:
        rows = db.execute(q + " ORDER BY a.appt_date DESC").fetchall()
    db.close()
    return render_template('appointments.html', appointments=rows, status_filter=status_filter)

@app.route('/appointments/new', methods=['GET', 'POST'])
def appt_new():
    db = get_db()
    if request.method == 'POST':
        db.execute("INSERT INTO appointments (pet_id,vet_id,appt_date,reason,status,notes) VALUES (?,?,?,?,?,?)",
            (request.form['pet_id'], request.form['vet_id'], request.form['appt_date'],
             request.form['reason'], request.form['status'], request.form['notes']))
        db.commit()
        db.close()
        flash('เพิ่มนัดหมายสำเร็จ', 'success')
        return redirect(url_for('appointments'))
    pets = db.execute("SELECT p.pet_id, p.name||' ('||o.first_name||' '||o.last_name||')' AS label FROM pets p JOIN owners o ON o.owner_id=p.owner_id").fetchall()
    vets = db.execute("SELECT vet_id, first_name||' '||last_name AS name FROM vets").fetchall()
    db.close()
    return render_template('appt_form.html', appt=None, pets=pets, vets=vets)

@app.route('/appointments/<int:aid>/edit', methods=['GET', 'POST'])
def appt_edit(aid):
    db = get_db()
    appt = db.execute("SELECT * FROM appointments WHERE appt_id=?", (aid,)).fetchone()
    if request.method == 'POST':
        db.execute("UPDATE appointments SET pet_id=?,vet_id=?,appt_date=?,reason=?,status=?,notes=? WHERE appt_id=?",
            (request.form['pet_id'], request.form['vet_id'], request.form['appt_date'],
             request.form['reason'], request.form['status'], request.form['notes'], aid))
        db.commit()
        db.close()
        flash('แก้ไขนัดหมายสำเร็จ', 'success')
        return redirect(url_for('appointments'))
    pets = db.execute("SELECT p.pet_id, p.name||' ('||o.first_name||' '||o.last_name||')' AS label FROM pets p JOIN owners o ON o.owner_id=p.owner_id").fetchall()
    vets = db.execute("SELECT vet_id, first_name||' '||last_name AS name FROM vets").fetchall()
    db.close()
    return render_template('appt_form.html', appt=appt, pets=pets, vets=vets)

@app.route('/appointments/<int:aid>/delete', methods=['POST'])
def appt_delete(aid):
    db = get_db()
    db.execute("DELETE FROM appointments WHERE appt_id=?", (aid,))
    db.commit()
    db.close()
    flash('ลบนัดหมายสำเร็จ', 'success')
    return redirect(url_for('appointments'))


# ════════════ TREATMENTS ════════════
@app.route('/treatments')
def treatments():
    db = get_db()
    rows = db.execute("""SELECT t.*, a.reason, a.appt_date, p.name AS pet_name
        FROM treatments t JOIN appointments a ON a.appt_id=t.appt_id
        JOIN pets p ON p.pet_id=a.pet_id ORDER BY a.appt_date DESC""").fetchall()
    db.close()
    return render_template('treatments.html', treatments=rows)

@app.route('/treatments/new', methods=['GET', 'POST'])
def treat_new():
    db = get_db()
    if request.method == 'POST':
        db.execute("INSERT INTO treatments (appt_id,description,medication,cost) VALUES (?,?,?,?)",
            (request.form['appt_id'], request.form['description'],
             request.form['medication'], request.form['cost']))
        db.commit()
        db.close()
        flash('เพิ่มการรักษาสำเร็จ', 'success')
        return redirect(url_for('treatments'))
    appts = db.execute("""SELECT a.appt_id, p.name||' - '||a.reason||' ('||a.appt_date||')' AS label
        FROM appointments a JOIN pets p ON p.pet_id=a.pet_id ORDER BY a.appt_date DESC""").fetchall()
    db.close()
    return render_template('treat_form.html', treat=None, appts=appts)

@app.route('/treatments/<int:tid>/edit', methods=['GET', 'POST'])
def treat_edit(tid):
    db = get_db()
    treat = db.execute("SELECT * FROM treatments WHERE treat_id=?", (tid,)).fetchone()
    if request.method == 'POST':
        db.execute("UPDATE treatments SET appt_id=?,description=?,medication=?,cost=? WHERE treat_id=?",
            (request.form['appt_id'], request.form['description'],
             request.form['medication'], request.form['cost'], tid))
        db.commit()
        db.close()
        flash('แก้ไขการรักษาสำเร็จ', 'success')
        return redirect(url_for('treatments'))
    appts = db.execute("""SELECT a.appt_id, p.name||' - '||a.reason||' ('||a.appt_date||')' AS label
        FROM appointments a JOIN pets p ON p.pet_id=a.pet_id ORDER BY a.appt_date DESC""").fetchall()
    db.close()
    return render_template('treat_form.html', treat=treat, appts=appts)

@app.route('/treatments/<int:tid>/delete', methods=['POST'])
def treat_delete(tid):
    db = get_db()
    db.execute("DELETE FROM treatments WHERE treat_id=?", (tid,))
    db.commit()
    db.close()
    flash('ลบการรักษาสำเร็จ', 'success')
    return redirect(url_for('treatments'))


if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(debug=True)
