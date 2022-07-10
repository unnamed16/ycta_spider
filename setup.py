from setuptools import setup, find_packages
import ycta_spider


setup(
    name='ycta_spider',
    version=ycta_spider.__version__,
    description='Set of api shells, sentiment estimation system and chatbot.',
    long_description=ycta_spider.__doc__.strip(),
    url='https://github.com/unnamed16/ycta_spider',
    download_url='https://github.com/unnamed16/ycta_spider',
    author=ycta_spider.__author__,
    author_email='yakimetsku@gmail.com',
    license=ycta_spider.__licence__,
    packages=find_packages(),
    extras_require={},
    install_requires=open('requirements.txt', 'r').readlines(),
    tests_require=open('requirements.txt', 'r').readlines(),
    classifiers=[
        'Programming Language :: Python',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development',
        'Topic :: Utilities'
    ],
    package_data={'ycta_spider': ['config.json']}
)
