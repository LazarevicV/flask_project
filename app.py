from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = "RAF2021-2022"

mydb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = '',
    database = 'kolokvijum2priprema'
)

@app.route('/')
def hello_world():  # put application's code here
    return render_template(
        'index.html',
        poruka = 'Home page'
    )

@app.route('/register', methods = ["POST", 'GET'])
def register():

    if request.method == 'GET':
        return render_template(
            'register.html',
        )

    if request.method == 'POST':
        broj_indeksa = request.form.get('broj_indeksa')
        ime_prezime = request.form.get('ime_prezime')
        godina_rodjenja = request.form.get('godina_rodjenja')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        prosek = request.form.get('prosek')
        broj_polozenih_ispita = request.form.get('broj_polozenih_ispita')

        if broj_indeksa == '' or ime_prezime == '' or godina_rodjenja == '' or password == '' or confirm_password == '' or prosek == '' or broj_polozenih_ispita == '':
            return render_template(
                'register.html',
                greska = 'Sva polja moraju biti popunjena!',
                broj_indeksa=broj_indeksa,
                ime_prezime=ime_prezime,
                godina_rodjenja=godina_rodjenja,
                prosek=prosek,
                broj_polozenih_ispita=broj_polozenih_ispita
            )

        sql = 'SELECT * FROM korisnik WHERE broj_indeksa = ?'
        parametri = (broj_indeksa, )
        cursor = mydb.cursor(prepared=True)
        cursor.execute(sql, parametri)
        rezultat_upita = cursor.fetchone()

        if rezultat_upita != None:
            return render_template(
                'register.html',
                greska_broj_indeksa = 'Vec postojeci indeks!',
                broj_indeksa = broj_indeksa,
                ime_prezime = ime_prezime,
                godina_rodjenja = godina_rodjenja,
                prosek = prosek,
                broj_polozenih_ispita = broj_polozenih_ispita
            )

        if ' ' not in ime_prezime:
            return render_template(
                'register.html',
                greska_ime_prezime = 'Morate uneti i ime i prezime!',
                broj_indeksa=broj_indeksa,
                ime_prezime=ime_prezime,
                godina_rodjenja=godina_rodjenja,
                prosek=prosek,
                broj_polozenih_ispita=broj_polozenih_ispita
            )
        godina_rodjenja = int(godina_rodjenja)
        if godina_rodjenja < 0 or godina_rodjenja > 2023:
            return render_template(
                'register.html',
                greska_godina_rodjenja = 'Godina mora biti > 0 i < 2023!',
                broj_indeksa=broj_indeksa,
                ime_prezime=ime_prezime,
                godina_rodjenja=godina_rodjenja,
                prosek=prosek,
                broj_polozenih_ispita=broj_polozenih_ispita
            )

        if password != confirm_password:
            return render_template(
                'register.html',
                greska_password = 'Sifre se moraju poklapati!',
                broj_indeksa=broj_indeksa,
                ime_prezime=ime_prezime,
                godina_rodjenja=godina_rodjenja,
                prosek=prosek,
                broj_polozenih_ispita=broj_polozenih_ispita
            )

        prosek = float(prosek)
        if prosek < 6 or prosek > 10:
            return render_template(
                'register.html',
                greska_prosek = 'Prosek mora biti izmedju 6 i 10!',
                broj_indeksa=broj_indeksa,
                ime_prezime=ime_prezime,
                godina_rodjenja=godina_rodjenja,
                prosek=prosek,
                broj_polozenih_ispita=broj_polozenih_ispita
            )

        broj_polozenih_ispita = int(broj_polozenih_ispita)
        if broj_polozenih_ispita < 0:
            return render_template(
                'register.html',
                greska_broj_polozenih = 'Broj polozenih ispita ne moze biti negativan broj!',
                broj_indeksa=broj_indeksa,
                ime_prezime=ime_prezime,
                godina_rodjenja=godina_rodjenja,
                prosek=prosek,
                broj_polozenih_ispita=broj_polozenih_ispita
            )

        sql = '''
            INSERT INTO korisnik
            VALUES (null, ?, ?, ?, ?, ?, ?)
        '''
        parametri = (broj_indeksa, ime_prezime, godina_rodjenja, password, prosek, broj_polozenih_ispita)
        cursor = mydb.cursor(prepared=True)
        cursor.execute(sql, parametri)
        mydb.commit()

        return redirect(url_for('show_all'))

def decode_bytearray_tuple(bytearray_tuple):
    bytearray_tuple = list(bytearray_tuple)
    n = len(bytearray_tuple)
    for i in range(n):
        if isinstance(bytearray_tuple[i], bytearray):
            bytearray_tuple[i] = bytearray_tuple[i].decode()
    return bytearray_tuple

def decode_bytearray_list(bytearray_list):
    n = len(bytearray_list)
    for i in range(n):
        bytearray_list[i] = decode_bytearray_tuple(bytearray_list[i])
    return bytearray_list

@app.route('/show_all')
def show_all():

    sql = 'SELECT * FROM korisnik'
    cursor = mydb.cursor(prepared=True)
    cursor.execute(sql)
    rezultat_upita = cursor.fetchall()

    rezultat_upita = decode_bytearray_list(rezultat_upita)

    return render_template(
        'show_all.html',
        svi_korisnici = rezultat_upita
    )

@app.route('/login', methods = ['POST', 'GET'])
def login():

    if request.method == 'GET':
        return render_template(
            'login.html',
        )

    if request.method == 'POST':
        broj_indeksa = request.form.get('broj_indeksa')
        password = request.form.get('password')

        if broj_indeksa == '' or password == '':
            return render_template(
                'login.html',
                greska = 'Sva polja moraju biti popunjena!'
            )
        sql = 'SELECT * FROM korisnik WHERE broj_indeksa = ?'
        parametri = (broj_indeksa, )
        cursor = mydb.cursor(prepared=True)
        cursor.execute(sql, parametri)
        rezultat_upita = cursor.fetchone()

        if rezultat_upita == None:
            return render_template(
                'login.html',
                greska_broj_indeksa = 'Nepostojeci korisnik!'
            )
        rezultat_upita = decode_bytearray_tuple(rezultat_upita)
        if rezultat_upita[4] != password:
            return render_template(
                'login.html',
                greska_password = 'Pogresna sifra!'
            )

        print(rezultat_upita)

        session['ulogovani_id'] = rezultat_upita[0]
        session['ulogovani_broj_indeksa'] = rezultat_upita[1]
        session['ulogovani_password'] = rezultat_upita[4]

        return redirect(url_for('show_all'))

@app.route('/logout')
def logout():
    if 'ulogovani_id' in session:
        del session['ulogovani_id']
        del session['ulogovani_broj_indeksa']
        del session['ulogovani_password']
        return redirect(url_for('show_all'))

    return redirect(url_for('login'))

@app.route('/delete/<id>')
def delete(id):

    if 'ulogovani_id' not in session:
        return redirect(url_for('login'))

    sql = 'DELETE FROM korisnik WHERE id = ?'
    parametri = (id, )

    cursor = mydb.cursor(prepared=True)
    cursor.execute(sql, parametri)
    mydb.commit()
    return redirect(url_for('show_all'))

@app.route('/update/<id>', methods = ["POST", "GET"])
def update(id):

    if 'ulogovani_id' not in session:
        return redirect(url_for('login'))

    sql = 'SELECT * FROM korisnik WHERE id = ?'
    parametri = (id, )
    cursor = mydb.cursor(prepared=True)
    cursor.execute(sql, parametri)
    rezultat_upita = cursor.fetchone()

    rezultat_upita = decode_bytearray_tuple(rezultat_upita)

    if request.method == 'GET':
        return render_template(
            'update.html',
            korisnik = rezultat_upita
        )

    if request.method == 'POST':

        ime_prezime = request.form.get('ime_prezime')
        godina_rodjenja = request.form.get('godina_rodjenja')
        prosek = request.form.get('prosek')
        broj_polozenih_ispita = request.form.get('broj_polozenih_ispita')
        password = request.form.get('password')

        if ime_prezime == '' or godina_rodjenja == '' or prosek == '' or broj_polozenih_ispita == '' or password == '':
            return render_template(
                'update.html',
                ime_prezime = ime_prezime,
                godina_rodjenja = godina_rodjenja,
                prosek = prosek,
                broj_polozenih_ispita = broj_polozenih_ispita,
                greska = 'Sva polja moraju biti popunjena!'
            )

        sql = '''
            UPDATE korisnik
            SET ime_prezime = ?, godina_rodjenja = ?, sifra = ?, prosek = ?, polozeni_ispiti = ?
            WHERE id = ?
        '''
        parametri = (ime_prezime, godina_rodjenja, password, prosek, broj_polozenih_ispita, id)
        cursor = mydb.cursor(prepared=True)
        cursor.execute(sql, parametri)
        mydb.commit()

        return redirect(url_for('show_all'))

if __name__ == '__main__':
    app.run(debug=True)
