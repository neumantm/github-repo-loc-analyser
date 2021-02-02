"""Module with some helper methods and classes."""

from json import JSONEncoder, JSONDecoder
from os import unlink, path, fdopen, fsync, rename
from re import sub
from tempfile import mkstemp
from typing import Callable, TextIO, Type, Any
from unicodedata import normalize

from . import CONFIG
from . import data_structure
from .data_structure import Serializable

DATA_TYPE_MODULES = [data_structure]


class SerializableJsonEncoder(JSONEncoder):
    """Json Serializer for the Serializable class."""

    def default(self, o):
        """See overridden."""
        if isinstance(o, Serializable):
            return o.serialize()
        else:
            super().default()


class SerializableJsonDecoder(JSONDecoder):
    """Json Deserializer for the Serializable class."""

    def __init__(self):
        """Init."""
        super().__init__(object_hook=deserialization_hook)


def get_serializable_class(classname: str) -> Type[Serializable]:
    """
    Get the serializable class for this name.

    Raises ValueError if no Serializable class with that name is found.
    """
    claz = None
    for module in DATA_TYPE_MODULES:
        claz = getattr(module, classname, None)
        if claz is not None:
            break
    if claz is None:
        raise ValueError("No such class was found")
    if not issubclass(claz, Serializable):
        raise ValueError("Class with that name is not a Serializable")
    return claz


def deserialization_hook(data: Any) -> Any:
    """Deserialization hook for the Serialiazable class."""
    if not isinstance(data, dict):
        return data
    if "_class" not in data:
        return data
    claz = get_serializable_class(data["_class"])
    return claz.deserialize(data)


def atmoic_write_file(filepath: str, writer: Callable[[TextIO], None], text_mode: bool = True):
    """
    Tries to atomically write to the given file using writer to get the data to write.

    Actually, writes to a temporary file and atomically moves it to the target location.
    writer should be a method writing to the givne file like object.
    text_mode is passed to the method opening the file.
    Raises ValuerError when anyhing goes wrong.
    """
    tmpfile = None
    try:
        file_basename = path.basename(filepath)
        file_basename_parts = file_basename.split(".")
        file_basename_prefix = ".".join(file_basename_parts[:-1])
        file_basename_ending = file_basename_parts[-1]
        tmpfile_fd, tmpfile = mkstemp(suffix="." + file_basename_ending,
                                      prefix=file_basename_prefix,
                                      dir=CONFIG["main"]["tmp_dir"],
                                      text=text_mode)
        with fdopen(tmpfile_fd, 'w') as f:
            writer(f)
            f.flush()
            fsync(tmpfile_fd)
        rename(tmpfile, filepath)
    except BaseException as e:
        raise ValueError("Failed to do atomic write to {}.".format(filepath)) from e
    finally:
        if tmpfile is not None and path.exists(tmpfile):
            unlink(tmpfile)


def sanitize_filename(name: str) -> str:
    """Sanitize a filename"""
    value = name.replace("/", "__")
    value = normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = sub(r'[^\w\s-]', '', value.lower())
    return sub(r'[-\s]+', '-', value)
