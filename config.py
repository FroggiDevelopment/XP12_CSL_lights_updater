import configparser


class DynamicConfig:
    def __init__(self, conf):
        if not isinstance(conf, dict):
            raise TypeError(f"dict expected, found {type(conf).__name__}")

        self._raw = conf
        for key, value in self._raw.items():
            setattr(self, key, value)


class DynamicConfigIni:
    def __init__(self, conf):
        if not isinstance(conf, configparser.ConfigParser):
            raise TypeError(f"ConfigParser expected, found {type(conf).__name__}")

        self._raw = conf
        for key, value in self._raw.items():
            setattr(self, key, DynamicConfig(dict(value.items())))


parser = configparser.ConfigParser()
parser.read_file(open("config.ini"))
config = DynamicConfigIni(parser)
print(config.generic.debug, config.CSL.csl_path)
# print("CSL", config.CLS.csl_path)
