import timeit
import matplotlib.pyplot as plt
from setup import Setup

setup = Setup("localhost", "5432", "data", "postgres", "docker")

sizes = [100, 1000, 10000, 100000, 1000000]

no_index_times = []
index_times = []

setup.connect()
setup.create_text_function()

for size in sizes:
    setup.create_test_table(size)

    # Medindo tempo de execução sem índice
    elapsed_time = timeit.timeit(lambda: setup.execute_query("EXPLAIN ANALYZE SELECT * FROM test WHERE name = 'valor500000';"), number=1)
    no_index_times.append(elapsed_time)

    setup.drop_index_idx_text()

    # Criando o índice
    setup.create_index_idx_text()

    # Medindo tempo de execução com índice
    elapsed_time = timeit.timeit(lambda: setup.execute_query("EXPLAIN ANALYZE SELECT * FROM test WHERE name = 'valor500000';"), number=1)
    index_times.append(elapsed_time)

    setup.drop_index_idx_text()
    setup.drop_table("test")

setup.close_connection()

# Converter tempos para milissegundos
no_index_times = [time * 1000 for time in no_index_times]
index_times = [time * 1000 for time in index_times]

print(no_index_times)
print(index_times)

# Plotando os resultados
plt.plot(sizes, no_index_times, label='Sem índice')
plt.plot(sizes, index_times, label='Com índice')
plt.xlabel('Número de registros')
plt.ylabel('Tempo de execução (milissegundos)')
plt.title('B-Tree tempo de execução da consulta por tamanho da tabela')
plt.legend()
plt.show()
