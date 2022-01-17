from global_logger import Log
import os

glob_log = Log.get_logger(name="main", logs_dir=os.path.abspath("./log"))

def main():
    pass

if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        glob_log.exception("Unhandeled error caught!")