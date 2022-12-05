# py_doc_reader

Python Utility to read and extract text from pdf documents and images.

# Implementation

1. Set Configurations required in config file:
   INPUT_PATH - dir path where you keep all docs you need to extract text from INTERMEDIATE_OUTPUT_PATH - output dir
   path

### File Structure

```
├── py_doc_reader
|   ├──content_checker
|   ├    └── ContentChecker.py
|   ├    └── __init__.py
|   ├──core
|   ├    └── configuration.py
|   ├    └── __init__.py
|   ├──data
|   ├    └── config.ini
|   ├──editable_doc_extractor
|   ├    └── EditableDocExtractor.py
|   ├    └── __init__.py
|   ├──preprocess
|   ├    └── Preprocess.py
|   ├    └── __init__.py
|   ├──exceptions
|   ├    └── exceptions.py
|   ├    └── logger.py
|   ├    └──  __init__.py
|   ├──scanned_doc_extractor
|   ├    └── ScannedDocExtractor.py
|   ├    └──  __init__.py
|   ├── main.py
├── README.md
├── MANIFEST.in
└── setup.py
```

The purpose of building this utility is to extract text from image/ pdf documents. To run this utility, simply run the
main file after configuring the PATH variables in the config files. The code flow is as follows:

1. The run method runs on every file kept inside the input directory.
2. In the ContentChecker class, it'll check for different input types and route each file accordingly for further
   processing.
3. Image files and scanned pdf images will be routed to Preprocessing (deskewing) and then Scanned Doc Extractor
4. Editable PDFs wil be routed to Editable PDF Extractor to obtain text extractions. 


