import psycopg2
import time
import matplotlib.pyplot as plt

# Função para criar tabela
def create_table(cursor, table_name, columns, index=False):
    columns_str = ', '.join([f'{col} text' for col in columns])
    cursor.execute(f"CREATE TABLE {table_name} ({columns_str});")

    if index:
        for col in columns:
            cursor.execute(f"CREATE INDEX idx_{col} ON {table_name} ({col});")

# Criação da conexão com o banco
conn = psycopg2.connect(
    dbname="data",
    user="postgres",
    password="docker",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

sizes = [100 , 1000, 10000]#, 100000, 1000000]
no_index_times = []
index_times = []

for size in sizes:
    # Criando e preenchendo a tabela
    create_table(cur, 'tabela_teste', ['campo1'])
    for i in range(size):
        cur.execute(f"INSERT INTO tabela_teste(campo1) VALUES ('valor{i}');")

    conn.commit()

    # Medindo tempo de execução sem índice
    start = time.time()
    cur.execute("EXPLAIN ANALYZE SELECT * FROM tabela_teste WHERE campo1 = 'valor500000';")
    end = time.time()
    no_index_times.append(end - start)

    # Dropando a tabela para criar com índice
    cur.execute("DROP TABLE tabela_teste;")

    # Criando a tabela com índice
    create_table(cur, 'tabela_teste', ['campo1'], index=True)
    for i in range(size):
        cur.execute(f"INSERT INTO tabela_teste(campo1) VALUES ('valor{i}');")

    conn.commit()

    # Medindo tempo de execução com índice
    start = time.time()
    cur.execute("EXPLAIN ANALYZE SELECT * FROM tabela_teste WHERE campo1 = 'valor500000';")
    end = time.time()
    index_times.append(end - start)

    # Dropando a tabela para o próximo loop
    cur.execute("DROP TABLE tabela_teste;")

conn.close()

# Plotando os resultados
plt.plot(sizes, no_index_times, label='Sem índice')
plt.plot(sizes, index_times, label='Com índice')
plt.xlabel('Número de registros')
plt.ylabel('Tempo de execução (segundos)')
plt.legend()
plt.show()
