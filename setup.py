import psycopg2

class Setup:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    def connect(self):
        self.connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )

    def execute_query(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()

    def analyze_table(self, table_name):
        analyze_query = f"ANALYZE {table_name};"
        self.execute_query(analyze_query)

    def table_exists(self, table_name):
        check_table_query = f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}');"
        cursor = self.connection.cursor()
        cursor.execute(check_table_query)
        result = cursor.fetchone()[0]
        return result

    def table_count_greater_equal(self, table_name, count):
        check_count_query = f"SELECT COUNT(*) FROM {table_name};"
        cursor = self.connection.cursor()
        cursor.execute(check_count_query)
        result = cursor.fetchone()[0]
        return result >= count

    def create_text_function(self):
        text_function = """
            CREATE OR REPLACE FUNCTION text(size integer) RETURNS text AS
            $$
            DECLARE
                chars text[] := '{0,1,2,3,4,5,6,7,8,9,A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z}';
                result text := '';
                i integer := 0;
            BEGIN
                IF size < 0 THEN
                    RAISE EXCEPTION 'Tamanho dado não pode ser menor que zero';
                END IF;
                FOR i IN 1..size LOOP
                    result := result || chars[1 + random() * (array_length(chars, 1) - 1)];
                END LOOP;
                RETURN result;
            END;
            $$ LANGUAGE plpgsql;
        """
        self.execute_query(text_function)

    def create_test_table(self, size):
        if not self.table_exists("test"):
            create_table_test = f"""
                CREATE TABLE test(name varchar);
                DO $$
                BEGIN
                    FOR i IN 1..{size} LOOP
                        INSERT INTO test VALUES (text(10));
                    END LOOP;
                END;
                $$ LANGUAGE plpgsql;
            """
            self.execute_query(create_table_test)
        
        self.analyze_table("test")

    def create_index_idx_text(self):
        if not self.table_exists("test"):
            raise Exception("A tabela test não existe.")

        create_index = """
            CREATE INDEX idx_text ON test(name);
        """
        self.execute_query(create_index)
        self.analyze_table("test")

    def drop_index_idx_text(self):
        if not self.table_exists("test"):
            raise Exception("A tabela test não existe.")

        drop_index = """
            DROP INDEX IF EXISTS idx_text;
        """
        self.execute_query(drop_index)
        self.analyze_table("test")

    def create_index_idx_text_trgm(self):
        if not self.table_exists("test"):
            raise Exception("A tabela test não existe.")

        create_extension = """
            CREATE EXTENSION IF NOT EXISTS pg_trgm;
        """
        create_index = """
            CREATE INDEX idx_text_trgm ON test USING GIN(name gin_trgm_ops);
        """
        self.execute_query(create_extension)
        self.execute_query(create_index)
        self.analyze_table("test")

    def drop_index_idx_text_trgm(self):
        if not self.table_exists("test"):
            raise Exception("A tabela test não existe.")

        drop_index = """
            DROP INDEX IF EXISTS idx_text_trgm;
        """
        self.execute_query(drop_index)

    def create_person_table(self, size):
        if not self.table_exists("person"):
            create_table_person = f"""
                CREATE TABLE person (
                    id serial PRIMARY KEY,
                    name varchar,
                    gender varchar(1) CHECK (gender IN ('M','F'))
                );
                DO $$
                BEGIN
                    FOR i IN 1..{size} LOOP
                        INSERT INTO person(name, gender) VALUES (text(10), 'M');
                    END LOOP;
                    FOR i IN 1..{size} LOOP
                        INSERT INTO person(name, gender) VALUES (text(10), 'F');
                    END LOOP;
                END;
                $$ LANGUAGE plpgsql;
            """
            self.execute_query(create_table_person)
       
        self.analyze_table("person")

    def create_index_idx_gender_bitmap(self):
        if not self.table_exists("person"):
            raise Exception("A tabela person não existe.")

        create_extension = """
            CREATE EXTENSION IF NOT EXISTS btree_gin;
        """
        create_index = """
            CREATE INDEX idx_gender_bitmap ON person USING gin (gender);
        """
        self.execute_query(create_extension)
        self.execute_query(create_index)
        self.analyze_table("person")

    def drop_index_idx_gender_bitmap(self):
        if not self.table_exists("person"):
            raise Exception("A tabela person não existe.")

        drop_index = """
            DROP INDEX IF EXISTS idx_gender_bitmap;
        """
        self.execute_query(drop_index)

    def create_index_idx_name_btree(self):
        if not self.table_exists("person"):
            raise Exception("A tabela person não existe.")

        create_index = """
            CREATE INDEX idx_name_btree ON person USING btree (name);
        """
        self.execute_query(create_index)
        self.analyze_table("person")

    def drop_index_idx_name_btree(self):
        if not self.table_exists("person"):
            raise Exception("A tabela person não existe.")

        drop_index = """
            DROP INDEX IF EXISTS idx_name_btree;
        """
        self.execute_query(drop_index)

    def create_index_idx_name_hash(self):
        if not self.table_exists("person"):
            raise Exception("A tabela person não existe.")

        create_index = """
            CREATE INDEX idx_name_hash ON person USING hash (name);
        """
        self.execute_query(create_index)
        self.analyze_table("person")

    def drop_index_idx_name_hash(self):
        if not self.table_exists("person"):
            raise Exception("A tabela person não existe.")

        drop_index = """
            DROP INDEX IF EXISTS idx_name_hash;
        """
        self.execute_query(drop_index)

    def create_students_table(self, size):
        if not self.table_exists("students"):
            create_table_students = """ 
                CREATE TABLE students (info jsonb);
                DO $$
                    DECLARE vartype varchar[] := '{"quiz", "exam", "homework"}';
                    BEGIN
                        FOR i IN 1..333333 LOOP
                            FOR j IN 1..3 LOOP
                                INSERT INTO students (info) VALUES (
                                    jsonb_build_object(
                                        'student', i,
                                        'type', vartype[j],
                                        'score', round(random() * 100)
                                    )
                                );
                            END LOOP;
                        END LOOP;
                    END;
                $$ LANGUAGE plpgsql; """
            
            self.execute_query(create_table_students)
        # elif not self.table_count_greater_equal("students", 3*size):
        #     raise Exception("A tabela students já existe, mas não possui o número mínimo de registros.")

        self.analyze_table("students")

    def create_index_idx_type(self):
        if not self.table_exists("students"):
            raise Exception("A tabela students não existe.")

        create_index = """
            CREATE INDEX idx_type ON students USING btree ((info->>'type'));
        """
        self.execute_query(create_index)
        self.analyze_table("students")

    def drop_index_idx_type(self):
        if not self.table_exists("students"):
            raise Exception("A tabela students não existe.")

        drop_index = """
            DROP INDEX IF EXISTS idx_type;
        """
        self.execute_query(drop_index)
        self.analyze_table("students")

    def create_index_idx_json(self):
        if not self.table_exists("students"):
            raise Exception("A tabela students não existe.")

        create_index = """
            CREATE INDEX idx_json ON students USING GIN (info);
        """
        self.execute_query(create_index)
        self.analyze_table("students")

    def drop_index_idx_json(self):
        if not self.table_exists("students"):
            raise Exception("A tabela students não existe.")

        drop_index = """
            DROP INDEX IF EXISTS idx_json;
        """
        self.execute_query(drop_index)
        self.analyze_table("students")
        
    def drop_table(self, table_name):
        drop_table_query = f"DROP TABLE IF EXISTS {table_name};"
        self.execute_query(drop_table_query)

    def close_connection(self):
        self.connection.close()
