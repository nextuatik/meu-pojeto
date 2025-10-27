from flask import Blueprint, render_template, request, jsonify
from app import conectar_db

cliente_bp = Blueprint('cliente', __name__)

@cliente_bp.route('/')
def index():
    return render_template('cliente/index.html')

@cliente_bp.route('/agendamento')
def agendamento():
    conn = conectar_db()
    barbeiros = conn.execute('SELECT * FROM barbeiros WHERE ativo=1').fetchall()
    datas = conn.execute('SELECT * FROM datas WHERE ativo=1').fetchall()
    conn.close()
    return render_template('cliente/agendamento.html', barbeiros=barbeiros, datas=datas)

@cliente_bp.route('/horarios_disponiveis')
def horarios_disponiveis():
    barbeiro_nome = request.args.get('barbeiro')
    data = request.args.get('data')
    todos = ["08:00", "09:00", "10:00", "11:00","13:00","14:00","15:00","16:00"]
    conn = conectar_db()
    agendados = conn.execute('SELECT hora FROM horarios WHERE barbeiro_nome=? AND data=?', (barbeiro_nome, data)).fetchall()
    conn.close()
    ocupados = [a['hora'] for a in agendados]
    livres = [h for h in todos if h not in ocupados]
    return jsonify(livres)

@cliente_bp.route('/enviar', methods=['POST'])
def enviar():
    data = request.form
    conn = conectar_db()
    existente = conn.execute('SELECT * FROM horarios WHERE barbeiro_nome=? AND data=? AND hora=?', (data['barbeiro'], data['data'], data['hora'])).fetchone()
    if existente:
        conn.close()
        return jsonify({"sucesso": "0"})
    conn.execute('INSERT INTO horarios (nome_cliente, telefone, servico, barbeiro_nome, data, hora, observacoes) VALUES (?, ?, ?, ?, ?, ?, ?)', (data['nome'], data['telefone'], data['servico'], data['barbeiro'], data['data'], data['hora'], data['observacoes']))
    conn.commit()
    conn.close()
    return jsonify({"sucesso": "1"})
