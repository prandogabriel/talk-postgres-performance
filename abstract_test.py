import timeit
import matplotlib.pyplot as plt
from setup import Setup

def run_test(stp, table_create_method, index_create_method, index_drop_method, explain_query, graph_title):
    sizes = [100, 1000, 10000, 100000, 1000000]
    no_index_times = []
    index_times = []

    stp.connect()
    stp.create_text_function()

    for size in sizes:
        table_create_method(size)

        # Medindo tempo de execução sem índice
        elapsed_time = timeit.timeit(lambda: stp.execute_query(explain_query), number=1)
        no_index_times.append(elapsed_time)

        index_drop_method()

        # Criando o índice
        index_create_method()

        # Medindo tempo de execução com índice
        elapsed_time = timeit.timeit(lambda: stp.execute_query(explain_query), number=1)
        index_times.append(elapsed_time)

        index_drop_method()

    stp.close_connection()

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



stp = Setup("localhost", "5432", "data", "postgres", "docker")


# --------------------- btree START -----------------------------
explain_query = "EXPLAIN ANALYZE SELECT * FROM test WHERE name = 'valor500000';"

graph_title = 'Tempos com e sem index Btree'


run_test(stp, stp.create_test_table, stp.create_index_idx_text, stp.drop_index_idx_text, explain_query, graph_title)

# # --------------------- btree END -----------------------------

# # # -------------------------------------------------------------------

# # --------------------- bitmap START -----------------------------
# explain_query = "explain analyze select * from person where gender = 'M';"

# graph_title = 'Tempos com e sem index Bitmap'

# run_test(stp, stp.create_person_table, stp.create_index_idx_gender_bitmap, stp.drop_index_idx_gender_bitmap, explain_query, graph_title)

# # --------------------- bitmap END -----------------------------
# # -------------------------------------------------------------------
# # --------------------- hash START -----------------------------
# explain_query = "explain analyze select * from person where name = 'joao';"

# graph_title = 'Tempos com e sem index  Hash'

# run_test(stp, stp.create_person_table, stp.create_index_idx_name_hash, stp.drop_index_idx_name_hash, explain_query, graph_title)

# # --------------------- hash END -----------------------------

# # -------------------------------------------------------------------
# # --------------------- pg_trgm START -----------------------------
# explain_query = "EXPLAIN ANALYZE select * from test where name LIKE 'eQi%';"

# graph_title = 'Tempos com e sem index  pg_trgm'

# run_test(stp, stp.create_test_table, stp.create_index_idx_text_trgm, stp.drop_index_idx_text_trgm, explain_query, graph_title)

# # --------------------- pg_trgm END -----------------------------