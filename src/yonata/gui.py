# Built-in imports
import os

# Third-party imports
from nicegui import ui

# Local imports
from yonata.utils import _list_to_string
from yonata.database import _get_table_columns, _get_table_data


def _run_gui():
    """Run the NiceGUI application."""

    @ui.page("/")
    def index():
        ui.label("Welcome to Yet One Neat!")

    @ui.page("/benchmark")
    def benchmark():
        ui.label("Benchmark Results")

        columns = _get_table_columns(table_name="task")
        ready_columns = []
        for column in columns:
            label = "".join(e for e in column if e.isalnum()).capitalize()
            if column == "task_id":
                ready_columns.append(
                    {
                        "name": column,
                        "label": label,
                        "field": column,
                        "required": True,
                        "align": "left",
                        "sortable": False,
                    }
                )
            else:
                ready_columns.append(
                    {
                        "name": column,
                        "label": label,
                        "field": column,
                        "required": False,
                        "align": "left",
                        "sortable": False,
                    }
                )
        print(ready_columns)

        rows = _get_table_data(table_name="task")
        ready_rows = []
        for row in rows:
            ready_row = {}
            for column in columns:
                if isinstance(row[column], list):
                    row[column] = _list_to_string(row[column])
                ready_row[column] = row[column]
            ready_rows.append(ready_row)
        ui.table(columns=ready_columns, rows=rows, row_key="task_id")

        # columns = [
        #     {
        #         "name": "name",
        #         "label": "Name",
        #         "field": "name",
        #         "required": True,
        #         "align": "left",
        #     },
        #     {"name": "age", "label": "Age", "field": "age", "sortable": True},
        # ]
        # rows = [
        #     {"name": "Alice", "age": 18},
        #     {"name": "Bob", "age": 21},
        #     {"name": "Carol"},
        # ]
        # ui.table(columns=columns, rows=rows, row_key="name")

    ui.run(title="Yet One Neat", port=8080, reload=False)
