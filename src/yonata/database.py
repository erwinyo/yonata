# Built-in imports
import os
import json
import uuid
from datetime import datetime
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Sequence

# Third-party imports
from psycopg2.extras import Json
from yonata.config import logger


# Local imports


__postgres_connection = None
__postgres_cursor = None


def set_client_database(postgres_connection, postgres_cursor):
    global __postgres_connection, __postgres_cursor
    __postgres_connection = postgres_connection
    __postgres_cursor = postgres_cursor


def __query_to_postgres(query: str, values=None) -> None:
    logger.trace(f"Query: {query}")
    logger.trace(f"Query values: {values}")

    if values is None:
        __postgres_cursor.execute(query)
    else:
        __postgres_cursor.execute(query, values)

    return __postgres_cursor


def __build_where_clause(
    condition: Dict[str, Any], use_or: bool
) -> tuple[str, List[Any]]:

    # Build WHERE clause based on the condition dictionary
    connector = " OR " if use_or else " AND "
    clauses: List[str] = []
    values: List[Any] = []

    for col, val in condition.items():
        if isinstance(val, list):
            placeholders = ", ".join(["%s"] * len(val))
            clauses.append(f"{col} IN ({placeholders})")
            values.extend([Json(v) if isinstance(v, (dict, list)) else v for v in val])
        else:
            clauses.append(f"{col} = %s")
            values.append(Json(val) if isinstance(val, (dict, list)) else val)

    where_clause = connector.join(clauses)
    return where_clause, values


def _check_postgres_connection() -> bool:
    try:
        __query_to_postgres("SELECT 1")
        logger.success("PostgreSQL connection is successful.")
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
    __postgres_cursor = __query_to_postgres(query)
    is_exist = bool(__postgres_cursor.fetchone()[0])

    logger.trace(f"Table {table_name} exists: {is_exist}")
    return is_exist


def _get_table_columns(table_name: str) -> list:
    query = f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position;  
    """
    __postgres_cursor = __query_to_postgres(query)
    results = __postgres_cursor.fetchall()
    logger.trace(f"Query results: {results}")

    return [row[0] for row in results]


def _get_table_data(
    table_name: str, condition: dict = None, use_or: bool = False
) -> list:
    if condition:
        # Choose connector based on use_or flag
        where_clause, values = __build_where_clause(condition, use_or)

        # Build query with WHERE clause
        query = f"SELECT * FROM {table_name} WHERE {where_clause};"
        __postgres_cursor = __query_to_postgres(query, values)
    else:
        # No condition, select all rows
        query = f"SELECT * FROM {table_name};"
        __postgres_cursor = __query_to_postgres(query)
    # Fetch all results
    results = __postgres_cursor.fetchall()
    logger.trace(f"Query results: {results}")

    # Get column names for the table
    columns = _get_table_columns(table_name)
    # Convert each row to a dict mapping column names to values + datetime format to string format
    data = [
        {
            key: (value.isoformat() if isinstance(value, datetime) else value)
            for key, value in zip(columns, row)
        }
        for row in results
    ]
    return data


def _insert_to_postgres(table_name: str, data: dict) -> None:
    # Extract columns and values
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    values = []
    for value in data.values():
        # If value is a dict or list, wrap with Json for PostgreSQL JSON/JSONB columns
        if isinstance(value, (dict, list)):
            values.append(Json(value))
        # If value is a string that looks like JSON, try to parse and wrap with Json
        elif isinstance(value, str):
            try:
                parsed = json.loads(value)
                values.append(Json(parsed))
            except (ValueError, TypeError):
                values.append(value)
        else:
            values.append(value)

    # Construct parameterized query
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    __postgres_cursor = __query_to_postgres(query, values)
    __postgres_connection.commit()

    logger.success(f"Data inserted into {table_name} successfully.")


def _update_to_postgres(
    table_name: str, data: dict, condition: dict, use_or: bool = False
) -> None:
    # Extract columns and values for SET clause
    set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
    set_values = [
        Json(value) if isinstance(value, dict) else value for value in data.values()
    ]

    where_clause, where_values = __build_where_clause(condition, use_or)
    # Combine values for parameterized query
    values = set_values + where_values

    # Construct parameterized query
    query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"

    __postgres_cursor = __query_to_postgres(query, values)
    __postgres_connection.commit()

    logger.success(f"Data updated in {table_name} successfully.")


def _is_data_exist(table_name: str, condition: dict, use_or: bool = False) -> bool:
    # Choose connector based on use_or flag
    where_clause, values = __build_where_clause(condition, use_or)
    # Build query with WHERE clause
    query = f"""
        SELECT EXISTS (
            SELECT 1
            FROM {table_name}
            WHERE {where_clause}
        );
    """
    # Execute query with values
    __postgres_cursor = __query_to_postgres(query, values)
    # Fetch result and convert to boolean
    is_exist = bool(__postgres_cursor.fetchone()[0])

    logger.info(f"Data exists in {table_name}: {is_exist}")
    return is_exist
