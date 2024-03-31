import json
import os

# First clone AWS SDK github
# git clone https://github.com/aws/aws-sdk-js.git


def load_file_list(directory):
    try:
        files = os.listdir(directory)
    except:
        print ("Error reading AWS API json files. Download them first.")
        print ("git clone https://github.com/aws/aws-sdk-js.git")
        exit()

    # Filter and sort the file list
    filtered_files = []
    for file in files:
        if file.endswith('min.json'):
            filtered_files.append(file)
    filtered_files.sort()

    # Group files by its first word
    files_by_command_name = {}
    for filtered in filtered_files:
        command_name = filtered[:-20]
        files_by_command_name.setdefault(command_name, []).append(filtered)
    
    # Sort and takes the last filename of the same command
    last_file_list = []
    for files_with_same_command in files_by_command_name.values():
        files_with_same_command.sort(reverse=True)
        last_file = files_with_same_command[0]
        last_file_list.append(last_file)

    return last_file_list


def read_file(commands_file):
    # Verifies if the commands_file exists, if not, creates it
    if not os.path.exists(commands_file):
        with open(commands_file, 'w'):
            pass
    # Reads the commands_file and loads it as json
    try:
        with open(commands_file, 'r') as existing_commands:
            json_commands = json.load(existing_commands)
            return json_commands
    except:
        json_commands = {}
        return json_commands


def data_load(directory, json_file):
    # Reads the API files and loads them as json
    with open(directory + json_file, 'r') as file:
        json_data = json.load(file)
        return json_data


def get_keys(data):
    # Extracts the parameters from each command
    new_command = {}
    try:
        command_name = data['metadata']['uid'][:-11]
    except KeyError:
        command_name = data['metadata']['endpointPrefix']
    data_operations = data['operations']
    if data_operations:
        operations = {}
        for key in data_operations.keys():
            if 'input' in data_operations[key].keys():
                if 'required' in data_operations[key]['input'].keys():
                    operations[key] = data_operations[key]['input']['required']
                else:
                    operations[key] = ''
            else:
                operations[key] = ''
        new_command[command_name] = operations
    else:
        new_command[command_name] = ''

    return new_command


def save_file(json_commands, commands_list, commands_file):
    # Saves commands_file with the information of the new command
    json_commands.update(commands_list)
    with open(commands_file, 'w') as file:
        updated_list = json.dumps(json_commands, indent=4)
        file.write(updated_list)


if __name__ == "__main__":

    commands_file = './commands_file.json'
    # Lists all API files
    directory = './aws-sdk-js/apis/'
    file_list = load_file_list(directory)

    for json_file in file_list:
        data = data_load(directory, json_file)
        json_commands = read_file(commands_file)
        commands_list = get_keys(data)
        save_file(json_commands, commands_list, commands_file)

    print ("Commands file created successfully!")
    print ("You can delete AWS SDK directory now.")
