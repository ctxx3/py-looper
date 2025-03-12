from setuptools import setup, find_packages

setup(
    name="looper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyaudio",
        "numpy",
        "keyboard"
    ],
    entry_points={
        "console_scripts": [
            "looper=start:main"  # changed entry point to start:main
        ]
    }
)
