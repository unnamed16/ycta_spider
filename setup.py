from setuptools import setup, find_packages
import highlight_comment


setup(
    name='highlight_comment',
    version=highlight_comment.__version__,
    description='Set of api shells, sentiment estimation system and chatbot.',
    long_description=highlight_comment.__doc__.strip(),
    url='https://github.com/unnamed16/highlight_comment',
    download_url='https://github.com/unnamed16/highlight_comment',
    author=highlight_comment.__author__,
    author_email='yakimetsku@gmail.com',
    license=highlight_comment.__licence__,
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
    package_data={'highlight_comment': ['config.json']}
)
