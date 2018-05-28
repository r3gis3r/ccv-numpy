#!/usr/bin/env python

# System imports
from distutils.core import Extension, setup
from distutils      import spawn
from distutils.command import build_ext
import subprocess
import re

# Third-party modules - we depend on numpy for everything
import numpy

# Obtain the numpy include directory.  This logic works across numpy versions.
try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()


def get_swig_executable():
    "Get SWIG executable"

    # Find SWIG executable
    swig_executable = None
    for executable in ["swig", "swig2.0"]:
        swig_executable = spawn.find_executable(executable)
        if swig_executable is not None:
            break
    if swig_executable is None:
        raise OSError("Unable to find SWIG installation. Please install SWIG version 2.0 or higher.")

    # Check that SWIG version is ok
    output = subprocess.check_output([swig_executable, "-version"])
    swig_version = re.findall(r"SWIG Version ([0-9.]+)", output)[0]
    swig_version_ok = True
    swig_minimum_version = [2, 0, 0]
    for i, v in enumerate([int(v) for v in swig_version.split(".")]):
        if swig_minimum_version[i] < v:
            break
        elif swig_minimum_version[i] == v:
            continue
        else:
            swig_version_ok = False
    if not swig_version_ok:
        raise OSError("Unable to find SWIG version 2.0 or higher.")

    return swig_executable


# Subclass extension building command to ensure that distutils to
# finds the correct SWIG executable
SWIG_EXECUTABLE = get_swig_executable()
class my_build_ext(build_ext.build_ext):
    def find_swig(self):
        return SWIG_EXECUTABLE


# view extension module
_libccv = Extension("_libccv",
                   ["ccv_wrapper.i",],
                   include_dirs = [numpy_include],
                   # Currently we add this manually and need manual build step for libccv
                   extra_objects = ["./ccv/lib/libccv.a"],
                   swig_opts = ["-threads"],
                   libraries = ["png", "jpeg", "blas"]
                   )

setup(  name        = "libccv module",
        description = "Wrapper module for ccv",
        author      = "r3gis3r",
        version     = "1.0",
        ext_modules = [_libccv],
        py_modules  = ["libccv"],
        cmdclass    = {"build_ext": my_build_ext},
        )



