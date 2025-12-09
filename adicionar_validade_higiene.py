import sqlite3

con = sqlite3.connect('comercio.db')
cur = con.cursor()

# Definir validade padrão para produtos de Higiene Pessoal
validade_padrao = '2027-12'  # formato YYYY-MM
cur.execute("""
    UPDATE produtos SET validade=? WHERE categoria='Higiene Pessoal'
""", (validade_padrao,))

con.commit()
con.close()
print('Validade adicionada aos produtos de Higiene Pessoal!')
