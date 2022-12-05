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



