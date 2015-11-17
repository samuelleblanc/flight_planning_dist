#!/usr/bin/env python

from distutils.core import setup
import ml

long_description = """Interactive map program to plot and prepare flight plans.
					  Provides an map based interface connected to an Excel spreadsheet.
					  Calculates distances, time of flight, speed, and other typically required values whne planning science flights.
                 	  Specifically developped for NASA aircraft"""


setup(name='Moving_lines',
      version=ml.__version__,
      description='NASA Ames airborne science flight planning software',
	  long_description=long_description,
      author='Samuel LeBlanc',
      author_email='samuel.leblanc@nasa.gov',
	  Classifiers=['Development Status :: 4 - Beta',
				   'Environment :: MacOS X',
				   'Environment :: Win32 (MS Windows)',
				   'Environment :: X11 Applications',
				   'Intended Audience :: Science/Research',
				   'Natural Language :: English',
				   'Programming Language :: Python :: 2.7',
				   'Topic :: Scientific/Engineering :: Atmospheric Science',
				   'Topic :: Utilities'],
	  py_modules=['moving_lines','map_utils','excel_interafce','map_interface','gui'],
	  packages=['moving_lines'],
	  package_data={'moving_lines':['arc.ico','sat.tle','labels.txt','aeronet_locations.txt']},
	  install_requires=['matplotlib',
	                    'Tkinter',
						'numpy',
						'mpl_toolkits',
						'scipy',
						'ephem',
						'pykml',
						'simplekml',
						'gpxpy',
						'xlwings',
						'Pysolar==0.6']
     )