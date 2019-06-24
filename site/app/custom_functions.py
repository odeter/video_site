import hashlib

def calc_file_hash(file_name):
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    buf = file_name.read(BLOCKSIZE)
    while len(buf) > 0:
        hasher.update(buf)
        buf = file_name.read(BLOCKSIZE)
    return hasher.hexdigest()

def calc_string_hash(in_string):
    bys = str.encode(in_string)
    hash_object = hashlib.sha256(bys)
    return hash_object.hexdigest()
