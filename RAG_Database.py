import psycopg2
from typing import List, Dict
import json
import requests
import pandas as pd


class AcademicRAG:
    def __init__(self,
                 db_name: str = "university_db",
                 db_user: str = "postgres",
                 db_password: str = "superuser",
                 db_host: str = "localhost",
                 db_port: str = "5432",
                 ollama_url: str = "http://localhost:11434",
                 schema_files: Dict[str, str] = None):
        self.db_config = {
            "dbname": db_name,
            "user": db_user,
            "password": db_password,
            "host": db_host,
            "port": db_port
        }
        self.ollama_url = ollama_url
        self.conversation_history = []  # Added for multi-turn conversation support
        self.schema_files = schema_files
        self.schema_info = self._get_schema_info()  # Store schema info to avoid repeated reading

    def _get_schema_info(self) -> str:
        """Fetch schema info from the provided CSV files to generate a structured schema description."""
        schema = {}

        # Load each CSV to get column details
        if self.schema_files:
            for table_name, file_path in self.schema_files.items():
                df = pd.read_csv(file_path)
                columns = df.columns.tolist()
                schema[table_name] = columns

        # Generate schema information as a descriptive string
        schema_text = "Tables and columns in the database:\n"
        for table, columns in schema.items():
            schema_text += f"- {table}: {', '.join(columns)}\n"

        return schema_text

    def connect_db(self):
        try:
            return psycopg2.connect(**self.db_config)
        except psycopg2.OperationalError as e:
            print(f"Connection error: {e}")
            raise

    def query_database(self, query: str) -> List[Dict]:
        """Execute a query and return results as a list of dictionaries."""
        try:
            with self.connect_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    columns = [desc[0] for desc in cur.description]
                    results = [dict(zip(columns, row)) for row in cur.fetchall()]
                    return results
        except psycopg2.Error as e:
            error_message = f"Database error: {e.pgerror if hasattr(e, 'pgerror') else str(e)}"
            print(error_message)
            return [{"error": error_message}]
        except Exception as e:
            error_message = f"Unexpected error while querying the database: {str(e)}"
            print(error_message)
            return [{"error": error_message}]

    def validate_sql(self, query: str) -> bool:
        """Validate generated SQL to avoid dangerous commands."""
        dangerous_keywords = ["drop", "delete", "truncate", "alter"]
        # Check each line for dangerous keywords
        lines = query.lower().splitlines()
        return not any(keyword in line for line in lines for keyword in dangerous_keywords)

    def generate_sql(self, user_query: str, model: str = "llama2") -> str:
        """
        Generate a SQL query using a Llama model based on the user's question.
        Returns only the SQL query as a string.
        """
        prompt = f"""You are an expert SQL database query generator. Given the database schema and relationships below, generate an accurate SQL query for the given user question.

        Database Schema:
        {self.schema_info}

        Relationships:
        - `students` table has `student_id` which links to `student_courses` via `student_id`.
        - `instructor_courses` links instructors and courses via `instructor_id` and `course_number`.
        - `teachers` table has `instructor_id` linking to `instructor_courses`.
        - `departments` links to `teachers`, `staff`, and `advisors` using `department_id`.
        - `departments` table contains information about departments, with `department_id` linking to other tables.

        Important Instructions:
        - If the user query mentions "student", "courses a student has", or anything related to a student, use the `student_courses` table.
        - If the user query mentions "instructor", "teacher", or anything related to courses taught by an instructor, use the `instructor_courses` table.
        - Always be consistent in interpreting identifiers such as `T` or `U`:
            - Identifiers starting with `T` refer to instructors and link to the `instructor_courses` table.
            - Identifiers starting with `U` refer to students and link to the `student_courses` table.

        Example Questions and Corresponding SQL Queries:
        - "What courses does student U1 have?"
          - Example SQL: `SELECT sc.course_prefix, sc.course_number, sc.semester, sc.year_taken FROM student_courses sc WHERE sc.student_id = 'U1';`
        - "How many students are in each major?"
          - Example SQL: `SELECT major, COUNT(*) AS num_students FROM students GROUP BY major;`
        - "What courses does instructor T3 teach?"
          - Example SQL: `SELECT ic.course_prefix, ic.course_number, ic.semester, ic.year_taught FROM instructor_courses ic WHERE ic.instructor_id = 'T3';`

        Now, generate an accurate SQL query for the following user question:
        {user_query}

        Return **only** the SQL query, without any explanation.
        """
        try:
            # Send the prompt to the Llama model
            print(f"Generating SQL for query: {user_query}")
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()

            # Parse the generated SQL
            generated_sql = response.json().get("response", "").strip()
            if not generated_sql:
                raise ValueError("The model did not return a SQL query.")

            print(f"Generated SQL: {generated_sql}")
            return generated_sql

        except requests.exceptions.RequestException as e:
            error_message = f"Error communicating with the AI model: {str(e)}"
            print(error_message)
            return None

        except ValueError as e:
            error_message = f"SQL generation error: {str(e)}"
            print(error_message)
            return None

        except Exception as e:
            error_message = f"Unexpected error during SQL generation: {str(e)}"
            print(error_message)
            return None

    def process_query(self, user_query: str) -> dict:
        """
        Process a user query, generate SQL, execute it, and return a response.
        """
        try:
            print(f"Processing query: {user_query}")

            # Add user query to conversation history
            self.conversation_history.append({"user_query": user_query})

            # Generate SQL
            generated_sql = self.generate_sql(user_query)
            if not generated_sql:
                return {
                    "success": False,
                    "error": "Failed to generate SQL query.",
                    "sql": None,
                    "data": None,
                    "response": "Could not generate a valid SQL query. Please try rephrasing your question."
                }

            # Validate SQL
            if not self.validate_sql(generated_sql):
                return {
                    "success": False,
                    "error": "Generated SQL query contains potentially dangerous commands.",
                    "sql": generated_sql,
                    "data": None,
                    "response": "Unsafe query detected. Please refine your request."
                }

            # Execute SQL
            results = self.query_database(generated_sql)
            if results and "error" in results[0]:
                return {
                    "success": False,
                    "error": results[0]["error"],
                    "sql": generated_sql,
                    "data": None,
                    "response": results[0]["error"]
                }

            if not results:
                return {
                    "success": False,
                    "error": "No data found.",
                    "sql": generated_sql,
                    "data": None,
                    "response": "No records matched your query. Try rephrasing or using different criteria."
                }

            # Generate natural language response
            prompt = f"""Based on this database query result:
            {json.dumps(results, indent=2)}

            Question: {user_query}

            Provide a clear, concise answer in natural language."""

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama2",
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            ollama_response = response.json().get("response", "").strip()

            self.conversation_history[-1].update({
                "sql": generated_sql,
                "response": ollama_response,
                "data": results
            })

            return {
                "success": True,
                "error": None,
                "sql": generated_sql,
                "data": results,
                "response": ollama_response
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"An unexpected error occurred: {str(e)}",
                "sql": None,
                "data": None,
                "response": "An unexpected issue occurred. Please try again."
            }
