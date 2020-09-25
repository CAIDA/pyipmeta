from setuptools import setup, Extension, find_packages

_pyipmeta_module = Extension("_pyipmeta",
                             libraries=["ipmeta"],
                             sources=["src/_pyipmeta_module.c",
                                      "src/_pyipmeta_ipmeta.c",
                                      "src/_pyipmeta_provider.c",
                                      "src/_pyipmeta_record.c"])

setup(name="pyipmeta",
      description="A Python interface to libipmeta",
      version="3.1.1",
      author="Alistair King",
      author_email="corsaro-info@caida.org",
      url="http://github.com/CAIDA/pyipmeta",
      license="GPLv3",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'Intended Audience :: System Administrators',
          'Intended Audience :: Telecommunications Industry',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: POSIX',
      ],
      keywords='_pyipmeta pyipmeta geolocation pfx2as',
      ext_modules=[_pyipmeta_module],
      packages=find_packages(),
      entry_points={'console_scripts': [
          'pyipmeta-lookup=pyipmeta.pyipmeta:main'
      ]},
      install_requires=[
          "python-dateutil",
          "python-keystoneclient",
          "python-swiftclient",
          ]
      )
