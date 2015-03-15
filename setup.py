from setuptools import setup, find_packages
setup(name='ksppy',
      scripts=['make_diff_image.py', 'update_wcs.py'],
      package_dir={'ksppy': 'ksppy'},
      packages=find_packages(),
      )
