from os import path
import os
from setuptools.extension import Library

from setuptools import setup, find_packages


COCOPY_SRC_DIR = os.path.join(
    os.path.dirname(__file__),
    "pycocotb", "verilator", "c_files")
COCOPY_SRCS = [os.path.join(COCOPY_SRC_DIR, p)
               for p in [
                         "signal_mem_proxy.cpp",
                         "signal_array_mem_proxy.cpp",
                         "sim_io.cpp",
                         "pycocotb_sim.cpp"]
               ]
#VERILATOR_ROOT = "/usr/local/share/verilator"
VERILATOR_ROOT = "./verilator"

VERILATOR_INCLUDE_DIR = os.path.join(VERILATOR_ROOT, "include")
VERILATOR_SOURCES = [
    os.path.join(VERILATOR_INCLUDE_DIR, x)
    for x in ["verilated.cpp", "verilated_save.cpp", "verilated_vcd_c.cpp"]
]

verilator_common = Library(
    "pycocotb.verilator.common",
    sources=COCOPY_SRCS + VERILATOR_SOURCES,
    extra_compile_args=["-std=c++11", "-I" + VERILATOR_INCLUDE_DIR],
)


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='hwtSimApiVerilator',
    version='1.2',
    description='RTL simulator API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email='michal.o.socials@gmail.com',
    install_requires=[
        "jinja2",  # template engine
        "hwtSimApi>=1.2",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "Topic :: System :: Hardware",
        "Topic :: System :: Emulators",
        "Topic :: Utilities"],
    license='MIT',
    packages=find_packages(),
    package_data={'hwtSimApiVerilator': ['*.h', '*.cpp', '*.template']},
    include_package_data=True,
    zip_safe=False,
    ext_modules=[verilator_common, ],
)
