import psycopg2
import timeit
import matplotlib.pyplot as plt

# Função para criar tabela
def create_table(cursor, table_name, columns, index=False):
    columns_str = ', '.join([f'{col} text' for col in columns])
    cursor.execute(f"CREATE TABLE {table_name} ({columns_str});")

    if index:
        for col in columns:
            cursor.execute(f"CREATE INDEX idx_{col} ON {table_name} ({col});")

# Função para executar a consulta
def run_query(cursor, query):
    cursor.execute(query)
    conn.commit()

# Criação da conexão com o banco
conn = psycopg2.connect(
    dbname="seu_banco_de_dados",
    user="seu_usuario",
    password="sua_senha",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

sizes = [100, 1000, 10000, 100000, 1000000]
no_index_times = []
index_times = []

for size in sizes:
    # Criando e preenchendo a tabela
    create_table(cur, 'tabela_teste', ['campo1'])
    for i in range(size):
        cur.execute(f"INSERT INTO tabela_teste(campo1) VALUES ('valor{i}');")

    conn.commit()

    # Medindo tempo de execução sem índice
    elapsed_time = timeit.timeit(lambda: run_query(cur, "EXPLAIN ANALYZE SELECT * FROM tabela_teste WHERE campo1 = 'valor500000';"), number=1)
    no_index_times.append(elapsed_time)

    # Dropando a tabela para criar com índice
    cur.execute("DROP TABLE tabela_teste;")

    # Criando a tabela com índice
    create_table(cur, 'tabela_teste', ['campo1'], index=True)
    for i in range(size):
        cur.execute(f"INSERT INTO tabela_teste(campo1) VALUES ('valor{i}');")

    conn.commit()

    # Medindo tempo de execução com índice
    elapsed_time = timeit.timeit(lambda: run_query(cur, "EXPLAIN ANALYZE SELECT * FROM tabela_teste WHERE campo1 = 'valor500000';"), number=1)
    index_times.append(elapsed_time)

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
