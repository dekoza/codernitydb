import io
import os
import pickle
import struct
from abc import ABCMeta, abstractmethod

from graphility import __version__


class StorageException(Exception):
    pass


class StorageBase(metaclass=ABCMeta):
    @abstractmethod
    def create(self, *args, **kwargs):
        pass

    @abstractmethod
    def open(self, *args, **kwargs):
        pass

    @abstractmethod
    def close(self, *args, **kwargs):
        pass

    @abstractmethod
    def data_from(self, *args, **kwargs):
        pass

    @abstractmethod
    def data_to(self, *args, **kwargs):
        pass

    @abstractmethod
    def save(self, *args, **kwargs):
        return 0, 0

    @abstractmethod
    def insert(self, *args, **kwargs):
        return self.save(*args, **kwargs)

    @abstractmethod
    def update(self, *args, **kwargs):
        return 0, 0

    @abstractmethod
    def get(self, *args, **kwargs):
        return None

    # def compact(self, *args, **kwargs):
    #     pass
    @abstractmethod
    def fsync(self, *args, **kwargs):
        pass

    @abstractmethod
    def flush(self, *args, **kwargs):
        pass


class DummyStorage(StorageBase):
    """
    Storage mostly used to fake real storage
    """

    def create(self, *args, **kwargs):
        pass

    def open(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass

    def data_from(self, *args, **kwargs):
        pass

    def data_to(self, *args, **kwargs):
        pass

    def save(self, *args, **kwargs):
        return 0, 0

    def insert(self, *args, **kwargs):
        return self.save(*args, **kwargs)

    def update(self, *args, **kwargs):
        return 0, 0

    def get(self, *args, **kwargs):
        return None

    # def compact(self, *args, **kwargs):
    #     pass

    def fsync(self, *args, **kwargs):
        pass

    def flush(self, *args, **kwargs):
        pass


class IU_Storage(StorageBase):
    __version__ = __version__

    def __init__(self, db_path, name="main"):
        self.db_path = db_path
        self.name = name
        self._header_size = 100
        self._f = None

    def create(self):
        if os.path.exists(os.path.join(self.db_path, self.name + "_stor")):
            raise IOError("Storage already exists!")
        with io.open(os.path.join(self.db_path, self.name + "_stor"), "wb") as f:
            f.write(struct.pack("10s90s", self.__version__.encode("utf8"), b"|||||"))
            f.close()
        self._f = io.open(
            os.path.join(self.db_path, self.name + "_stor"), "r+b", buffering=0
        )
        self.flush()
        self._f.seek(0, 2)

    def open(self):
        if not os.path.exists(os.path.join(self.db_path, self.name + "_stor")):
            raise IOError("Storage doesn't exists!")
        self._f = io.open(
            os.path.join(self.db_path, self.name + "_stor"), "r+b", buffering=0
        )
        self.flush()
        self._f.seek(0, 2)

    def destroy(self):
        os.unlink(os.path.join(self.db_path, self.name + "_stor"))

    def close(self):
        self._f.close()
        # self.flush()
        # self.fsync()

    def data_from(self, data):
        return pickle.loads(data)

    def data_to(self, data):
        return pickle.dumps(data)

    def save(self, data):
        s_data = self.data_to(data)
        self._f.seek(0, 2)
        start = self._f.tell()
        size = len(s_data)
        self._f.write(s_data)
        self.flush()
        return start, size

    def insert(self, data):
        return self.save(data)

    def update(self, data):
        return self.save(data)

    def get(self, start, size, status="c"):
        if status == "d":
            return None
        print(locals())
        self._f.seek(start)
        return self.data_from(self._f.read(size))

    def flush(self):
        self._f.flush()

    def fsync(self):
        os.fsync(self._f.fileno())


# classes for public use, done in this way because of
# generation static files with indexes (_index directory)


class Storage(IU_Storage):
    pass
