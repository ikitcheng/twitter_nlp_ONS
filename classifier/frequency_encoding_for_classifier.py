import pandas as pd

username_source_df = pd.read_csv("username_source_freq_mapping.csv")

def convert_string_to_dict(x):
    return eval(x)

username_source_list = (username_source_df['source_freq_map'].apply(lambda x: convert_string_to_dict(x))).tolist()
all_sources = set().union(*(dictionary.keys() for dictionary in username_source_list))

for source in all_sources:
    username_source_df[source] = 0

for index in range(username_source_df.shape[0]):
    dictionary = eval(username_source_df['source_freq_map'][index])
    for platform, freq in dictionary.items():
        username_source_df.loc[index, platform] = freq

username_source_df.to_csv("username_source_freq_encoding.csv")