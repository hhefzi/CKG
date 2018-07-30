import os.path
import gzip
import databases_config as dbconfig
from collections import defaultdict
from KnowledgeGrapher import utils
import csv
import pandas as pd
import re
from lxml import etree
import zipfile
from parsers import *

#########################
# General functionality # 
#########################
def write_relationships(relationships, header, outputfile):
    df = pd.DataFrame(list(relationships))
    df.columns = header 
    df.to_csv(path_or_buf=outputfile, 
                header=True, index=False, quotechar='"', 
                line_terminator='\n', escapechar='\\')

def write_entities(entities, header, outputfile):
    with open(outputfile, 'w') as csvfile:
        writer = csv.writer(csvfile, escapechar='\\', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(header)
        for entity in entities:
            writer.writerow(entity)

#########################
#       Graph files     # 
#########################
def generateGraphFiles(importDirectory, databases):
    for database in databases:
        print(database)
        if database.lower() == "internal":
            result = internalDBsParser.parser()
            for qtype in result:
                relationships, header, outputfileName = result[qtype]
                outputfile = os.path.join(importDirectory, outputfileName)
                write_relationships(relationships, header, outputfile)
        elif database.lower() == "mentions":
            entities, header, outputfileName = internalDBsParser.parserMentions(importDirectory)
            outputfile = os.path.join(importDirectory, outputfileName)
            write_entities(entities, header, outputfile)
        elif database.lower() == "hgnc":
            #HGNC
            entities, header = hgncParser.parser()
            outputfile = os.path.join(importDirectory, "Gene.csv")            
            write_entities(entities, header, outputfile)
        elif database.lower() == "refseq":
            entities, relationships, headers = refseqParser.parser()
            for entity in entities:
                header = headers[entity]
                outputfile = os.path.join(importDirectory, entity+".csv")
                write_entities(entities[entity], header, outputfile)
            for rel in relationships:
                header = headers[rel]
                outputfile = os.path.join(importDirectory, "refseq_"+rel.lower()+".csv")
                write_relationships(relationships[rel], header, outputfile)
        elif database.lower() == "uniprot":
            #UniProt
            result = uniprotParser.parser()
            for dataset in result:
                entities, relationships, entities_header, relationship_header = result[dataset]
                outputfile = os.path.join(importDirectory, dataset+".csv")
                write_entities(entities, entities_header, outputfile)
                for entity, rel in relationships:
                    outputfile = os.path.join(importDirectory, "uniprot_"+entity.lower()+"_"+rel.lower()+".csv")
                    write_relationships(relationships[(entity,rel)], relationship_header, outputfile)
        elif database.lower() == "intact":
            #IntAct
            relationships, header, outputfileName = intactParser.parser()
            outputfile = os.path.join(importDirectory, outputfileName)
            write_relationships(relationships, header, outputfile)
        elif database.lower() == "string":
            #STRING
            proteinMapping, drugMapping = stringParser.parser(importDirectory)
            stringParser.parseActions(importDirectory, proteinMapping, drugMapping, download = True, db="STRING")
        elif database.lower() == "stitch":
            #STITCH
            proteinMapping, drugMapping = stringParser.parser(importDirectory, db="STITCH")
            stringParser.parseActions(importDirectory, proteinMapping, drugMapping, download = True, db="STITCH")
        elif database.lower() == "disgenet":
            #DisGeNet
            relationships, header, outputfileName = disgenetParser.parser()
            for idType in relationships:
                outputfile = os.path.join(importDirectory, idType+"_"+outputfileName)
                write_relationships(relationships[idType], header, outputfile)
        elif database.lower() == "pathwaycommons":
            #PathwayCommons pathways
            entities, relationships, entities_header, relationships_header = pathwayCommonsParser.parser()
            entity_outputfile = os.path.join(importDirectory, "Pathway.csv")
            write_entities(entities, entities_header, entity_outputfile)
            pathway_outputfile = os.path.join(importDirectory, "pathwaycommons_protein_associated_with_pathway.csv")
            write_relationships(relationships, relationships_header, pathway_outputfile)
        elif database.lower() == "dgidb":
            relationships, header, outputfileName = drugGeneInteractionDBParser.parser()
            outputfile = os.path.join(importDirectory, outputfileName)           
            write_relationships(relationships, header, outputfile)
        elif database.lower() == "sider":
            relationships,header, outputfileName, drugMapping, phenotypeMapping = siderParser.parser()
            outputfile = os.path.join(importDirectory, outputfileName)
            write_relationships(relationships, header, outputfile)
            relationships, header, outputfileName = parserIndications(drugMapping, phenotypeMapping, download = True)
            outputfile = os.path.join(importDirectory, outputfileName)
            write_relationships(relationships, header, outputfile)
        elif database.lower() == "oncokb":
            entities, relationships, entities_header,  relationships_headers = oncokbParser.parser()
            outputfile = os.path.join(importDirectory, "oncokb_Clinically_relevant_variant.csv")
            write_entities(entities, entities_header, outputfile)
            for relationship in relationships:
                oncokb_outputfile = os.path.join(importDirectory, "oncokb_"+relationship+".csv")
                if relationship in relationships_headers:
                    header = relationships_headers[relationship]
                else:
                    header = ['START_ID', 'END_ID','TYPE']
                write_relationships(relationships[relationship], header, oncokb_outputfile)
        elif database.lower() == "cancergenomeinterpreter":
            entities, relationships, entities_header, relationships_headers = cancerGenomeInterpreterParser.parser()
            entity_outputfile = os.path.join(importDirectory, "cgi_Clinically_relevant_variant.csv")
            write_entities(entities, entities_header, entity_outputfile)
            for relationship in relationships:
                cgi_outputfile = os.path.join(importDirectory, "cgi_"+relationship+".csv")
                if relationship in relationships_headers:
                    header = relationships_headers[relationship]
                else:
                    header = ['START_ID', 'END_ID','TYPE']
                write_relationships(relationships[relationship], header, cgi_outputfile)
        elif database.lower() == "hmdb":
            entities, relationships, entities_header, relationships_header = hmdbParser.parser()
            entity_outputfile = os.path.join(importDirectory, "Metabolite.csv")
            write_entities(entities, entities_header, entity_outputfile)
            for relationship in relationships:
                hmdb_outputfile = os.path.join(importDirectory, relationship+".csv")
                write_relationships(relationships[relationship], relationships_header, hmdb_outputfile)
        elif database.lower() == "drugbank":
            entities, relationships, entities_header, relationships_headers = drugBankParser.parser()
            entity_outputfile = os.path.join(importDirectory, "Drug.csv")
            write_entities(entities, entities_header, entity_outputfile)            
            for relationship in relationships:
                relationship_outputfile = os.path.join(importDirectory, relationship+".csv")
                header = ['START_ID', 'END_ID','TYPE', 'source']
                if relationship in relationships_headers:
                    header = relationships_headers[relationship]
                write_relationships(relationships[relationship], header, relationship_outputfile)
        elif database.lower() == "gwascatalog":
            entities, relationships, entities_header, relationships_header = gwasCatalogParser.parser()
            entity_outputfile = os.path.join(importDirectory, "GWAS_study.csv")
            write_entities(entities, entities_header, entity_outputfile)
            for relationship in relationships:
                outputfile = os.path.join(importDirectory, "GWAS_study_"+relationship+".csv")
                write_relationships(relationships[relationship], relationships_header, outputfile)


if __name__ == "__main__":
    generateGraphFiles(importDirectory = '/Users/albertosantos/Downloads/test/', databases = [
            #"Internal",
            #"HGNC", 
            #"RefSeq", 
            #"UniProt", 
            #"IntAct", 
            #"DisGEnet", 
            #'DrugBank',
            #"DGIdb", 
            #"OncoKB", 
            #"STRING", 
            #"STITCH", 
            #"CancerGenomeInterpreter", 
            #"SIDER",
            "HMDB",
            "PathwayCommons",
            'GWASCatalog',
            "Mentions" 
            ])
