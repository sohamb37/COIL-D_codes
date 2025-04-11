# COIL-D_codes

## preprocessing1 : \\

root \\
|
hin-mai, hin-guj.... \\
|          |.... \\
EDU, GOV,... \\
|
sub_folder1, sub_folder2.... \\
|
file1.txt, file2.txt.... \\

Given the above directory structure, the preprocessing1 does the following:

- Removes empty lines, leading and trailing spaces of the individual lines.
- Combines the files on the basis of the review status, language-pair and  primary domains. for example, one possible output file will be unreviewed_HIN-MAI_EDU.txt and so on.
- This will also show the no of lines in each of those output files in terms of primary-domains, lan-pair and review status.
