from collections import defaultdict
import os
import pandas as pd
import platform

# recognize OS version
plat = platform.system().lower()
if plat == 'windows':
    print("Using Windows...")
    split_sym = '\\'
elif plat == 'linux':
    print("Using Linux...")
    split_sym = '/'
elif plat == 'darwin':
    print("Using MacOS...")
    split_sym = '/'

# extract seq info from directory structure and create a dict of dict of dict for represent 
seq_info_dict = defaultdict(dict) # species-sample : r_seq : {partition: [xxx,xxx], charge: {xxx,xxx}}

for root, dirs, files in os.walk('.'):
    for dir in dirs:
        dir_path = os.path.join(root, dir)
        # print("dir_path:", dir_path)

        dir_lst = dir_path.split(split_sym)
        # print("dir_lst:", dir_lst)
        # find all the peptide dir (./species/sample/partiton_charge_Rseq)
        if len(dir_lst) == 4:
            species = dir_lst[1]
            sample = dir_lst[2]
            ss_key = "-".join([species, sample]) # species-sample

            pcr_name_lst = dir_lst[3].split("_") # partiton_charge_Rseq
            r_seq = pcr_name_lst[-1]
            charge = pcr_name_lst[-2]
            partition = "_".join(pcr_name_lst[:-2])

            # print("r_seq", r_seq, "charge", charge, "partition", partition)

            if r_seq not in seq_info_dict[ss_key]:
                seq_info_dict[ss_key][r_seq] = {'partition': [partition], 'charge': set(charge)}
            else:
                seq_info_dict[ss_key][r_seq]['partition'].append(partition)
                seq_info_dict[ss_key][r_seq]['charge'].add(charge)

# print("seq_info_dict", seq_info_dict)

# read orginal 1website_information.xlsx
df_webInfo_raw = pd.read_excel('./1website_information.xlsx', sheet_name=0)
# create a species column in df_webInfo_raw
spec_raw_lst = []
for row in df_webInfo_raw.itertuples():
    protein_raw = row.Protein
    spec_raw = protein_raw.split(' ')[0].split('_')[-1]
    spec_raw_lst.append(spec_raw.lower().capitalize().replace('-', '_'))
# add the Species column
df_webInfo_raw['Species'] = spec_raw_lst

# print("df_webInfo_raw", df_webInfo_raw)

# create a dict to represent web_info 
web_info_dict = defaultdict(list)

# traverse all the r_seq placed in the folder and fill in contents

for ss_key in seq_info_dict.keys():
    species = ss_key.split('-')[0]
    sample = ss_key.split('-')[1]

    for r_seq in seq_info_dict[ss_key].keys():
        print("Processing:", species, sample, r_seq)
        # generate partition
        partition = ",".join(seq_info_dict[ss_key][r_seq]['partition'])

        # generate charege info
        charge_lst = [int(x) for x in seq_info_dict[ss_key][r_seq]['charge']]
        charge_lst.sort()
        charge_lst = [str(x) for x in charge_lst]
        charge = ','.join(charge_lst)

        # extract protein and calcmass.y info from df_webInfo_raw
        condition1 = (df_webInfo_raw['Species'] == species) # species condition
        condition2 = (df_webInfo_raw['Sample'] == sample) # sample condition
        condition3 = (df_webInfo_raw['R_sequence'] == r_seq) # r_seq condition
        df_webInfo_sel_raw = df_webInfo_raw[condition1 & condition2 & condition3].reset_index(drop=True)
        # print(df_webInfo_sel_raw)

        # generate protein info
        protein_raw = df_webInfo_sel_raw['Protein'][0]

        tmp_elem_lst = [] # collect fragments of protein name untill meet OS=xxx
        for elem in protein_raw.split(" "):
            if "OS" not in elem:
                tmp_elem_lst.append(elem)
            else:
                break
        # generate protein name and replace '-' with '_'
        protein = " ".join(tmp_elem_lst).replace('-', '_')
        protein = "|".join(protein.split('|')[1:])
        # protein = protein
        
        # generate Calcmass_y info
        calcmy = df_webInfo_sel_raw['Calcmass.y'][0]

        # write all the information to web_info_dict for each r_seq
        web_info_dict['Species'].append(species)
        web_info_dict['Sample'].append(sample)
        web_info_dict['Protein'].append(protein)
        web_info_dict['R_sequence'].append(r_seq)
        web_info_dict['Partition'].append(partition)
        web_info_dict['z'].append(charge)
        web_info_dict['Calcmass_y'].append(calcmy)

# generate web_info.xlsx
df_web_info = pd.DataFrame.from_dict(web_info_dict)
df_web_info.to_excel('./web_info.xlsx',index=False)

# df_rd_test = pd.read_excel('./web_info.xlsx', sheet_name=0)
# print('df_rd_test:')
# print(df_rd_test)

print("Complete!")




