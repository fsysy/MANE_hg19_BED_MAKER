#! /bin/bash



#read the config.ini
#[DATABASE]
#mane_table = database/MANE_GRCh37_list.tsv
#mane_table_original= database/MANE_GRCh37_list.csv
#transcript_table = database/mart_export.txt
#hg19_CDS_bed = database/hg19_CDS.bed
#HGNC_data = database/HGNC_data.csv
CURRENT_PATH=$(pwd)
CONFIG_FILE=$CURRENT_PATH/config.ini

mane_table_original=$(awk '/^mane_table_original=/ {print $2}' $CONFIG_FILE)
mane_table=$(awk '/^mane_table=/ {print $2}' $CONFIG_FILE)
transcript_table=$(awk '/^transcript_table=/ {print $2}' $CONFIG_FILE)
hg19_CDS_bed=$(awk '/^hg19_CDS_bed=/ {print $2}' $CONFIG_FILE)
hg19_exon_bed=$(awk '/^hg19_exon_bed=/ {print $2}' $CONFIG_FILE)
HGNC_data_original=$(awk '/^HGNC_data_original=/ {print $2}' $CONFIG_FILE)
HGNC_data=$(awk '/^HGNC_data=/ {print $2}' $CONFIG_FILE)
hgTables=$(awk '/^hgTables=/ {print $2}' $CONFIG_FILE)
hgTables_exon=$(awk '/^hgTables_exon=/ {print $2}' $CONFIG_FILE)
LRG_RefSeqGene=$(awk '/^LRG_RefSeqGene=/ {print $2}' $CONFIG_FILE)

echo "Prep start!"

#Step 1: Preparation for the Ensemble data
#resource from https://tark.ensembl.org/web/mane_GRCh37_list/
sed 's/ /_/g' $mane_table_original | sed 's/"//g' | sed 's/❌/0/g' | sed 's/✔/1/g' | sed 's/,/\t/g' > $mane_table

#Step 2: Preparation for the UCSC data
#resource from UCSC table browser
#check these 1: Mammal, Human, hg19, Gene and Gene Predictions, RefSeq All (ncbiRefSeq), genome, BED
#check these 2: CDS for 2.1 / Exon for 2.2
#Step 2.1: CDS region
cat $hgTables | awk 'BEGIN{OFS="\t"}{print $1, $2, $3, $4}' | awk -F "_" 'BEGIN{ OFS="\t"} {print $1"_"$2,$4}' > $hg19_CDS_bed
#Step 2.2: Exon region
cat $hgTables_exon | awk 'BEGIN{OFS="\t"}{print $1, $2, $3, $4}' | awk -F "_" 'BEGIN{ OFS="\t"} {print $1"_"$2,$4}' > $hg19_exon_bed

#Step 3: Preparation for the HGNC data
#resource from HGNC custom
#https://www.genenames.org/download/custom/
#HGNC ID,Approved symbol,Approved name,Status,Previous symbols,Alias symbols,Chromosome,Accession numbers,RefSeq IDs
#NCBI Gene ID,RefSeq,Ensembl ID,UCSC ID,MANE SELECT Ensembl transcript ID,MANE Select RefSeq transcript ID
#new header: Approved symbol|Status|Alias symbols|Chromosome|MANE Select RefSeq transcript ID (supplied by NCBI)
#1:Approved symbol
#2:Status
#3:Alias symbols
#4:Chromosome
#5:MANE Select RefSeq transcript ID
#cat $HGNC_data_original | awk -F "\t" 'BEGIN{OFS="\t"}{print $2,$4,$6,$7,$12}' > $HGNC_data
#save all the information for the troubleshooting.
cat $HGNC_data_original > $HGNC_data

echo "Done!"

#deactive the following script if you do not want to use it separately.
#===========================
#= Makeing MANE bed file   =
#===========================
echo "makeing MANE bed"
python set_mane.py
echo "Done"

