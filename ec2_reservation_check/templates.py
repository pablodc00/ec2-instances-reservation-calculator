report_template = """
##############################################################
####            Reserved EC2 Instances Report            #####
##############################################################
{% for service in report %}
Below is the report on {{ service }} reserved instances:
    {%- if report[service]['unused_reservations'] -%}
      {%- for type, count in report[service]['unused_reservations'].items() %}
UNUSED RESERVATION!\t[{{ count }}]\t{{ type }}
      {%- endfor %}
    {%- else %}
You have no unused {{ service }} reservations.
    {%- endif %}
    {%- if report[service]['unreserved_instances'] %}
--------------------------------------------------------------
--------------------------------------------------------------
--------------------------------------------------------------
--------------------------------------------------------------
Status\t\tCount\tType\t\tInstances\t\t\tComment
      {%- for type, count in report[service]['unreserved_instances'].items() %}
NOT RESERVED!\t[{{ count }}]\t{{ type }}
        {% if instance_ids %}
          {%- for instanceid in instance_ids[type] %}
            \t\t\t\t{{ instanceid }} {%- if instanceid in tags.keys() %}  \t\t ---- Cloud Bill Review Comment: {{ tags[instanceid] }} {% endif %}
          {%- endfor %}
        {% endif %}
      {%- endfor %}
    {%- else %}
You have no unreserved {{ service }} instances.
    {%- endif %}
({{ report[service]['qty_running_instances'] }}) running on-demand {{ service }} instances
({{ report[service]['qty_reserved_instances'] }}) {{ service }} reservations
({{ report[service]['qty_unreserved_instances'] }}) Unreserved {{ service }} reservations
--------------------------------------------------
{% endfor %}
"""
