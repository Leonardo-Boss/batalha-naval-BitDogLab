block_lib = False

def block():
    global block_lib
    block_lib = True

def unblock():
    global block_lib
    block_lib = False

def blocked():
    while block_lib:
        pass
    return
