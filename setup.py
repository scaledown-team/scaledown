import setuptools
import scaledown
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setuptools.setup(
    name="scaledown",
    version=scaledown.__version__,
    author="csoham",
    author_email="hello@csoham.com",
    description="Scaledown is an Open Source Neural Network Optimization Framework for TinyML Devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scaledown-team/scaledown",
    project_urls={
        "Bug Tracker": "https://github.com/scaledown-team/scaledown/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(exclude=['test*']),
    python_requires=">=3.6",
)
