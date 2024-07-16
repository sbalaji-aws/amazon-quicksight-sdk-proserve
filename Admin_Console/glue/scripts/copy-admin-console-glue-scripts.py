import sys
import boto3
import logging
from awsglue.utils import getResolvedOptions

args = getResolvedOptions(sys.argv, ['AWS_REGION','AWS_ACCOUNT_ID'])
current_region = args['AWS_REGION']
account_id = args['AWS_ACCOUNT_ID']

source_bucket_key_1 = "admin-console-cfn-dataprepare-code/glue/scripts/glue-quicksight-admin-console-user-data-access-info.py"
source_bucket_key_2 = "admin-console-cfn-dataprepare-code/glue/scripts/glue-quicksight-admin-console-dataset-dashboard-info.py"

target_bucket = "aws-glue-assets-" + account_id + "-" + current_region
target_key_1 = "scripts/glue-quicksight-admin-console-user-data-access-info.py"
target_key_2 = "scripts/glue-quicksight-admin-console-dataset-dashboard-info.py"

s3 = boto3.client('s3')

"""Make a copy of the glue-quicksight-admin-console-user-data-access-info.py & glue-quicksight-admin-console-dataset-dashboard-info.py scripts and place it in the Glue assets S3 bucket. This will allow the script to be edited or updated as needed for different use cases or requirements."""
response_1 = s3.copy_object(Bucket=target_bucket,CopySource=source_bucket_key_1,Key=target_key_1)

response_2 = s3.copy_object(Bucket=target_bucket,CopySource=source_bucket_key_2,Key=target_key_2)
