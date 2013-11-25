from distutils.core import setup

# Parse the version, may not be able to import the module at this point.
han_py = open('howaboutnow.py', 'r').read()
vi = han_py.index("__version__ = '") + 15
__version__ = han_py[vi:han_py.index("'", vi)]

setup(name='howaboutnow',
      version=__version__,
      description='Asynchronous rechecking tool',
      author='Fergal Hainey',
      py_modules=['howaboutnow'],
      )
