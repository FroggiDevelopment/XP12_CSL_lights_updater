from configparser import ConfigParser
from config import DynamicConfigIni

parser = ConfigParser()
parser.read_file(open("config.ini"))
config = DynamicConfigIni(parser)

print(config.generic.debug, config.CSL.csl_path)
