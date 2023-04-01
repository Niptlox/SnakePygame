import os
from configparser import ConfigParser
from typing import Any


def config_save():
    with open(config_filename, 'w') as configfile:
        config.write(configfile)


config_filename = os.getcwd() + r'/settings.ini'
print("config_filename", config_filename)
# with open(config_filename, "r") as f:
#     print(f.read())
config = ConfigParser()
config.read(config_filename)


class __Settings:
    config = config
    section = ""
    variables = {}

    def __init__(self):
        self.load_vars()

    @classmethod
    def set(cls, var_name, var_value):
        # print(cls.section, var_name, var_value)
        config.set(cls.section, var_name, str(var_value))
        config_save()
        if var_name in cls.__dict__:
            if isinstance(var_value, str):
                var_value = '"' + var_value + '"'
            exec(f"cls.{var_name} = {var_value}")
        print(cls.__dict__[var_name])

    @classmethod
    def get(cls, var_name, var_type=str, list_sep=",", format_str=True):
        if var_type is str:
            if format_str:
                return "'" + config.get(cls.section, var_name) + "'"
            return config.get(cls.section, var_name)
        if var_type is bool:
            return config.getboolean(cls.section, var_name)
        if var_type is int:
            return config.getint(cls.section, var_name)
        if var_type is float:
            return config.getfloat(cls.section, var_name)
        if var_type is list:
            return config.get(cls.section, var_name).split(list_sep)
        raise Exception(f"Get that is type? {var_type}")

    @classmethod
    def load_vars_from_variables(cls):
        for var_name, var_type in cls.variables.items():
            exec(f"cls.{var_name} = {cls.get(var_name, var_type)}", locals(), globals())

    @classmethod
    def load_vars(cls):
        for var_name, var_cls in cls.__dict__.items():
            if isinstance(var_cls, ConfigVar) or var_cls in [ConfigVar]:
                exec(f"cls.{var_name} = {cls.get(var_name, var_cls.var_type)}", locals(), globals())


class ConfigVar:
    var_type = str

    def __init__(self, var_type: Any = str, default=None):
        self.var_type = var_type
        self.default = default


class WindowCnf(__Settings):
    section = "Window"
    WindowSize = ConfigVar(list)
    FPS = ConfigVar(int)


class GameCnf(__Settings):
    section = "Game"
    DEBUG = ConfigVar(bool)
    Online = ConfigVar(bool)
    ServerIsLocal = ConfigVar(bool)
    ServerLocal = ConfigVar(str)
    ServerGlobal = ConfigVar(str)
    PORT = ConfigVar(int)
    Flags = ConfigVar(str)
    SmoothCamera = ConfigVar(bool)


class ServerCnf(__Settings):
    section = "Server"
    HOST = ConfigVar(str)
    PORT = ConfigVar(int)
    DEBUG = ConfigVar(bool)


WindowCnf.load_vars()
GameCnf.load_vars()
ServerCnf.load_vars()
