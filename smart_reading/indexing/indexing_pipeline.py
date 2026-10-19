from config.setting import QaConfig


class IndexingPipline:
    def __init__(self):
        self.__config = QaConfig()
        from indexing.hash_calculate import HashCalculator
        self.__file_hash = HashCalculator()