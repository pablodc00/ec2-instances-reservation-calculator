import datetime, boto3
from collections import defaultdict
from ec2_reservation_check.calculate import calc_expiry_time


instance_ids = defaultdict(list)
reserve_expiry = defaultdict(list)
tags = {}

def create_boto_session(account):
    """Set up the boto3 session to connect to AWS.

    Args:
        account (dict): The AWS Account to scan as loaded from the
            configuration file.

    Returns:
        The authenticated boto3 session.

    """
    aws_access_key_id = account['aws_access_key_id']
    aws_secret_access_key = account['aws_secret_access_key']
    region = account['region']
    #aws_profile = account['aws_profile']


    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region,
        #profile_name=aws_profile,
    )

    return session


def calculate_ec2_ris(session, results):
    """Calculate the running/reserved instances in EC2.

    This function is unique as it performs both checks for both VPC-launched
    instances, and EC2-Classic instances. Classic and VPC
    instances/reservations are treated separately in the report.

    Args:
        session (:boto3:session.Session): The authenticated boto3 session.
        results (dict): Global results in dictionary format to be appended.

    Returns:
        A dictionary of the running/reserved instances for both VPC and Classic
        instances.

    """
    ec2_conn = session.client('ec2')


    paginator = ec2_conn.get_paginator('describe_instances')
    page_iterator = paginator.paginate(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    # Loop through running EC2 instances and record their AZ, type, and
    # Instance ID or Name Tag if it exists.
    for page in page_iterator:
        for reservation in page['Reservations']:
            for instance in reservation['Instances']:
                # Ignore spot instances
                if 'SpotInstanceRequestId' not in instance:
                    #az = instance['Placement']['AvailabilityZone']
                    instance_type = instance['InstanceType']
                    # Check for 'skip reservation' tag and name tag
                    found_skip_tag = False
                    instance_name = None
                    cloud_bill_review_comment = None
                    if 'Tags' in instance:
                        for tag in instance['Tags']:
                            if tag['Key'] == 'Name' and len(tag['Value']) > 0:
                                instance_name = tag['Value']                                                        
                            if tag['Key'] == 'CloudBillReviewComment' and len(tag['Value']) > 0:
                                cloud_bill_review_comment = tag['Value']                                
                                
                    instancekey = instance['InstanceId'] if not instance_name else instance_name                    
                    #print(instancekey)

                    #if instance_type == 't2.small':
                    #    print('instance type: %s instance_id: %s' %(instance_type, instancekey))

                    if cloud_bill_review_comment:
                        tags[instancekey] = cloud_bill_review_comment
                        #print(tags[instancekey])
                        cloud_bill_review_comment = None

                    results['ec2_running_instances'][(instance_type)] = \
                        results['ec2_running_instances'].get((instance_type), 0) + 1
   
                    instance_ids[(instance_type)].append(
                        instance['InstanceId'] if not instance_name
                        else instance_name)

    #print(instance_ids[('t2.small')])


    # Loop through active EC2 RIs and record their AZ and type.
    for reserved_instance in ec2_conn.describe_reserved_instances(
            Filters=[{'Name': 'state', 'Values': ['active']}])['ReservedInstances']:
        # Detect if an EC2 RI is a regional benefit RI or not

        instance_type = reserved_instance['InstanceType']

        results['ec2_reserved_instances'][(
            instance_type)] = results['ec2_reserved_instances'].get(
                (instance_type), 0) + reserved_instance['InstanceCount']

        reserve_expiry[(instance_type)].append(calc_expiry_time(
            expiry=reserved_instance['End']))
        

    return results

