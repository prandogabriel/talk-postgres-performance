import timeit
import matplotlib.pyplot as plt
# from setup import Setup, create_test_table, create_index, drop_index
from setup import Setup

def run_test(table_create_method, index_create_method, index_drop_method, explain_query, graph_title):
    setup = Setup("localhost", "5432", "data", "postgres", "docker")
    sizes = [100, 1000, 10000, 100000, 1000000]
    no_index_times = []
    index_times = []

    setup.connect()
    setup.create_text_function()

    for size in sizes:
        table_create_method(setup, size)

        # Medindo tempo de execução sem índice
        elapsed_time = timeit.timeit(lambda: setup.execute_query(explain_query), number=1)
        no_index_times.append(elapsed_time)

        index_drop_method(setup)

        # Criando o índice
        index_create_method(setup)

        # Medindo tempo de execução com índice
        elapsed_time = timeit.timeit(lambda: setup.execute_query(explain_query), number=1)
        index_times.append(elapsed_time)

        index_drop_method(setup)
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
    plt.title(graph_title)
    plt.legend()
    plt.show()

# # Consulta EXPLAIN
# explain_query = "EXPLAIN ANALYZE SELECT * FROM test WHERE name = 'valor500000';"

# # Título do gráfico
# graph_title = 'Tempo de execução da consulta por tamanho da tabela'

# # Chamar a função para executar o teste com os parâmetros desejados
# run_test(create_test_table, create_index, drop_index, explain_query, graph_title)
