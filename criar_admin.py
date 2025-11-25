from werkzeug.security import generate_password_hash
import sqlite3

senha = "123456"  
hash_senha = generate_password_hash(senha)

conn = sqlite3.connect('locadora.db')
cursor = conn.cursor()
cursor.execute('''
    INSERT INTO clientes (nome, email, senha, role)
    VALUES (?, ?, ?, ?)
''', ("Admin", "admin@locadora.com", hash_senha, "admin"))
conn.commit()
conn.close()

print("Admin criado com sucesso!")
