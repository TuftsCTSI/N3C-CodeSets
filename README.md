# N3C-CodeSets

[N3C-CodeSets](https://github.com/TuftsCTSI/N3C-CodeSets) repository has three CSVs:
1) codeset.csv has a list of all [TermHub]([url](https://purple-plant-0f4023d0f.2.azurestaticapps.net/OMOPConceptSets)) codesets and their metadata
1) codeset_item.csv has one entry for every concept in the codesets
1) researcher.csv has one entry for every unique researcher_id referenced in the codeset.csv metadata (codeset_created_by and container_created_by fields)

**To regenerate these CSV files:** clone this repository, delete the existing CSV files, and execute _populateCodesets.py_. If you do not delete the existing CSV files, they will be appended to.
