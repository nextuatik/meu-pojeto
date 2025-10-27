import sqlite3

# Conectar (vai criar o arquivo barbearia.db se não existir)
conn = sqlite3.connect('barbearia.db')
cursor = conn.cursor()

# Criar tabela de barbeiros
cursor.execute('''
CREATE TABLE IF NOT EXISTS barbeiros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    foto_url TEXT,
    ativo INTEGER DEFAULT 1
)
''')

# Criar tabela de datas disponíveis
cursor.execute('''
CREATE TABLE IF NOT EXISTS datas_disponiveis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    ativo INTEGER DEFAULT 1
)
''')

# Criar tabela de agendamentos
cursor.execute('''
CREATE TABLE IF NOT EXISTS agendamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_cliente TEXT NOT NULL,
    telefone TEXT NOT NULL,
    servico TEXT NOT NULL,
    barbeiro_id INTEGER,
    data TEXT NOT NULL,
    hora TEXT NOT NULL,
    observacoes TEXT,
    FOREIGN KEY (barbeiro_id) REFERENCES barbeiros(id)
)
''')

conn.commit()
conn.close()

print("✅ Banco de dados criado com sucesso!")
