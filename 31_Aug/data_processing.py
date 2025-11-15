import pandas as pd

# Load both Excel files
df1 = pd.read_excel('POLA_SUOMOTO_with_data.xlsx')
df2 = pd.read_excel('476_records.xlsx')

# Concatenate the dataframes
combined_df = pd.concat([df1, df2], ignore_index=True)

# Drop duplicates based on 'Request ID', keeping the row where 'Ration Card Number' is not blank
# First, sort so that rows with a value in 'Ration Card Number' come first
combined_df_sorted = combined_df.sort_values(by=['Request ID', 'Ration Card Number'], ascending=[True, False], na_position='last')

# Drop duplicates, keeping the first (which will have the value if present)
final_df = combined_df_sorted.drop_duplicates(subset=['Request ID'], keep='first')

# Save to new Excel file
final_df.to_excel('combined_no_blank_duplicates.xlsx', index=False)

print('Combined file saved as combined_no_blank_duplicates.xlsx')
