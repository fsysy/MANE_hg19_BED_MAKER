import pandas as pd
import numpy as np
import configparser
import os


#get current exe dir
current_path = os.path.dirname(os.path.abspath(__file__))
#set path
os.chdir(current_path)

#load config
config = configparser.ConfigParser()
config.read('config.ini')

#input
gene_list_path = config["INPUT"]["gene_list_path"]

#DB
mane_table = config["DATABASE"]["mane_table"]
transcript_table = config["DATABASE"]["transcript_table"]
hg19_CDS_bed = config["DATABASE"]["hg19_CDS_bed"]
HGNC_data = config["DATABASE"]["HGNC_data"]
LRG_data = config["DATABASE"]["LRG_RefSeqGene"]

#SETTING
target = config["SETTING"]["target"]

#output
output_file = config["OUTPUT"]["output_file"]
summary_file = config["OUTPUT"]["summary_file"]


#Load DB and prep
hg19_CDS_bed = pd.read_csv(hg19_CDS_bed, sep="\t", header=None)
hg19_CDS_bed.columns = ["chr","start","end","transcript","Exon_number"]
HGNC_data = pd.read_csv(HGNC_data, sep="\t")
gene_list = pd.read_csv(gene_list_path, header=None)
gene_list.columns = ["Gene"]
mane_table = pd.read_csv(mane_table, sep="\t")
transcript_table = pd.read_csv(transcript_table, sep="\t")

LRG_data = pd.read_csv(LRG_data, sep="\t")
LRG_ref = LRG_data[ LRG_data["Category"] == "reference standard" ].reset_index()
LRG_ref = LRG_ref[["Symbol","RNA","GeneID"]].copy()
LRG_ref.columns = ["Symbol", "LRG_RNA", "GeneID"]

#Join Gene DB
gene_mane = pd.merge(gene_list,mane_table,left_on="Gene",right_on="Gene",how="left")
gene_mane_LRG = pd.merge(gene_mane, LRG_ref, left_on="Gene", right_on="Symbol", how="left")
gene_mane_LRG_HGNC = pd.merge(gene_mane_LRG, HGNC_data, left_on="Gene", right_on="Approved symbol", how="left")

#use transcript following order
#1. Ensemble https://tark.ensembl.org/web/mane_GRCh37_list/
#2. UCSC downloaded data
#3. NCBI LRG selected

gene_mane_LRG_HGNC["final_transcript"] = gene_mane_LRG_HGNC["RefSeq_StableID_GRCh38_/_GRCh37"]
gene_mane_LRG_HGNC["final_source"] = gene_mane_LRG_HGNC["MANE_TYPE"]
gene_mane_LRG_HGNC.loc[ gene_mane_LRG_HGNC["final_transcript"].isna(), "final_source"  ] = "HGNC_REF_MANE"
gene_mane_LRG_HGNC.loc[ gene_mane_LRG_HGNC["final_transcript"].isna(), "final_transcript"  ] = gene_mane_LRG_HGNC["MANE Select RefSeq transcript ID (supplied by NCBI)"]
gene_mane_LRG_HGNC.loc[ gene_mane_LRG_HGNC["final_transcript"].isna(), "final_source"  ] = "LRG"
gene_mane_LRG_HGNC.loc[ gene_mane_LRG_HGNC["final_transcript"].isna(), "final_transcript" ] = gene_mane_LRG_HGNC["LRG_RNA"]
gene_mane_LRG_HGNC.loc[ gene_mane_LRG_HGNC["final_transcript"].isna(), "final_source" ] = np.nan

gene_transcript = pd.merge(gene_mane_LRG_HGNC, hg19_CDS_bed,left_on="final_transcript", right_on="transcript", how="left")

#to bed file
passed_gene_transcript = gene_transcript[ ~gene_transcript["final_source"].isna() ].copy().reset_index() 
bed_file = passed_gene_transcript[ ["chr", "start", "end", "Gene", "transcript", "Exon_number", "final_source"] ]

#summary_file = bed_file
bed_file.to_csv(summary_file)

#write excel file
with pd.ExcelWriter(output_file) as writer:
    #Too big!!
    #gene_transcript.to_excel(writer, sheet_name="Transcript", index=False)
    gene_mane_LRG_HGNC.to_excel(writer, sheet_name="Gene", index=False)

