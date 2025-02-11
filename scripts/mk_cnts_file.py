#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

from __future__ import print_function
import sys
import os
import argparse

parser = argparse.ArgumentParser(
    usage='%(prog)s --counts_dir <path/to/coutns_dir> '
          '--gene_ids <path/to/geneIds.txt',
    description="This script summarises log files information into html table",
    add_help=True
    )
parser.add_argument('-i',
                    '--counts_file',
                    metavar='FILE',
                    required=True,
                    help="path to directory with featureCounts files"
                    )
parser.add_argument('-g',
                    '--gene_ids',
                    metavar='FILE',
                    required=True,
                    help="path to geneIds.txt file, format "
                         "EnsmblId\tChrm\tGeneName\tBiotype"
                    )
parser.add_argument('-s',
                    '--samples_sheet',
                    metavar='FILE',
                    required=True,
                    help="path to samplesSheet.txt file, format "
                         "old_prefix\tnew_prefix"
                    )
parser.add_argument('-b',
                    '--biotype',
                    metavar='STR',
                    default="protein_coding",
                    help="specify biotype of interest [protein_coding], "
                         "'all' is special to include everything"
                    )
parser.add_argument('--counts_col',
                    type=int,
                    metavar='INT',
                    default=7,
                    help="Indicate which column begins read counts. "
                         "default [7], which is featureCounts default, all "
                         "columns before 7th are metadata cols"
                    )

args = parser.parse_args()
counts_file = args.counts_file
gene_ids = args.gene_ids
samples_sheet = args.samples_sheet
usr_biotype = args.biotype
cnts_col = args.counts_col
# this is to covert to zero based index
cnts_col = cnts_col - 1

ensembl_dict = {}

with open(gene_ids) as handler:
    for i in handler:
        line = i.strip()
        line = line.split("\t")
        if line[0] in ensembl_dict:
            raise Exception(
                "%s gene Id is already in the dictionary, "
                "duplicated gene name" %
                line[0])
        ensembl_dict[line[0]] = [line[1], line[2], line[3]]

# make samples sheet dictionary
ss = open(samples_sheet).read().split("\n")
ss = [s.split("\t")[1] for s in ss if s]
sorted(ss, key=len)
ss = ss[::-1]

def get_name(raw_name, sample_names):
    for s_name in sample_names:
        if raw_name.startswith(s_name):
            return s_name
    raise Exception(
        "Didn't found sample name for this %s column in counts file, "
        "check your %s" % (raw_name, samples_sheet))

with open(counts_file) as handler:
    s_names = None
    header = True
    for i in handler:
        line = i.strip()

        if line.startswith("#"):
            continue
        if line.startswith("Geneid"):
            sample_names = line.split("\t")[cnts_col:]
            sample_names = [get_name(os.path.basename(n), ss) for n in sample_names]
            s_names = '\t'.join(sample_names)
            continue

        line = line.split("\t")
        gene_id = line[0]
        row_cnts = "\t".join(line[cnts_col:])
        if gene_id not in ensembl_dict:
            raise Exception(
                "This shouldn't happened, %s and %s don't have same number "
                "of genes" % (gene_ids, "counts_file"))

        chrom, gene_name, biotype = ensembl_dict[gene_id]

        if header:
            if not s_names:
                sys.exit(
                    "ERROR: This shouldn't happened, check samples sheet "
                    "and/or counts file columns")
            ids = "\t".join(("Gene.ID", "Chrom", "Gene.Name", "Biotype"))
            print('\t'.join((ids, s_names)))
            header = False

        if usr_biotype == "all":
            print('\t'.join((gene_id, chrom, gene_name, biotype, row_cnts)))
        elif usr_biotype == biotype:
            print('\t'.join((gene_id, chrom, gene_name, biotype, row_cnts)))
