
from documentLoad import *
loads_txt()
spliter = recursive_spliter(loads_txt())

from embed_and_storage import embed

print(embed(spliter))