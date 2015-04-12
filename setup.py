from setuptools import setup, find_packages
setup(name='ksppy',
      scripts=['make_diff_image.py', 'update_wcs.py', 'combine_kmtnet.py',
               'find_sources.py'],
      package_dir={'ksppy': 'ksppy'},
      packages=find_packages(),
      package_data={'ksppy':['params/*']},
      )
