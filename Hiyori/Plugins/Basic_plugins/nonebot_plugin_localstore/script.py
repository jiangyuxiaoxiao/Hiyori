from typing import Callable
from argparse import ArgumentParser

from .utils import remove_dir, show_dir_detail
from . import BASE_DATA_DIR, BASE_CACHE_DIR, BASE_CONFIG_DIR

parser = ArgumentParser("nb localstore")


# main function
def show_dir():
    print("Cache Dir: ", BASE_CACHE_DIR)
    print("Config Dir: ", BASE_CONFIG_DIR)
    print("Data Dir: ", BASE_DATA_DIR)


parser.set_defaults(func=show_dir)

# sub parsers
subparsers = parser.add_subparsers(title="command")

# cache parser
cache = subparsers.add_parser("cache", help="cache directory")
cache_subparsers = cache.add_subparsers(title="subcommand")


def show_cache():
    show_dir_detail(BASE_CACHE_DIR)


cache.set_defaults(func=show_cache)

cache_clear = cache_subparsers.add_parser("clear", help="clear cache")


def clear_cache():
    remove_dir(BASE_CACHE_DIR)


cache_clear.set_defaults(func=clear_cache)


# config parser
config = subparsers.add_parser("config", help="config directory")
config_subparsers = config.add_subparsers(title="subcommand")


def show_config():
    show_dir_detail(BASE_CONFIG_DIR)


config.set_defaults(func=show_config)

config_clear = config_subparsers.add_parser("clear", help="clear config")


def clear_config():
    remove_dir(BASE_CONFIG_DIR)


config_clear.set_defaults(func=clear_config)


# data parser
data = subparsers.add_parser("data", help="data directory")
data_subparsers = data.add_subparsers(title="subcommand")


def show_data():
    show_dir_detail(BASE_DATA_DIR)


data.set_defaults(func=show_data)

data_clear = data_subparsers.add_parser("clear", help="clear data")


def clear_data():
    remove_dir(BASE_DATA_DIR)


data_clear.set_defaults(func=clear_data)


def main():
    result = parser.parse_args()
    result = vars(result)
    prompt: Callable[..., None] = result.pop("func")
    prompt(**result)


if __name__ == "__main__":
    main()
