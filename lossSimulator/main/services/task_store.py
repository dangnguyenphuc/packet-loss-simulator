from multiprocessing import Manager

_manager = Manager()
myCache = _manager.dict()
tasks = _manager.dict()
