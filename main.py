import os
from global_logger import Log
from src.resolver import *

glob_log = Log.get_logger(name="main", logs_dir=os.path.abspath("./log"))

def main():
    resolver_app = Resolver()
    resolver_app.main_loop()

if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        glob_log.exception("Unhandeled error caught!")