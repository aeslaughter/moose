{% macro define(item, default=False) -%}
{% if hasTemplateItem(item) %}
  {{getTemplateItem(item)}}
{% elif default %}
  {{ caller() }}
{% else %}
<div class="admonition error">
  <div class="admonition-title">
    <p style="margin-bottom:8px;">Missing Template Item: "{{item}}"
    <a class="waves-effect waves-light btn-floating red" data-target="moose-modal-help-data-0" style="float:right;">
      <i class="material-icons">help</i>
    </a>
    </p>
  </div>
  <div class="admonition-message" markdown="1">
    {{ caller() }}
  </div>
  <div class="modal" id="moose-modal-help-data-0">
    <div class="modal-content">
      <h3>Adding Markdown for "{{item}}" Item</h3>
      <p>To add content for the "{{item}}", simply add a block similar to was is shown below in the markdown file.</p>
      <pre><code class="language-text">
!SQA-template-item {{item}}
The content placed here should be valid markdown that will replace the template description.
!END-template-item
      </code></pre>
    </div>
  </div>
</div>
{% endif %}
{%- endmacro %}
