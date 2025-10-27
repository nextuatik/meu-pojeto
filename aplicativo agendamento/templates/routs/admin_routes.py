from flask import Blueprint, render_template, request, redirect, url_for
from app import conectar_db, salvar_foto

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
def admin():
    conn = conectar_db()
    barbeiros = conn.execute('SELECT * FROM barbeiros').fetchall()
    datas = conn.execute('SELECT * FROM datas').fetchall()
    horarios = conn.execute('SELECT * FROM horarios').fetchall()
    conn.close()
    return render_template('admin/admin.html', barbeiros=barbeiros, datas=datas, horarios=horarios)

@admin_bp.route('/adicionar_barbeiro', methods=['POST'])
def adicionar_barbeiro():
    nome = request.form['nome']
    foto_file = request.files.get('foto')
    foto_url = salvar_foto(foto_file)
    conn = conectar_db()
    conn.execute('INSERT INTO barbeiros (nome, foto_url, ativo) VALUES (?, ?, 1)', (nome, foto_url))
    conn.commit()
    conn.close()
    return redirect(url_for('admin.admin'))

# Adicione aqui todas as outras rotas do admin (editar, adicionar_data, excluir etc.)
