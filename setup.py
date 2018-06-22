#!/usr/bin/env python

# System imports
import multiprocessing
import os
import re
import subprocess
from distutils import spawn
from distutils.core import setup
from distutils.command import build_ext
from distutils.command.build import build
import distutils.command.install as orig

# Third-party modules - we depend on numpy for everything
import numpy
import setuptools
from setuptools import Extension
from setuptools.command.install import install

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


class CcvBuildExt(build_ext.build_ext):
    def find_swig(self):
        return SWIG_EXECUTABLE

    def build_ccv_static_lib(self):
        # Run configure/make
        abs_path = os.path.dirname(os.path.abspath(__file__)) + '/ccv/lib'

        def call(cmd):
            subprocess.check_call(cmd.split(' '), cwd=abs_path)

        # Run the autotools/make build to generate a python extension module
        call('./configure')
        call('make -j%s' % (multiprocessing.cpu_count()))

    def run(self):
        self.build_ccv_static_lib()
        # Call super
        build_ext.build_ext.run(self)


class CcvBuild(build):
    def run(self):
        self.run_command('build_ext')
        build.run(self)


class CcvInstall(install):
    def run(self):
        self.run_command('build_ext')
        orig.install.run(self)


# view extension module
_libccv = Extension("_libccv",
                    ["ccv_wrapper.i", ],
                    include_dirs=[numpy_include],
                    # Currently we add this manually and need manual build step for libccv
                    extra_objects=["./ccv/lib/libccv.a"],
                    swig_opts=["-threads"],
                    libraries=["png", "jpeg", "blas"]
                    )

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(name="ccv-numpy",
      description="Wrapper module for ccv using numpy arrays interface",
      author="r3gis3r",
      author_email="r3gis.3r@gmail.com",
      version="0.0.1",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/r3gis3r/ccv-numpy",
      packages=setuptools.find_packages(),
      ext_modules=[_libccv],
      py_modules=["libccv"],
      cmdclass={
          "build_ext": CcvBuildExt,
          "build": CcvBuild,
          "install": CcvInstall
      },

      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: Implementation :: CPython",
          "Topic :: Software Development :: Libraries",
          "Topic :: Scientific/Engineering :: Image Recognition"
      ]
      )
