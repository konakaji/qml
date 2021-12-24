import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qmlutil",
    version="0.0.5",
    author="kouhei nakaji",
    author_email="nakajijiji@gmail.com",
    description="You can receive the message 'Hello!!!'",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/konakaji/qmlutil",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "numpy~=1.21.2",
        "scipy~=1.7.1",
        "qiskit~=0.29.1",
        "Qulacs~=0.3.0",
        "matplotlib~=3.4.3",
        "setuptools~=58.0.4",
    ],
    python_requires='>=3.7',
)
