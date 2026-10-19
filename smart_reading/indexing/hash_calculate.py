import hashlib

class HashCalculator:
    """根据文件计算哈希值"""
    def compute_hash(self, pdf_bytes : bytes) -> str:
        return hashlib.md5(pdf_bytes).hexdigest()

    def compute_hash_from_file(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()