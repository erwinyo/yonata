# Built-in imports
import uuid
from datetime import datetime

# Third-party imports
from psycopg2.extras import Json
from .config import logger, _postgres_connection, _postgres_cursor

# Local imports


def __query_to_postgres(query: str, values=None) -> None:
    logger.trace(f"Query: {query}")
    logger.trace(f"Query values: {values}")

    if values is None:
        _postgres_cursor.execute(query)
    else:
        _postgres_cursor.execute(query, values)

    return _postgres_cursor


def _check_postgres_connection() -> bool:
    try:
        __query_to_postgres("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"PostgreSQL connection error: {e}")
        return False


def _is_table_exist(table_name: str) -> bool:
    query = f"""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = '{table_name}'
        );
    """
    _postgres_cursor = __query_to_postgres(query)
    is_exist = bool(_postgres_cursor.fetchone()[0])

    logger.trace(f"Table {table_name} exists: {is_exist}")
    return is_exist


def _get_table_columns(table_name: str) -> list:
    query = f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position;  
    """
    _postgres_cursor = __query_to_postgres(query)
    results = _postgres_cursor.fetchall()
    logger.trace(f"Query results: {results}")

    return [row[0] for row in results]


def _get_table_data(
    table_name: str, condition: dict = None, use_or: bool = False
) -> list:
    if condition:
        connector = " OR " if use_or else " AND "
        where_clauses = []
        values = []
        for key, value in condition.items():
            if isinstance(value, list):
                placeholders = ", ".join(["%s"] * len(value))
                where_clauses.append(f"{key} IN ({placeholders})")
                values.extend(
                    [Json(v) if isinstance(v, (dict, list)) else v for v in value]
                )
            else:
                where_clauses.append(f"{key} = %s")
                values.append(Json(value) if isinstance(value, (dict, list)) else value)
        where_clause = connector.join(where_clauses)
        query = f"SELECT * FROM {table_name} WHERE {where_clause};"
        _postgres_cursor = __query_to_postgres(query, values)
    else:
        query = f"SELECT * FROM {table_name};"
        _postgres_cursor = __query_to_postgres(query)
    results = _postgres_cursor.fetchall()
    logger.trace(f"Query results: {results}")

    columns = _get_table_columns(table_name)
    data = [dict(zip(columns, row)) for row in results]

    return data


def _insert_to_postgres(table_name: str, data: dict) -> None:
    # Extract columns and values
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    values = [
        Json(value) if isinstance(value, (dict, list)) else value
        for value in data.values()
    ]

    # Construct parameterized query
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    _postgres_cursor = __query_to_postgres(query, values)
    _postgres_connection.commit()

    logger.info(f"Data inserted into {table_name} successfully.")


def _update_to_postgres(
    table_name: str, data: dict, condition: dict, use_or: bool = False
) -> None:
    # Extract columns and values for SET clause
    set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
    set_values = [
        Json(value) if isinstance(value, dict) else value for value in data.values()
    ]

    # Extract columns and values for WHERE clause
    connector = " OR " if use_or else " AND "
    where_clauses = []
    where_values = []
    for key, value in condition.items():
        if isinstance(value, list):
            placeholders = ", ".join(["%s"] * len(value))
            where_clauses.append(f"{key} IN ({placeholders})")
            where_values.extend([Json(v) if isinstance(v, dict) else v for v in value])
        else:
            where_clauses.append(f"{key} = %s")
            where_values.append(Json(value) if isinstance(value, dict) else value)
    where_clause = connector.join(where_clauses)

    # Combine values for parameterized query
    values = set_values + where_values

    # Construct parameterized query
    query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"

    _postgres_cursor = __query_to_postgres(query, values)
    _postgres_connection.commit()

    logger.info(f"Data updated in {table_name} successfully.")


def _is_data_exist(table_name: str, condition: dict, use_or: bool = False) -> bool:
    connector = " OR " if use_or else " AND "
    where_clauses = []
    values = []
    for key, value in condition.items():
        if isinstance(value, list):
            placeholders = ", ".join(["%s"] * len(value))
            where_clauses.append(f"{key} IN ({placeholders})")
            values.extend(
                [Json(v) if isinstance(v, (dict, list)) else v for v in value]
            )
        else:
            where_clauses.append(f"{key} = %s")
            values.append(Json(value) if isinstance(value, (dict, list)) else value)
    where_clause = connector.join(where_clauses)
    query = f"""
        SELECT EXISTS (
            SELECT 1
            FROM {table_name}
            WHERE {where_clause}
        );
    """
    _postgres_cursor = __query_to_postgres(query, values)
    is_exist = bool(_postgres_cursor.fetchone()[0])

    logger.trace(f"Data exists in {table_name}: {is_exist}")
    return is_exist
