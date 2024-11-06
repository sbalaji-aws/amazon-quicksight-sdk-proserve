import json
import boto3
import logging
import csv
import io
import os
import tempfile
from typing import Any, Callable, Dict, List, Optional, Union
import sys
from awsglue.utils import getResolvedOptions
import botocore


def default_botocore_config() -> botocore.config.Config:
    """Botocore configuration."""
    retries_config: Dict[str, Union[str, int]] = {
        "max_attempts": int(os.getenv("AWS_MAX_ATTEMPTS", "5")),
    }
    mode: Optional[str] = os.getenv("AWS_RETRY_MODE")
    if mode:
        retries_config["mode"] = mode
    return botocore.config.Config(
        retries=retries_config,
        connect_timeout=10,
        max_pool_connections=10,
        user_agent_extra=f"qs_sdk_admin_console",
    )


sts_client = boto3.client("sts", config=default_botocore_config())
account_id = sts_client.get_caller_identity()["Account"]
aws_region = 'us-east-1'
args = getResolvedOptions(sys.argv, ['AWS_REGION'])
print('region', args['AWS_REGION'])
glue_aws_region = args['AWS_REGION']
qs_client = boto3.client('quicksight', config=default_botocore_config())
qs_local_client = boto3.client('quicksight', region_name=glue_aws_region, config=default_botocore_config())

print(glue_aws_region)

ssm = boto3.client('ssm', region_name=glue_aws_region, config=default_botocore_config())


def get_ssm_parameters(ssm_string):
    config_str = ssm.get_parameter(
        Name=ssm_string
    )['Parameter']['Value']
    return json.loads(config_str)


def get_s3_info(account_id, glue_aws_region):
    bucket_name = get_ssm_parameters('/qs/config/groups')
    bucket_name = bucket_name['bucket-name']
    return bucket_name

def list_group_memberships(
        group_name: str,
        account_id: str,
        aws_region: str,
        namespace: str = "default"
) -> List[Dict[str, Any]]:
    return _list(
        func_name="list_group_memberships",
        attr_name="GroupMemberList",
        account_id=account_id,
        GroupName=group_name,
        Namespace=namespace,
        aws_region=aws_region
    )


def list_users(account_id, aws_region, ns) -> List[Dict[str, Any]]:
    return _list(
        func_name="list_users",
        attr_name="UserList",
        Namespace=ns,
        account_id=account_id,
        aws_region=aws_region
    )


def _list(
        func_name: str,
        attr_name: str,
        account_id: str,
        aws_region: str,
        **kwargs, ) -> List[Dict[str, Any]]:
    qs_client = boto3.client('quicksight', region_name=aws_region, config=default_botocore_config())
    func: Callable = getattr(qs_client, func_name)
    response = func(AwsAccountId=account_id, **kwargs)
    next_token: str = response.get("NextToken", None)
    result: List[Dict[str, Any]] = response[attr_name]
    while next_token is not None:
        response = func(AwsAccountId=account_id, NextToken=next_token, **kwargs)
        next_token = response.get("NextToken", None)
        result += response[attr_name]
    return result


def list_groups(
        account_id, aws_region, ns
) -> List[Dict[str, Any]]:
    return _list(
        func_name="list_groups",
        attr_name="GroupList",
        Namespace=ns,
        account_id=account_id,
        aws_region=aws_region
    )


def list_user_groups(UserName, account_id, aws_region, ns) -> List[Dict[str, Any]]:
    return _list(
        func_name="list_user_groups",
        attr_name="GroupList",
        Namespace=ns,
        UserName=UserName,
        account_id=account_id,
        aws_region=aws_region
    )


def list_namespaces(
        account_id, aws_region
) -> List[Dict[str, Any]]:
    return _list(
        func_name="list_namespaces",
        attr_name="Namespaces",
        account_id=account_id,
        aws_region=aws_region
    )


def list_dashboards(
        account_id,
        aws_region
) -> List[Dict[str, Any]]:
    return _list(
        func_name="list_dashboards",
        attr_name="DashboardSummaryList",
        account_id=account_id,
        aws_region=aws_region
    )

def list_analyses(
        account_id,
        aws_region
) -> List[Dict[str, Any]]:
    return _list(
        func_name="list_analyses",
        attr_name="AnalysisSummaryList",
        account_id=account_id,
        aws_region=aws_region
    )

def list_themes(
        account_id,
        aws_region
) -> List[Dict[str, Any]]:
    return _list(
        func_name="list_themes",
        attr_name="ThemeSummaryList",
        account_id=account_id,
        aws_region=aws_region
    )

def describe_dashboard_permissions(account_id, dashboardid, aws_region):
    qs_client = boto3.client('quicksight', region_name=aws_region, config=default_botocore_config())
    res = qs_client.describe_dashboard_permissions(
        AwsAccountId=account_id,
        DashboardId=dashboardid
    )
    return res

def describe_analysis_permissions(account_id, aid, aws_region):
    qs_client = boto3.client('quicksight', region_name=aws_region, config=default_botocore_config())
    res = qs_client.describe_analysis_permissions(
        AwsAccountId=account_id,
        AnalysisId=aid
    )
    return res

def describe_theme_permissions(account_id, aid, aws_region):
    qs_client = boto3.client('quicksight', region_name=aws_region, config=default_botocore_config())
    res = qs_client.describe_theme_permissions(
        AwsAccountId=account_id,
        ThemeId=aid
    )
    return res

def list_datasets(
        account_id,
        aws_region
) -> List[Dict[str, Any]]:
    return _list(
        func_name="list_data_sets",
        attr_name="DataSetSummaries",
        account_id=account_id,
        aws_region=aws_region
    )


def list_datasources(
        account_id,
        aws_region
) -> List[Dict[str, Any]]:
    return _list(
        func_name="list_data_sources",
        attr_name="DataSources",
        account_id=account_id,
        aws_region=aws_region
    )


def describe_data_set_permissions(account_id, datasetid, aws_region):
    qs_client = boto3.client('quicksight', region_name=aws_region, config=default_botocore_config())
    res = qs_client.describe_data_set_permissions(
        AwsAccountId=account_id,
        DataSetId=datasetid
    )
    return res


def describe_data_source_permissions(account_id, DataSourceId, aws_region):
    qs_client = boto3.client('quicksight', region_name=aws_region, config=default_botocore_config())
    res = qs_client.describe_data_source_permissions(
        AwsAccountId=account_id,
        DataSourceId=DataSourceId
    )
    return res


if __name__ == "__main__":
    sts_client = boto3.client("sts", region_name=aws_region, config=default_botocore_config())
    account_id = sts_client.get_caller_identity()["Account"]

    # call s3 bucket
    s3 = boto3.resource('s3')
    bucketname = 'admin-console' + account_id
    bucket = s3.Bucket(bucketname)

    key = 'monitoring/quicksight/group_membership/group_membership.csv'
    key2 = 'monitoring/quicksight/object_access/object_access.csv'
    tmpdir = tempfile.mkdtemp()
    local_file_name = 'group_membership.csv'
    local_file_name2 = 'object_access.csv'
    path = os.path.join(tmpdir, local_file_name)

    lists = []
    access = []
    namespaces = list_namespaces(account_id, aws_region)
    for ns in namespaces:
        try:
            ns = ns['Name']
            users = list_users(account_id, aws_region, ns)
        
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"Account " + account_id + " is not signed up with QuickSight with namespace " + ns + " . Skipping this namespace.")
                continue
        except Exception as e:
            print(e)

        for user in users:
            if user['UserName'] == 'N/A':
                continue
            try:
                groups = list_user_groups(user['UserName'], account_id, aws_region, ns)
                if len(groups) == 0:
                    lists.append([account_id, ns, None, user['UserName'], user['Email'], user['Role'], user['IdentityType']])
                else:
                    for group in groups:
                        lists.append([account_id, ns, group['GroupName'], user['UserName'], user['Email'], user['Role'], user['IdentityType']])
            except Exception as e:
                print(e)

    print(len(lists))
    #print(lists)

    with open(path, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        for line in lists:
            writer.writerow(line)
    bucket.upload_file(path, key)

    path = os.path.join(tmpdir, local_file_name2)
    print(path)
    dashboards = list_dashboards(account_id, glue_aws_region)

    for dashboard in dashboards:
        dashboardid = dashboard['DashboardId']

        response = describe_dashboard_permissions(account_id, dashboardid, glue_aws_region)
        permissions = response['Permissions']
        for principal in permissions:
            actions = '|'.join(principal['Actions'])
            principal = principal['Principal'].split("/")
            ptype = principal[0].split(":")
            ptype = ptype[-1]
            additional_info = principal[1]
            if len(principal)==4:
                # This will handle user
                principal = principal[2]+'/'+principal[3]
            elif len(principal)==3:
                # This will handle group
                principal = principal[2]
            else:
                # This will handle namespace
                principal = principal[1]

            access.append(
                [account_id, glue_aws_region, 'dashboard', dashboard['Name'], dashboardid, ptype, principal, additional_info, actions])

    datasets = list_datasets(account_id, glue_aws_region)

    for dataset in datasets:
        if dataset['Name'] not in ['Business Review', 'People Overview', 'Sales Pipeline',
                                   'Web and Social Media Analytics']:
            datasetid = dataset['DataSetId']

            response = describe_data_set_permissions(account_id, datasetid, glue_aws_region)
            permissions = response['Permissions']
            for principal in permissions:
                actions = '|'.join(principal['Actions'])
                principal = principal['Principal'].split("/")
                ptype = principal[0].split(":")
                ptype = ptype[-1]
                additional_info = principal[-2]
                if len(principal)==4:
                    principal = principal[2]+'/'+principal[3]
                elif len(principal)==3:
                    principal = principal[2]
                else:
                    principal = principal[1]
                
                access.append(
                    [account_id, glue_aws_region, 'dataset', dataset['Name'], datasetid, ptype, principal, additional_info, actions])

    datasources = list_datasources(account_id, glue_aws_region)

    for datasource in datasources:
        #print(datasource)
        if datasource['Name'] not in ['Business Review', 'People Overview', 'Sales Pipeline',
                                      'Web and Social Media Analytics']:
            datasourceid = datasource['DataSourceId']
            if 'DataSourceParameters' in datasource:
                #print(datasourceid)
                try:
                    response = describe_data_source_permissions(account_id, datasourceid, glue_aws_region)
                    #print(response)
                    permissions = response['Permissions']
                    #print(permissions)
                    for principal in permissions:
                        actions = '|'.join(principal['Actions'])
                        principal = principal['Principal'].split("/")
                        ptype = principal[0].split(":")
                        ptype = ptype[-1]
                        additional_info = principal[-2]
                        if len(principal)==4:
                            principal = principal[2]+'/'+principal[3]
                        elif len(principal)==3:
                            principal = principal[2]

                        access.append([account_id, glue_aws_region, 'data_source', datasource['Name'], datasourceid, ptype, principal,
                                       additional_info, actions])
                except Exception as e:
                    print(e)

    analyses = list_analyses(account_id, glue_aws_region)

    for analysis in analyses:
        if analysis['Status'] != 'DELETED':
            analysisid = analysis['AnalysisId']

            response = describe_analysis_permissions(account_id, analysisid, glue_aws_region)
            permissions = response['Permissions']
            for principal in permissions:
                actions = '|'.join(principal['Actions'])
                principal = principal['Principal'].split("/")
                ptype = principal[0].split(":")
                ptype = ptype[-1]
                additional_info = principal[-2]
                if len(principal)==4:
                    principal = principal[2]+'/'+principal[3]
                elif len(principal)==3:
                    principal = principal[2]
                else:
                    principal = principal[1]

                access.append(
                    [account_id, glue_aws_region, 'analysis', analysis['Name'], analysisid, ptype, principal, additional_info, actions])

    themes = list_themes(account_id, glue_aws_region)
    for theme in themes:
        if theme['ThemeId'] not in ['SEASIDE', 'CLASSIC', 'MIDNIGHT', 'RAINIER', 'AQUASCAPE']:
            themeid = theme['ThemeId']
            response = describe_theme_permissions(account_id, themeid, glue_aws_region)
            permissions = response['Permissions']
            for principal in permissions:
                actions = '|'.join(principal['Actions'])
                principal = principal['Principal'].split("/")
                ptype = principal[0].split(":")
                ptype = ptype[-1]
                additional_info = principal[-2]
                if len(principal)==4:
                    principal = principal[2]+'/'+principal[3]
                elif len(principal)==3:
                    principal = principal[2]
                else:
                    principal = principal[1]

                access.append(
                    [account_id, glue_aws_region, 'theme', theme['Name'], themeid, ptype, principal, additional_info,
                     actions])

    print(access)
    with open(path, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        for line in access:
            writer.writerow(line)

    # upload file from tmp to s3 key

    bucket.upload_file(path, key2)
