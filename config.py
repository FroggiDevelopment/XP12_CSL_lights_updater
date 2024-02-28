from configparser import ConfigParser


class Config:
    def __init__(self, config_file: str) -> None:
        self.config_file = config_file
        self.config = self.get_config()

    def get_config(self) -> ConfigParser:
        _config = {}
        config_object = ConfigParser()
        config_object.read(self.config_file)

        return config_object


if __name__ == "__main__":
    config = Config("./config.ini").get_config()
    print(config["generic"]["backup"])
