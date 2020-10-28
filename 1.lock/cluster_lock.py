import redlock

if __name__ == '__main__':
    addrs = [{
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": "739e9ec7-efd7-4e21-b68b-c4a3807b448b"
    }, {
        "host": "localhost",
        "port": 6479,
        "db": 0
    }, {
        "host": "localhost",
        "port": 6579,
        "db": 0
    }]
    dlm = redlock.RedLock(resource="hello", connection_details=addrs)
    success = dlm.acquire()
    if success:
        print('lock success')
        dlm.release()
    else:
        print('lock failed')
