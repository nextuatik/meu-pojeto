from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3, os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# --- CONFIGURAÇÕES ---
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
DB_NAME = 'barbearia.db'

# --- FUNÇÕES AUXILIARES ---
def conectar_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabelas():
    conn = conectar_db()

    # Tabelas existentes
    conn.execute('''CREATE TABLE IF NOT EXISTS barbeiros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        foto_url TEXT,
        ativo INTEGER
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS datas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT,
        ativo INTEGER
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS horarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_cliente TEXT,
        telefone TEXT,
        servico TEXT,
        barbeiro_nome TEXT,
        data TEXT,
        hora TEXT,
        observacoes TEXT
    )''')

    # Tabela de admins
    conn.execute('''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        senha_hash TEXT
    )''')

    # Criar admin padrão se não existir
    admin_existente = conn.execute('SELECT * FROM admins WHERE usuario=?', ('admin',)).fetchone()
    if not admin_existente:
        conn.execute(
            'INSERT INTO admins (usuario, senha_hash) VALUES (?, ?)',
            ('admin', generate_password_hash('1234'))
        )

    conn.commit()
    conn.close()

def salvar_foto(file):
    if file:
        filename = secure_filename(file.filename)
        caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(caminho)
        return caminho
    return None

def verificar_login():
    if not session.get('admin_logado'):
        return redirect(url_for('login_admin'))
    return None

# --- ROTAS CLIENTE ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/agendamento')
def agendamento():
    conn = conectar_db()
    barbeiros = conn.execute('SELECT * FROM barbeiros WHERE ativo=1').fetchall()
    datas = conn.execute('SELECT * FROM datas WHERE ativo=1').fetchall()
    conn.close()
    return render_template('agendamento.html', barbeiros=barbeiros, datas=datas)

# --- ROTAS ADMIN ---
@app.route('/admin/login', methods=['GET', 'POST'])
def login_admin():
    erro = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        conn = conectar_db()
        admin = conn.execute('SELECT * FROM admins WHERE usuario=?', (usuario,)).fetchone()
        conn.close()

        if admin and check_password_hash(admin['senha_hash'], senha):
            session['admin_logado'] = True
            return redirect(url_for('dashboard'))
        else:
            erro = "Usuário ou senha incorretos."
    return render_template('login.html', erro=erro)

@app.route('/admin/logout')
def logout_admin():
    session.pop('admin_logado', None)
    return redirect(url_for('login_admin'))

@app.route('/admin')
def dashboard():
    redirect_login = verificar_login()
    if redirect_login:
        return redirect_login

    conn = conectar_db()
    barbeiros = conn.execute('SELECT * FROM barbeiros').fetchall()
    datas = conn.execute('SELECT * FROM datas').fetchall()
    horarios = conn.execute('SELECT * FROM horarios').fetchall()
    conn.close()
    return render_template('admin/admin.html', barbeiros=barbeiros, datas=datas, horarios=horarios)

# --- FUNÇÕES ADMIN ---
@app.route('/admin/adicionar_barbeiro', methods=['POST'])
def adicionar_barbeiro():
    redirect_login = verificar_login()
    if redirect_login:
        return redirect_login

    nome = request.form['nome']
    foto_file = request.files.get('foto')
    foto_url = salvar_foto(foto_file)
    conn = conectar_db()
    conn.execute('INSERT INTO barbeiros (nome, foto_url, ativo) VALUES (?, ?, 1)', (nome, foto_url))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/admin/editar_agendamento/<int:id>', methods=['GET', 'POST'])
def editar_agendamento(id):
    redirect_login = verificar_login()
    if redirect_login:
        return redirect_login

    conn = conectar_db()

    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        servico = request.form['servico']
        barbeiro = request.form['barbeiro']
        data = request.form['data']
        hora = request.form['hora']
        observacoes = request.form['observacoes']

        conn.execute('''
            UPDATE horarios 
            SET nome_cliente=?, telefone=?, servico=?, barbeiro_nome=?, data=?, hora=?, observacoes=?
            WHERE id=?
        ''', (nome, telefone, servico, barbeiro, data, hora, observacoes, id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    agendamento = conn.execute('SELECT * FROM horarios WHERE id=?', (id,)).fetchone()
    barbeiros = conn.execute('SELECT * FROM barbeiros WHERE ativo=1').fetchall()
    datas = conn.execute('SELECT * FROM datas WHERE ativo=1').fetchall()
    conn.close()

    return render_template('admin/editar_agendamento.html', agendamento=agendamento, barbeiros=barbeiros, datas=datas)

@app.route('/admin/editar_barbeiro', methods=['POST'])
def editar_barbeiro():
    redirect_login = verificar_login()
    if redirect_login:
        return redirect_login

    id_b = request.form['id']
    ativo = 1 if 'ativo' in request.form else 0
    conn = conectar_db()
    conn.execute('UPDATE barbeiros SET ativo=? WHERE id=?', (ativo, id_b))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/admin/adicionar_data', methods=['POST'])
def adicionar_data():
    redirect_login = verificar_login()
    if redirect_login:
        return redirect_login

    nova_data = request.form['nova_data']
    conn = conectar_db()
    conn.execute('INSERT INTO datas (data, ativo) VALUES (?,1)', (nova_data,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/admin/editar_data', methods=['POST'])
def editar_data():
    redirect_login = verificar_login()
    if redirect_login:
        return redirect_login

    id_d = request.form['id']
    ativo = 1 if 'ativo' in request.form else 0
    conn = conectar_db()
    conn.execute('UPDATE datas SET ativo=? WHERE id=?', (ativo, id_d))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/admin/excluir_horario/<int:id>')
def excluir_horario(id):
    redirect_login = verificar_login()
    if redirect_login:
        return redirect_login

    conn = conectar_db()
    conn.execute('DELETE FROM horarios WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# --- HORÁRIOS ---
@app.route('/horarios_disponiveis')
def horarios_disponiveis():
    barbeiro = request.args.get('barbeiro')
    data = request.args.get('data')

    horarios_fixos = [
        "08:00", "09:00", "10:00", "11:00",
        "13:00", "14:00", "15:00",
        "16:00", "17:00", "18:00", "19:00", "20:00"
    ]

    conn = conectar_db()
    resultados = conn.execute(
        'SELECT hora FROM horarios WHERE barbeiro_nome = ? AND data = ?',
        (barbeiro, data)
    ).fetchall()
    conn.close()

    ocupados = [r['hora'] for r in resultados]
    livres = [h for h in horarios_fixos if h not in ocupados]

    return jsonify(livres)

@app.route('/enviar', methods=['POST'])
def enviar():
    nome = request.form.get('nome')
    telefone = request.form.get('telefone')
    servico = request.form.get('servico')
    barbeiro = request.form.get('barbeiro')
    data_agendada = request.form.get('data')
    hora = request.form.get('hora')
    observacoes = request.form.get('observacoes')

    conn = conectar_db()
    existente = conn.execute(
        'SELECT * FROM horarios WHERE barbeiro_nome=? AND data=? AND hora=?',
        (barbeiro, data_agendada, hora)
    ).fetchone()

    if existente:
        conn.close()
        return jsonify({'sucesso': "0"})

    conn.execute(
        '''INSERT INTO horarios 
        (nome_cliente, telefone, servico, barbeiro_nome, data, hora, observacoes)
        VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (nome, telefone, servico, barbeiro, data_agendada, hora, observacoes)
    )
    conn.commit()
    conn.close()

    return jsonify({'sucesso': "1"})

# --- EXECUÇÃO ---
if __name__ == '__main__':
    criar_tabelas()
    app.run(debug=True)
