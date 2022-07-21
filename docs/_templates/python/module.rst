{% if not obj.display %}
:orphan:

{% endif %}
.. py:module:: {{ obj.name }}
   :noindex:

{% block subpackages %}
{% set visible_submodules = obj.submodules|selectattr("display")|list %}
{% if visible_submodules %}
{{ obj.name }}
======={{ "=" * obj.name|length }}

{% if obj.docstring %}
{{ obj.docstring|prepare_docstring }}
{% endif %}

{% for submodule in visible_submodules %}
{% if submodule.all is not none %}
{% set visible_children = submodule.children|selectattr("short_name", "in", submodule.all)|list %}
{% else %}
{% set visible_children = submodule.children|selectattr("display")|rejectattr("imported")|list %}
{% endif %}
{% if visible_children %}
{% for obj_item in visible_children %}
{{ obj_item.rendered|indent(0) }}
{% endfor %}
{% endif %}
{% endfor %}

{% endif %}
{% endblock %}
