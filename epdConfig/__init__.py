from .config import *
__all__ = [
    '.config'
]
# Command define from rPi
#for func in [x for x in dir() if not x.startswith('_')]:
#    setattr(sys.modules[__name__], func, getattr(locals, func))