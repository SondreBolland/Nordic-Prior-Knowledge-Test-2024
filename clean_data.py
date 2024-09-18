import pandas as pd
import data_replacements
import math
pd.options.mode.chained_assignment = None  # default='warn'

### Clean data ###
def replace_substrings(old_new_dict, filename):
    with open(filename, "r", encoding="utf8") as f:
        file_content = f.read()
        

    new_file_content = ""
    for key, value in old_new_dict.items():
        
        new_file_content = file_content.replace(key, value)
        file_content = new_file_content

    new_filename = path + "clean.csv"
    with open(new_filename, 'w', encoding="utf8") as f:
        f.write(new_file_content)
    f.close()
    return new_filename


# Original file
path = "data/"
filename = path + "total.csv"

# Replace escape characters from Nettskjema export
filename = replace_substrings(data_replacements.escape_character_dict, filename)
print("Replace escape characters:", str(data_replacements.escape_character_dict.items()))

# Replace all institution names with their shorthand
filename = replace_substrings(data_replacements.institution_dict, filename)
print("Replace all institution full names with their shorthand.")

# Replace all varations of gender with mann/kvinne
filename = replace_substrings(data_replacements.gender_dict, filename)
print("Replace all ambigious genders with standardized labels: [\'m\', \'f\'] (other gender identities are not included)")

df = pd.read_csv(filename, on_bad_lines="skip", delimiter=";", encoding="utf8")
print(f'{len(df)} submissions.')


### Rename columns ###
df = df.rename(columns=data_replacements.new_column_names)
print("Rename columns with simpler titles. Easier to use in analysis.")

# Remove all genders that are not male or female. The other gender identities do not have a large enough sample size for valid statistical analysis
df.loc[(~df['Gender'].isin(['f', 'm'])), 'Gender'] = " "
print("Removed all genders that are not in: [\'m\', \'f\']. The other gender identities do not have a large enough sample size for valid statistical analysis.")

# Replace graduation years with 2024, 2023 and before 2023
df.loc[(~df['GraduateYear'].isin(['2024', '2023'])), 'GraduateYear'] = "Before 2023"
print("Replace graduation years with: [2024, 2023, Before 2023]")

# Set "I don't know" as the answer if selected and the question is not answered
for i, row in df.iterrows():
    for column in df.columns:
        if "_unknown" in column:
            if row[column] != "Jeg vet ikke":
                continue
            # Check if answer is not empty
            prev_index = df.columns.get_loc(column) - 1
            prev_column_name = df.columns[prev_index]
            if pd.isnull(row[prev_index]):
                df[prev_column_name][i] = "I don't know"
            
                if 'Variables' in column:
                    prev_index = prev_index - 1
                    prev_column_name = df.columns[prev_index]
                    df[prev_column_name][i] = "I don't know"
                    if 'Variables5' in column or 'Variables6' in column:
                        prev_index = prev_index - 1
                        prev_column_name = df.columns[prev_index]
                        df[prev_column_name][i] = "I don't know"
                
                


df.to_csv(filename, encoding="utf8", sep=";")