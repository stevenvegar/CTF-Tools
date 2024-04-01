# Operation Shadow Cloud

During the February 2024 , I participated on the brand new **INE's CTF Arena**, I encountered a series of challenges centered around AWS hacking. After completing the CTF, I documented a comprehensive walkthrough of the challenges, which you can find here:\
[INE's CTF - Operation Shadow Cloud Writeup](https://dc506.org/ines-ctf-operation-shadow-cloud-writeup/)

Inspired by the CTF challenges, I developed my own AWS enumeration tool called `aws_enum_for_ctf.py`.

## [aws_enum_for_ctf.py](https://github.com/stevenvegar/CTF-Tools/blob/main/INECTFArena/OperationShadowCloud/aws_enum_for_ctf.py)
This script facilitates the identification of available AWS CLI commands based on the current permissions and credentials. It executes each command to determine which ones are executable.
![1_help.png](https://github.com/stevenvegar/CTF-Tools/blob/main/INECTFArena/OperationShadowCloud/images/1_help.png)

First of all, you need to provide an AWS CLI profile which you can configure it with ` aws configure ` or you can modify the ` ~/.aws/credentials ` file. This should look like this:\
<img src="/INECTFArena/OperationShadowCloud/images/2_creds.png" width=70%>

This script has some useful features to improve the enumeration:
- profile: Specify the AWS CLI profile to use by the script to execute every service commands. Required.
- level: Determine the level of commands to enumerate, ranging from 1 to 5, with level 1 being the most common. Default is set to 1.
- options: Add custom options obtained from previous enumeration. E.g. '--bucket xxxx, --arn zzzz'.
- max_output: Set the maximum size of output to display on the terminal. Default is 2000 bytes.
- service: Override the level option and perform enumeration on a specific service.

### Usage:
` python3 ./aws_enum_for_ctf.py --profile <PROFILE> `

With no additional options, it executes the level 1 of enumeration, the most common services are requested; and shows the issued command and outputs the result if this not exceed 2000 bytes limit.
<img src="/INECTFArena/OperationShadowCloud/images/3_no_add_options.png" width=70%>

When the script finishes enumeration, provides a summary of successful commands and their output size generated from each one. Providing a list for further manual enumeration.
<img src="/INECTFArena/OperationShadowCloud/images/4_summary.png" width=70%>

If additional options are provided, helps to narrow the enumeration and information extraction process. As shown below, ` --service "s3" ` indicates the specific service to enumerate, also ` --options "--bucket stvg4r-test1" ` indicates to the script that should execute every command that has the "--bucket" parameter.
<img src="/INECTFArena/OperationShadowCloud/images/5_service.png" width=70%>

At the end, shows a list of the successful commands, including any additional options provided.
<img src="/INECTFArena/OperationShadowCloud/images/6_service.png" width=70%>



## [commands_file.json](https://github.com/stevenvegar/CTF-Tools/blob/main/INECTFArena/OperationShadowCloud/commands_file.json)
This file has the complete list of every command and its required options of each service you can access via the CLI. It is consumed by the main script to construct the appopiate commands based on the user's input.

## [create_commands_file.py](https://github.com/stevenvegar/CTF-Tools/blob/main/INECTFArena/OperationShadowCloud/create_commands_file.py)
This script creates an updated commands_file.json file from the AWS SDK API documentation. It is not necessary to run it because the file is already created, but just in case.
