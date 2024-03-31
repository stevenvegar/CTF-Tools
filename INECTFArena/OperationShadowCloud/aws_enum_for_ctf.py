import json
import os
import argparse
import subprocess
import re

def parse_args():
	# Parse command line arguments
	parser = argparse.ArgumentParser(description='AWS access enumeration tool')
	parser.add_argument('-p', '--profile', type=str, required=True, help='Required. AWS CLI profile to use')
	parser.add_argument('-l', '--level', type=int, choices=range(1, 6), help='Level of common kind commands. From 1 to 5 (default: 1)')
	parser.add_argument('-o', '--options', nargs='+', help='Additional options for enumeration (comma separated) (e.g. --options "--bucket test-bucket, --role-name test-role")')
	parser.add_argument('-m', '--max_output', type=int, default=2000, help='Max output size shown when a command is sucessful (default: 2000)')
	parser.add_argument('-s', '--service', nargs='+', help='Enumerate specific services (comma separated) (e.g --service "s3api, iam")')
	return parser.parse_args()


def get_args():
	# Get command line arguments and perform additional validations
	args = parse_args()
	if args.options and not args.options[0]:
		raise ValueError("The --options argument must contain at least one option")
	if args.service and not args.service[0]:
		raise ValueError("The --service argument must contain at least one service")
	PROFILE = args.profile
	level_mapping = {1: level1, 2: level2, 3: level3, 4: level4, 5: level5}
	LEVEL = level_mapping.get(args.level, level1)
	ADD_OPTIONS = args.options[0].split(',') if args.options else None
	MAX_OUTPUT = args.max_output if args.max_output else 2000
	SERVICE = args.service[0].split(',') if args.service else None
	return PROFILE, LEVEL, ADD_OPTIONS, MAX_OUTPUT, SERVICE


def read_commands_file(commands_file):
	# Read commands file and load it as a JSON dictionary
	try:
		with open(commands_file, 'r') as existing_commands:
			json_commands = json.load(existing_commands)
			return json_commands
	except:
		print ("Error reading commands file. Use create_commands_file.py to solve it.")
		exit()


def construct_commands(all_commands, LEVEL, PROFILE, ADD_OPTIONS, MAX_OUTPUT):
	# Construct and execute commands based on provided options
	success_dict = {}
	for command in all_commands.keys():
		if command in LEVEL:
			all_options = all_commands[command].items()
			if command == "s3":
				command = "s3api"
			for item in all_options:
				if item[0].startswith(('Describe', 'Get', 'List')):
					# If there are no additional options and the command doesn't require options
					if ADD_OPTIONS is None and not item[1]:
						const_command = f"aws {command} {item[0]} --profile {PROFILE}"
						success_command, success_lenght = execute_command(const_command, MAX_OUTPUT)
						if success_command != None:
							success_dict[success_command] = success_lenght
					# If there are additional options but the command doesn't require options
					if ADD_OPTIONS and not item[1]:
						const_command = f"aws {command} {item[0]} --profile {PROFILE}"
						success_command, success_lenght = execute_command(const_command, MAX_OUTPUT)
						if success_command != None:
							success_dict[success_command] = success_lenght
					# If there are both, additional options and the command has options
					if ADD_OPTIONS and item[1]:
						user_options = []
						command_options = []
						for options in ADD_OPTIONS:
							option = re.search(r'--(\w+)', options).group(1).lower()
							user_options.append(option)
						for comm_options in item[1]:
							command_options.append(comm_options.lower())
						# Check required command options are the same as the supplied options
						difference = set(command_options).difference(set(user_options))
						for opt in user_options:
							if opt in command_options:
								for opts in ADD_OPTIONS:
									if opt in opts:
										if len(difference) != 0:
											print (f"[X] aws {command} {item[0]} --profile {PROFILE} {opts}")									
											print (f"    Requires: {command_options}")
										else:
											const_command = f"aws {command} {item[0]} --profile {PROFILE} {opts}"
											success_command, success_lenght = execute_command(const_command, MAX_OUTPUT)
											if success_command != None:
												success_dict[success_command] = success_lenght
	return success_dict


def execute_command(command, MAX_OUTPUT):
	# Execute a command and handle output
	# Normalizes the AWS parameters, converts to lowercase and adds hyppen - between words
	pattern = re.compile(r'(?<! )([A-Z][a-z])')
	command = pattern.sub(r'-\1', command)
	pattern = re.compile(r'([a-z])([A-Z])')
	command = pattern.sub(r'\1-\2', command).lower()

	try:
		execute_command = subprocess.run([command], shell=True, capture_output=True, text=True, timeout=10)
		if execute_command.returncode == 0 and len(execute_command.stdout) != 0:
			print (f"[>] {command}")
			if len(execute_command.stdout) < MAX_OUTPUT:
				print (execute_command.stdout)
			else:
				print (f"    Success command but output not shown. Output lenght: {len(execute_command.stdout)}")
			return command, len(execute_command.stdout)
		else:
			print (f"[X] {command}")
			if "ExpiredToken" in execute_command.stderr:
				print ("[X] Error. Expired credentials, should be renewed to continue.")
				exit()
			return None, None
	except subprocess.TimeoutExpired:
		print (f"[/] {command}")
		print (f"    Exited by timeout.")
		return command, "Exited by timeout"
	except Exception as e:
		print (e)
		exit()


if __name__ == "__main__":
	# Different levels of the common kind of commands, the most common first
	level1 = ["account", "apigateway", "apigatewayv2", "cloud9", "cloudfront", "cloudtrail", "cognito-identity", "cognito-idp", "cognito-sync", "dynamodb", "ec2", "events", "iam", "lambda", "logs", "s3", "secretsmanager", "sns", "sqs", "sts"]
	level2 = ["acm-pca", "amp", "amplify", "appstream", "backup", "bedrock", "clouddirectory", "cloudformation", "cloudsearch", "cloudwatch", "codepipeline", "codestar", "discovery", "drs", "ecr", "ecr-public", "ecs", "glue", "grafana", "inspector", "launch-wizard", "location", "m2", "neptune", "neptunedata", "payment-cryptography-data", "personalize", "personalize-runtime", "pi", "pinpoint", "pinpoint-sms-voice-v2", "pipes", "privatenetworks", "qbusiness", "ram", "rds-data", "redshift", "redshift-data", "redshift-serverless", "resource-groups", "resourcegroupstaggingapi", "rolesanywhere", "route53", "route53-recovery-control-config", "route53-recovery-readiness", "route53domains", "savingsplans", "scheduler", "service-quotas", "storagegateway", "transfer", "workdocs", "workspaces", "workspaces-thin-client"]
	level3 = ["acm", "apigatewaymanagementapi", "appconfig", "appconfigdata", "appsync", "cloudcontrol", "cloudhsm", "cloudhsmv2", "codeartifact", "codebuild", "codecommit", "connect", "datasync", "datazone", "ds", "eks", "es", "identitystore", "imagebuilder", "keyspaces", "kms", "lightsail", "machinelearning", "managedblockchain", "managedblockchain-query", "memorydb", "mq", "network-firewall", "networkmanager", "networkmonitor", "organizations", "payment-cryptography", "pinpoint-email", "qconnect", "rds", "rekognition", "resource-explorer-2", "route53-recovery-cluster", "route53resolver", "rum", "s3outposts", "servicecatalog", "servicecatalog-appregistry", "servicediscovery", "support", "support-app", "transcribe", "vpc-lattice", "waf", "waf-regional", "wafv2", "workmail", "workspaces-web"]
	level4 = ["amplifybackend", "appflow", "appintegrations", "application-insights", "appmesh", "apprunner", "arc-zonal-shift", "artifact", "auditmanager", "autoscaling", "b2bi", "batch", "bedrock-agent", "ce", "chime-sdk-identity", "chime-sdk-messaging", "cleanroomsml", "cloudfront-keyvaluestore", "codecatalyst", "codeguru-security", "codeguruprofiler", "codestar-notifications", "comprehend", "comprehendmedical", "cost-optimization-hub", "cur", "databrew", "dataexchange", "datapipeline", "dax", "devicefarm", "devops-guru", "dms", "docdb-elastic", "dynamodbstreams", "efs", "elastictranscoder", "elb", "elbv2", "emr", "entityresolution", "finspace", "fis", "forecast", "forecastquery", "gamelift", "glacier", "greengrass", "greengrassv2", "guardduty", "healthlake", "honeycode", "inspector2", "iot-data", "iot1click-devices", "iot1click-projects", "iotanalytics", "iotevents-data", "iotthingsgraph", "ivs-realtime", "ivschat", "kafkaconnect", "kinesis-video-media", "kinesis-video-webrtc-storage", "kinesisanalytics", "kinesisanalyticsv2", "lakeformation", "lex-runtime", "lexv2-models", "lexv2-runtime", "license-manager", "license-manager-linux-subscriptions", "license-manager-user-subscriptions", "lookoutequipment", "marketplace-agreement", "marketplace-catalog", "marketplace-deployment", "marketplace-entitlement", "mediaconnect", "mediatailor", "meteringmarketplace", "mgh", "mgn", "migrationhuborchestrator", "mobile", "mturk", "mwaa", "neptune-graph", "oam", "omics", "opensearch", "opensearchserverless", "opsworks", "panorama", "pca-connector-ad", "pinpoint-sms-voice", "pricing", "proton", "qldb", "quicksight", "repostspace", "resiliencehub", "robomaker", "sagemaker", "sagemaker-a2i-runtime", "sagemaker-edge", "sagemaker-runtime", "serverlessrepo", "ses", "sesv2", "shield", "sms-voice", "ssm", "ssm-sap", "sso-oidc", "stepfunctions", "textract", "timestream-write", "tnb", "verifiedpermissions", "wellarchitected", "wisdom", "worklink"]
	level5 = ["accessanalyzer", "alexaforbusiness", "amplifyuibuilder", "appfabric", "application-autoscaling", "applicationcostprofiler", "athena", "autoscaling-plans", "backup-gateway", "backupstorage", "bcm-data-exports", "bedrock-agent-runtime", "bedrock-runtime", "braket", "budgets", "billingconductor", "chime", "chime-sdk-meetings", "chime-sdk-media-pipelines", "chime-sdk-voice", "cleanrooms", "cloudsearchdomain", "cloudtrail-data", "codeguru-reviewer", "codestar-connections", "compute-optimizer", "connect-contact-lens", "connectcampaigns", "connectcases", "connectparticipant", "controltower", "customer-profiles", "detective", "directconnect", "dlm", "docdb", "ebs", "ec2-instance-connect", "eks-auth", "elastic-inference", "elasticache", "elasticbeanstalk", "emr-containers", "emr-serverless", "evidently", "finspace-data", "firehose", "fms", "frauddetector", "freetier", "fsx", "globalaccelerator", "groundstation", "health", "importexport", "inspector-scan", "internetmonitor", "iot", "iot-jobs-data", "iot-roborunner", "iotdeviceadvisor", "iotevents", "iotfleethub", "iotfleetwise", "iotsecuretunneling", "iotsitewise", "iottwinmaker", "iotwireless", "ivs", "kafka", "kendra", "kendra-ranking", "kinesis", "kinesis-video-archived-media", "kinesis-video-signaling", "kinesisvideo", "lex-models", "lookoutmetrics", "lookoutvision", "macie2", "marketplacecommerceanalytics", "mediaconvert", "medialive", "mediapackage", "mediapackage-vod", "mediapackagev2", "mediastore", "mediastore-data", "medical-imaging", "migration-hub-refactor-spaces", "migrationhub-config", "migrationhubstrategy", "nimble", "opsworkscm", "osis", "outposts", "personalize-events", "polly", "qldb-session", "rbin", "s3control", "sagemaker-featurestore-runtime", "sagemaker-geospatial", "sagemaker-metrics", "schemas", "sdb", "securityhub", "securitylake", "signer", "simspaceweaver", "sms", "snow-device-management", "snowball", "ssm-contacts", "ssm-incidents", "sso", "sso-admin", "supplychain", "swf", "synthetics", "timestream-query", "translate", "trustedadvisor", "voice-id", "workmailmessageflow", "xray"]

	commands_file = './commands_file.json'
	PROFILE, LEVEL, ADD_OPTIONS, MAX_OUTPUT, SERVICE = get_args()

	# Overrides the level if specific service is supplied
	if SERVICE:
		LEVEL = SERVICE

	all_commands = read_commands_file(commands_file)
	success_dict = construct_commands(all_commands, LEVEL, PROFILE, ADD_OPTIONS, MAX_OUTPUT)

	# Prints the summary of the successful commands at the end
	print ("\n\n[>] Successful commands:\n")
	for command, lenght in success_dict.items():
		print (f"[>] Command: {command} / Output Lenght: {lenght}")
