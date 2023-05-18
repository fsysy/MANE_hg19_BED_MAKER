1. What is this code?
This code is to make a bed file coordinate to the hg19 human genome according to the gene name.
gene_list --> bed_file (hg19, MANE select or MANE select PLUS or MANE_RefSeq)

2. What is the input file?
A list of gene names.
Please, use gene name HGNC approved.
Alias name or unapproved would be not converted into bed format.
location: input [generally]
IMPORTANT! You have to modify [INPUT] in the config.ini to use new input data!

3. What is the output file?
A bed file and a excel file
The bed file is the purpose of this code, 
and the excel file includes important logs.
IMPORTANT! 
Do not use the bed file without checking the excel file,
especially these following sheets, "Failed, Multiple MANE, and Input_Genes"
You have to check the genes in "Failed" sheet, and maybe modify some gene name in the input file.

4. How can I download data?
This code need some foundation data.
It's from UCSC(or NCBI) and Ensemble.
The method is write on the mane.sh as comments.
You should modify the path of each database on the config.ini

5. How can I use this code?
If the database is not modifed yet, you have to run mane.sh.

example)
$ sh mane.sh
 
This code is needed just for first time and do not have to run anymore.
If you operate the mane.sh multiple times, but it's ok anyway.

After the modification of the original database use mane.sh, you can get bed file with

$ python set_mane.py

And check the output folder.

IMPORTANT!
Please check the input file and config.ini
You have to put in input file and modify config.ini accoring to the input file path!



Thanks!

Please contact to MD. PHD. JM Choi if you have any question.
fsysy@naver.com
fsysy@mf.seegene.com
+82 10)8771-7264
