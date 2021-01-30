import click
from ec2_reservation_check.aws import (
    calculate_ec2_ris,
    create_boto_session
)
from ec2_reservation_check.calculate import report_diffs
from ec2_reservation_check.config import parse_config
from ec2_reservation_check.report import report_results


current_config = {}
# current_config = {
#   'Accounts': [
#       {
#           'name': 'Account 1',
#           'aws_access_key_id': '',
#           'aws_secret_access_key': '',
#           'region': 'us-east-1',
#       }
#    ]
# }


@click.command()
@click.option(
    '--config', default='config.ini',
    help='Provide the path to the configuration file',
    type=click.Path(exists=True))
def cli(config):
    """Compare instance reservations and running instances for AWS services.

    Args:
        config (str): The path to the configuration file.

    """
    current_config = parse_config(config)
    # global results for all accounts
    results = {
        'ec2_running_instances': {},
        'ec2_reserved_instances': {},
    }
    aws_accounts = current_config['Accounts']

    for aws_account in aws_accounts:
        session = create_boto_session(aws_account)
        results = calculate_ec2_ris(session, results)

    print('\n')
    print('--------------------------------------------------------------')    
    print('[Reserved]:')
    print(results['ec2_reserved_instances'])
    print('\n')
    print('[EC2 instances]:')
    print(results['ec2_running_instances'])
    print('\n')
    print('--------------------------------------------------------------')
    print('--------------------------------------------------------------')
    print('--------------------------------------------------------------')
    print('--------------------------------------------------------------')


    report = {}
    report['EC2'] = report_diffs(
        results['ec2_running_instances'],
        results['ec2_reserved_instances'])
    report_results(current_config, report)




