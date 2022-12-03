#!/usr/bin/env python
from distutils.core import setup
import tourcms


setup(name='tourcms-py',
      version=tourcms.__version__,
      description="Python wrapper class for TourCMS Rest API",
      long_description="A simple wrapper for connecting to the TourCMS Marketplace API (http://www.tourcms.com/support/api/mp/). This wrapper mirrors the TourCMS PHP library. See https://github.com/prio/tourcms for more details.",
      author=tourcms.__author__,
      author_email='elmaleh.inbal@gmail.com',
      url='https://github.com/InbalEl/tourcms-py',
      download_url='https://github.com/InbalEl/tourcms-py',
      license=tourcms.__license__,
      platforms=['all'],
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.8',
      ],
      py_modules=['tourcms-py'],
      )