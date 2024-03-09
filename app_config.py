from dataclasses import dataclass
from configparser import ConfigParser


@dataclass
class ParseSections:
    sections: dict

    def __post_init__(self):
        for section_key, section_value in self.sections.items():
            setattr(self, section_key, ParseSectionContent(section_value.items()))


@dataclass
class ParseSectionContent:
    section_content: dict

    def __post_init__(self):
        for content_key, content_value in self.section_content:
            setattr(self, content_key, content_value)


class Config(ParseSections):
    def __init__(self, config_file):
        config_data = ConfigParser()
        config_data.read(config_file)

        self.config = ParseSections(config_data)
        # ParseSections.__init__(self, config_data)

        self.get_config()

    def get_config(self):
        return self.config


_config = Config("config.ini")
config = _config.get_config()

print(config.generic.debug, config.csl.csl_path)
