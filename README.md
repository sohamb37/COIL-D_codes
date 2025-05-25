# COIL-D_codes

## preprocessing1 : <br />

root
<br />
|
<br />
hin-mai, hin-guj....
<br />
|          .... 
<br />
EDU, GOV,... 
<br />
|
<br />
sub_folder1, sub_folder2....
<br />
|
<br />
file1.txt, file2.txt.... 

Given the above directory structure, the preprocessing1 does the following:
 <br />
- Removes empty lines, leading and trailing spaces of the individual lines.
  <br />
  <br />
- Combines the files on the basis of the review status, language-pair and  primary domains. for example, one possible output file will be unreviewed_HIN-MAI_EDU.txt and so on.
  <br />
  <br />
- This will also show the no of lines in each of those output files in terms of primary-domains, lan-pair and review status.

## combine_translated_files_v1.py : <br />

Given the same directory structure as before, this file does the following: <br />

- deletes extra empty folders.
- **python3 combine_translated_files.py /path/to/parent/folder** is used to display the stats in terms of language pairs, domain and review status. <br />
- **python3 combine_translated_files.py /path/to/parent/folder -o -- output desired path/ to save/ the combined text** is used to combine and save the files organized by language pair, domain, and type. (optional) <br />
- **python3 combine_translated_files.py /path/to/parent/folder -c -- csv desired path/ to save the statistics/ as csv file** is used to save the display stats as csv file.(optional) <br />

## combine_translated_files_v2.py : <br />

Updates: <br />
- **python3 combine_translated_files.py /path/to/parent/folder -cons -- consortium desired path/ to save the combined source_translated/ as text file** is used to save the combined source_translated files, maintaining the same directory structure in the given path to be shared with the other consortium members. <br />
- Improved the process_translation_files function to add the header only once per combined file. <br />
- Corrected the count_lines_and_words function.


