import jinja2
from ec2_reservation_check.aws import instance_ids
from ec2_reservation_check.aws import reserve_expiry
from ec2_reservation_check.aws import tags
from ec2_reservation_check.templates import report_template


def report_results(config, results):
    report_text = jinja2.Template(report_template).render(
        report=results, instance_ids=instance_ids,
        reserve_expiry=reserve_expiry,
        tags=tags
    )
    print(report_text)
