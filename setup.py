from setuptools import setup, find_packages
import highlight_comment
import os
from setuptools.command.build_py import build_py
from shutil import copytree

HERE = os.path.abspath(os.path.dirname(__file__))
NAME = os.path.join("highlight_comment", "config.json")


class BuildCommand(build_py):

    def run(self) -> None:
        build_py.run(self)
        if not self.dry_run:
            target_dir = os.path.join(self.build_lib, NAME)
            copytree(os.path.join(HERE, NAME), target_dir)


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
    cmdclass={"build_py": BuildCommand},
)
