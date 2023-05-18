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
mane_table = config["DATABASE"]["mane_table"] #"/data/home/fsysy/code/cjm_bio/NGS_pipeline/database/ensemble/MANE_GRCh37_list.tsv"
transcript_table = config["DATABASE"]["transcript_table"] #"/data/home/fsysy/code/cjm_bio/NGS_pipeline/database/ensemble/mart_export.txt"
hg19_CDS_bed = config["DATABASE"]["hg19_CDS_bed"] #"/data/home/fsysy/code/cjm_bio/NGS_pipeline/database/ensemble/hg19_CDS.bed"
HGNC_data = config["DATABASE"]["HGNC_data"] #"/data/home/fsysy/code/cjm_bio/NGS_pipeline/database/ensemble/HGNC_data.csv"

#SETTING
target = config["SETTING"]["target"]

#output
output_file = config["OUTPUT"]["output_file"] #"/data/home/fsysy/code/cjm_bio/NGS_pipeline/database/ensemble/Celemics_HC_MANE.xlsx"
summary_file = config["OUTPUT"]["summary_file"] #"/data/home/fsysy/code/cjm_bio/NGS_pipeline/database/ensemble/Celemics_HC_MANE_summary.csv"


hg19_CDS_bed = pd.read_csv(hg19_CDS_bed, sep="\t", header=None)
hg19_CDS_bed.columns = ["chr","start","end","transcript","Exon_number"]
HGNC_data = pd.read_csv(HGNC_data, sep="\t")
gene_list = pd.read_csv(gene_list_path, header=None)
gene_list.columns = ["Gene"]
mane_table = pd.read_csv(mane_table, sep="\t")
transcript_table = pd.read_csv(transcript_table, sep="\t")

gene_mane = pd.merge(gene_list,mane_table,left_on="Gene",right_on="Gene",how="left")
gene_mane_transcript = pd.merge(gene_mane,transcript_table,left_on="Ensembl_StableID_GRCh37_(Not_MANE)", right_on="Transcript stable ID version", how="left")
target_header="""Gene,MANE_TYPE,RefSeq_StableID_GRCh38_/_GRCh37,Ensembl_StableID_GRCh37_(Not_MANE),5'UTR,CDS,3'UTR,Exon region start (bp),Exon region end (bp),CDS start,CDS end,cDNA coding end,cDNA coding start,Exon rank in transcript,Genomic coding start,Genomic coding end""".split(",")
summary_df = gene_mane_transcript[target_header]
yesmane_df = summary_df[ ~summary_df["MANE_TYPE"].isnull() ] 
nomane_df = summary_df[ summary_df["MANE_TYPE"].isnull()  ]
gene_transcript_dict = {}
no_mane_df = {"Gene": [], "Why":[]}
multiple_mane_df = {"Gene": [], "Transcripts":[]}

for idx, row in nomane_df.iterrows():
    gene_name = row["Gene"]
    HGNC_matched_gene = HGNC_data[HGNC_data["Approved symbol"] == gene_name]
    if len(HGNC_matched_gene) == 0:
        print(f"{gene_name} is not HGNC approved. please check it")
        no_mane_df["Gene"].append(row['Gene'])
        no_mane_df["Why"].append("Check gene name")
    else:
        HGNC_mane_transcripts = HGNC_matched_gene["MANE Select RefSeq transcript ID (supplied by NCBI)"]
        if len(HGNC_mane_transcripts) == 0:
            print(f"There is no MANE data for {row['Gene']} in the HGNC data.")
            no_mane_df["Gene"].append(row['Gene'])
            no_mane_df["Why"].append("No Transcript in HGNC data") 
            continue
        else:
            if len(HGNC_mane_transcripts) > 1:
                print(f"There is multiple MANE data for {row['Gene']} in the HGNC data.")
                print("First transcript would be used. Please check it")
                multiple_mane_df["Gene"].append(row['Gene'])
                multiple_mane_df["Transcripts"].append(str(HGNC_mane_transcripts))

            HGNC_mane_transcript = HGNC_mane_transcripts.item()
            gene_transcript_dict[HGNC_mane_transcript] = row["Gene"]
transcript_list = list(gene_transcript_dict.keys())
nomane_CDS_bed = hg19_CDS_bed [ hg19_CDS_bed["transcript"].isin(transcript_list) ].copy()
nomane_genes = [gene_transcript_dict[a] for a in nomane_CDS_bed["transcript"].tolist()]
nomane_CDS_bed["Gene"] = nomane_genes
nomane_CDS_bed["MANE_TYPE"] = ["hg19_MANE"]*len(nomane_genes)

#If you want to use Exon level, please change config.ini, [SETTING][target]
if target == "Exon":
    target_start = "Exon region start (bp)"
    target_end = "Exon region end (bp)"
else:
    #Genomic coding start    Genomic coding end
    target_start = "Genomic coding start"
    target_end = "Genomic coding end"
nomane_CDS_bed[target_start] = nomane_CDS_bed["start"]
nomane_CDS_bed[target_end] = nomane_CDS_bed["end"]
#Done!

nomane_CDS_bed["Exon rank in transcript"] = nomane_CDS_bed["Exon_number"]
nomane_CDS_bed["RefSeq_StableID_GRCh38_/_GRCh37"] = nomane_CDS_bed["transcript"]
nomane_CDS_bed = nomane_CDS_bed.reset_index()
new_mane_bed = pd.concat([yesmane_df, nomane_CDS_bed], join="inner", ignore_index= True)

#set chromsome...
HGNC_chromosome = HGNC_data[["Approved symbol", "Chromosome"]].copy()
HGNC_chromosome["chr"] = HGNC_chromosome["Chromosome"].str.split(r"[pq]", expand = True)[0]
HGNC_chromosome["chr"] = "chr"+HGNC_chromosome["chr"]
new_mane_bed_withchr = pd.merge( new_mane_bed, HGNC_chromosome[["Approved symbol", "chr"]] , left_on="Gene",right_on="Approved symbol",how="left")
new_mane_bed_withchr = new_mane_bed_withchr.copy()[ ["chr",target_start, target_end, "Gene", "RefSeq_StableID_GRCh38_/_GRCh37", "Exon rank in transcript", "MANE_TYPE"] ]
new_mane_bed_withchr.columns = ["chromosome", "start", "end", "gene", "transcript", "rank", "mane_type"]
new_mane_bed_withchr = new_mane_bed_withchr[ ~new_mane_bed_withchr["start"].isnull() ]
new_mane_bed_withchr = new_mane_bed_withchr.astype({"start": "int", "end": "int", "rank": "int"}) 

#write bed file
new_mane_bed_withchr.to_csv(summary_file, index=False, header=False, sep="\t")
print("Done", summary_file)
success_list = new_mane_bed["Gene"].tolist()
gene_list2 = gene_list.copy()
gene_list2["success"] = ["O" if a in success_list else "X" for a in gene_list["Gene"].tolist()]

#write excel file
with pd.ExcelWriter(output_file) as writer:
    new_mane_bed_withchr.to_excel(writer, sheet_name="Success", index=False)
    no_mane_df = pd.DataFrame(data=no_mane_df)
    no_mane_df.to_excel(writer, sheet_name="Failed", index=False)
    multiple_mane_df = pd.DataFrame(data=multiple_mane_df)
    multiple_mane_df.to_excel(writer, sheet_name="Multiple_MANE", index=False)
    gene_list2.to_excel(writer, "Input_Genes", index=False)
    print("Done", output_file)
        
