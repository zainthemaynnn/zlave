# default
import sqlite3
import os
from functools import wraps

# external
import yaml

# self-made
from tools import logger_tools

# logger
logger = logger_tools.standard_logger("INFO")

# intitialization
with open("config\\controls.yml") as controls_file:
    data_controls = yaml.safe_load(controls_file)["data"]


# functions
def query_params(length):
    """
    hacky way to create a dynamic number of parameters in an sql query"
    """

    params = "("
    for i in range(length - 1):
        params += "?, "
    else:
        params += "?)"
    return params


# decorators
def query(func):
    """
    just to make sure the database is ok before each query
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            db = "{0}\\{1}".format(
                os.environ["PYTHONPATH"], data_controls["database"])
            conn = sqlite3.connect(db)
            logger.debug(f"successfully opened database {db}")
        except Exception as e:
            logger.error(f"database machine broke at {db}; {e}")
            conn = None

        if conn:
            return func(*args, conn, **kwargs)
        else:
            logger.error(
                f"could not perform query \"{func.__name__}\" attempted on {db}; connection issue")
            return None
    return wrapper


# simple queries
@query
def setup(entry, table, conn):
    """
    configures an entry based on default_prefs.json. so you can setup without db_insert :)
    """

    logger.info(
        f"received setup request for instance \"{entry}\"")
    with open("config\\default_prefs.yml") as default_preferences:
        defprefs = yaml.safe_load(default_preferences)

    if (pref_table := defprefs.get(table)) is None:
        return

    def_entries = [entry]
    for preset in pref_table:
        def_entries.append(pref_table[preset]["default"])

    conn.execute("INSERT INTO {0} VALUES{1}".format(
        table, query_params(len(def_entries))), def_entries)
    conn.commit()
    conn.close()
    logger.debug(
        f"row set up in {table} for entry {entry}")


@query
def db_get(entry, table, column, conn, querytype="single"):
    """
    gets one or all values. does an emergency setup if the value wasn't found.
    """

    def get_data():
        cursor = conn.cursor()
        cursor.execute("SELECT {1} FROM {0} WHERE {2} = ?".format(
            table, column, entry[0]), (entry[1],))

        if querytype == "single":
            data = cursor.fetchone()[0]
        elif querytype == "all":
            data = cursor.fetchall()
        else:
            raise ValueError(
                f"unexpected value {querytype} for argument \"querytype\"")

        cursor.close()
        return data

    try:
        data = get_data()
        logger.debug(
            f"fetched column \"{column}\" for entry {entry} on \"{table}\"")

    except TypeError:
        logger.warning(
            f"no column \"{column}\" for entry {entry} found on \"{table}\". attempting recovery...")
        setup(entry[1], table)
        data = get_data()

    conn.close()
    return data


@query
def db_remove(entry, table, conn):
    """
    deletes an entry
    """

    conn.execute("DELETE FROM {0} WHERE {1} = ?".format(table, entry[0]), (entry[1],))
    conn.commit()
    conn.close()
    logger.debug(
        f"row deleted in {table} for entry {entry}")
