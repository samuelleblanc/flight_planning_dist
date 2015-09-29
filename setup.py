import flight_planning
from setuptools import setup
import os

def read(fname):
	return open(os.path.join(os.path.dirname(__file__),fname)).read()

setup(
    name = 'moving_lines',
    version = flight_planning.__version__,
    author = 'Samuel LeBlanc',
    author_email = 'samuel.leblanc@nasa.gov',
    description = ('A flight planning software with integration to excel and clickable map and multi aircraft capabilities'),
    license = 'GPL',
    keywords = 'NASA Airborne Science :: flight planning :: atmospheric research',
    url = 'http://github.com/samuelleblanc/flight_planning/',
    packages = ['flight_planning'],
    long_description = read('README.MD'),
    classifiers = ['Development Status :: 4 - Beta',
                   'Programming Language :: Python :: 2.7',
		   'Intended Audience :: Science/Research',
		   'Topic :: Scientific/Engineering :: Atmospheric Science'],
    install_requires = ['numpy',
                        'matplotlib',
			'mpl_toolkits.basemap',
			'datetime',
			'scipy.misc',
			'PIL',
			'Tkinter',
			'xlwings',
			'Pysolar<0.7,>=0.6',
			'simplekml',
			'gpxpy',
			'owslib',
			'pykml',
			'ephem'],
    data_files = ['README.MD',
                  'license.txt',
		  'flight_planning/aeronet_locations.txt',
		  'flight_planning/arc.ico',
		  'file.rc',
		  'labels.txt',
		  'profiles.txt',
		  'sat.tle']
    )



    

