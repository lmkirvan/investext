def query_create_table(sql_query, table_name, is_temporary=False):
    """
    Wraps a SELECT statement into a CREATE TABLE AS (CTAS) statement.
    
    Args:
        sql_query (str): The original SELECT statement.
        table_name (str): The name of the table to be created.
        is_temporary (bool): If True, creates a TEMPORARY table.
        
    Returns:
        str: The complete CREATE TABLE SQL statement.
    """
    # Clean up the query to ensure no trailing semicolons interfere 
    # with the wrapping parenthesis
    clean_query = sql_query.strip().rstrip(';')
    
    table_type = "TEMP " if is_temporary else ""
    
    create_statement = (
        f"CREATE {table_type}TABLE {table_name} AS (\n"
        f"{clean_query}\n"
        f");"
    )
    
    return create_statement

def insert_query_into(sql_query, table_name, columns=None):
    """
    Wraps a SELECT statement into an INSERT INTO statement.
    
    Args:
        sql_query (str): The SELECT statement providing the data.
        table_name (str): The existing table to receive the data.
        columns (list, optional): A list of column names in the target table.
        
    Returns:
        str: The complete INSERT INTO SQL statement.
    """


    # Remove trailing semicolons from the inner query
    clean_query = sql_query.strip().rstrip(';')
    
    # Format columns if provided (e.g., "(col1, col2, col3)")
    column_str = ""
    if columns:
        column_str = f" ({', '.join(columns)})"
    
    insert_statement = (
        f"INSERT INTO {table_name}{column_str}\n"
        f"{clean_query};"
    )
    
    return insert_statement


def add_column_float(sql_query, table_name, colname):
    """
    Wraps a SELECT statement into an INSERT INTO statement.
    
    Args:
        sql_query (str): The SELECT statement providing the data.
        table_name (str): The existing table to receive the data.
        columns (list, optional): A list of column names in the target table.
        
    Returns:
        str: The complete INSERT INTO SQL statement.
    """
    # Remove trailing semicolons from the inner query
    clean_query = sql_query.strip().rstrip(';')
    # Format columns if provided (e.g., "(col1, col2, col3)")
    alter_statement  = (
        f"ALTER TABLE {table_name} ADD {colname} FLOAT;\n"
        f"INSERT INTO {table_name} BY NAME ("
        f"{clean_query} AS {colname});"
    )
    
    return alter_statement
