# Author: Gaurav Ail (2022)
import setuptools

with open("README.md", "r") as f:
    lstr_long_description = f.read()

setuptools.setup(
    name='py_doc_reader',
    version='1.0.0',
    description='Python Distribution Utilities',
    author='Gaurav Ail',
    author_email='ail.gaurav10@gmail.com',
    long_description=lstr_long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=['numpy==1.18.1', 'pandas==0.25.3', 'opencv-python==4.1.2.30',
                      'rapidfuzz==2.0.11', 'python-Levenshtein>=0.12.2', 'pdf2image==1.11.0',
                      'Pillow==7.0.0', 'PyMuPDF==1.16.14']
)
