from setuptools import setup

setup(name='pybaseball',
        version='0.1',
        description='retrieve baseball data in python',
        classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
        'Topic :: Baseball :: Sports :: Sabermetrics :: Data',
      	],
      	keywords='baseball data statcast sabermetrics mlb',
        author='James LeDoux',
        author_email='ledoux.james.r@gmail.com',
        url='github.com/jldbc/pybaseball',
        license='MIT',
        packages=['pybaseball'],
        install_requires=[
        	'pandas',
        	'requests',
        	'numpy'
        ]
        zip_safe=False)
