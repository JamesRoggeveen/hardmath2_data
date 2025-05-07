import pandas as pd
import yaml
import os

def find_csv_files(csv_dir):
    csv_list = []
    for file in os.listdir(csv_dir):
        if file.endswith(".csv"):
            csv_list.append(file[:-4])
    return csv_list

def convert_csv_to_yaml_fmt(csv_file):
    df = pd.read_csv(csv_file)
    # Find the verified column
    verified_col = df.columns[df.columns.str.contains('Verified', case=False)][0]
    
    # Filter rows where verified is 'yes' (case insensitive)
    df_filtered = df[df[verified_col].str.lower() == 'yes']
    
    # Select required columns
    problems = df_filtered[['Prompt', 'Solution', 'Parameters']].rename(columns=str.lower)
    
    # Convert to YAML
    yaml_data = []
    for _, row in problems.iterrows():
        problem = {
            'prompt': row['prompt'],
            'solution': row['solution'],
            'parameters': row['parameters']
        }
        yaml_data.append(problem)
    return yaml_data

def write_yaml_file(yaml_data, csv_name):
    # Create YAML structure matching boundary_layers.yaml format
    output_file = f"data_src/{csv_name}.yaml"
    yaml_doc = {
        'meta': {
            'name': csv_name.replace('_',' ').title(),
            'date': '2025-05-03'  # Placeholder date matching example
        },
        'type': csv_name.lower(),
        'problems': yaml_data
    }
    
    # Reorder keys to put type before problems
    ordered_doc = {
        'meta': yaml_doc['meta'],
        'type': yaml_doc['type'], 
        'problems': yaml_doc['problems']
    }
    
    with open(output_file, 'w') as f:
        yaml.dump(ordered_doc, f, sort_keys=False, default_flow_style=False, indent=2)

if __name__ == "__main__":
    csv_dir = "raw_csv"
    csv_list = find_csv_files(csv_dir)
    for csv_name in csv_list:
        yaml_data = convert_csv_to_yaml_fmt(f"{csv_dir}/{csv_name}.csv")
        write_yaml_file(yaml_data, csv_name)




