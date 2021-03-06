# NGO_Name_Extractor
A tool to extract and verify NGO names from annual reports, part of UCL Systems Engineering Module, Team 36.

## Requirements  

### Azure Cognative Services
An Azure Cognative Services API token is required. Fill in configuration.txt as follows:

First line - API token.

Second line - endpoint url.

E.g. 

```
eeca4bbd274c4b4e97d0a945aebf8b98
https://uksouth.api.cognitive.microsoft.com/

```

This program is based on Python 3.7.

### Database
This program requires access to database to store data. Database should contain table 'pdfs' with two columns, "PDF_NAME" and "NGO_NAME", both large varchars.

Connection details for database should be put in connect.py.

### Required Python libraries
```
Pillow
azure.cognitiveservices.language.textanalytics
msrest.authentication
Poppler
```

Poppler can be installed with Brew on Linux based machines.

# Usage

## Setup
Input database details into connect.py.

Input details into configuration.txt as described above.

Store PDF documents to process in report directory.

## Use
This program is designed to streamline the process of providing NGO names for PDFs by searching documents for names and asking for user confirmation. The program then automatically uploads the correct NGO name and filename to the database.

The application runs from extract.py.

The application will iterate through all reports in reports directory.

Follow onscreen instructions.

```
a: find name, s: find first three pages of text, d: ignore file, <empty input> - accept found name, anything else accepted as name
> 
```

User can select any of the options seen above.


