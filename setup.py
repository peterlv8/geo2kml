from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='geo2kml',
    version='0.0.3',
    author='Peter LV',
    author_email='peterlvpy@gmail.com',
    description='A package to convert geojson to kml',
    long_description=readme,
    license='License :: OSI Approved :: MIT License',
    url="https://github.com/peterlv8/geo2kml",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    packages=['geo2kml'],
    python_requires=">=3.6",
)
