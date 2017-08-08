{% macro define(item, default=False) -%}
{% if hasTemplateItem(item) %}
  {{getTemplateItem(item)}}
{% elif default %}
  {{ caller() }}
{% else %}
  {{ createHelpElement(item) }}
  <div class="moose-sqa-template-item-description">
  {{ caller() }}
  </div>
{% endif %}
{%- endmacro %}
