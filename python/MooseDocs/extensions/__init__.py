import os
from markdown.util import etree
import MooseDocs

def get_collection_items(info_objects, show_hidden=False):
    """
    Returns li html elements for each object in a system.

    Input:
      info_objects: A list of MooseInfoBase objects to collect.
    """
    items = []
    # Alphabetize items as they're passed in
    for info in sorted(info_objects, key=lambda item: item.name):
        if info.hidden and not show_hidden:
            continue
        item = etree.Element('li')
        items.append(item)
        header = etree.SubElement(item, 'div')
        header.set('class', 'collapsible-header')
        header_row = etree.SubElement(header, 'div')
        header_row.set('class', 'row')
        item_name= etree.SubElement(header_row, 'div' )
        item_name.set('class', 'moose-collection-name col l4')
        a = etree.SubElement(item_name, 'a')
        a.text = info.name
        a.set('href', info.markdown)
        if info.description:
            item_desc = etree.SubElement(header_row, 'div')
            item_desc.set('class', 'moose-collection-description hide-on-med-and-down col l8')
            item_desc.text = info.description
            body = etree.SubElement(item, 'div')
            body.set('class', 'collapsible-body')
            body.text = info.description
    return items


def create_collection(name, syntax, action, groups=[], **kwargs):
    """
    Creates subobject collection for a given node from the YAML dump.

    Inputs:
      name: The name of the object/system
      syntax: The dict of MooseApplicationSyntax objects
      action[str]: Name of test function on the MooseApplicationSyntax object to call ('system' or 'object')
      groups[list]: The list of groups to restrict the collection.
    """

    groups = groups if groups else syntax.keys()
    use_header = True if len(groups) > 1 else False

    children = []
    for group in groups:
        if action == 'object':
            items = get_collection_items(syntax[group].objects(name, include_self=False), **kwargs)
        elif action == 'system':
            items = get_collection_items(syntax[group].actions(name, include_self=False), **kwargs)
        else:
            log.error('Invalid action name, must supply "system" or "object".')
            return None

        if items and use_header:
            li = etree.Element('li')
            header = etree.SubElement(li, 'div')
            header.set('class', 'collapsible-header moose-group-header')
            header.text = '{} {}'.format(syntax[group].name(), '{}s'.format(action.title()))
            items.insert(0, header)
        children += items

    collection = None
    if children:
        collection = etree.Element('ul')
        collection.set('class', 'collapsible')
        collection.set('data-collapsible', 'accordion')
        collection.extend(children)

    return collection


def create_object_collection(name, syntax, **kwargs):
    """
    Return html element listing objects.
    """
    return create_collection(name, syntax, 'object', **kwargs)

def create_system_collection(name, syntax, **kwargs):
    """
    Return html element listing systems.
    """
    return create_collection(name, syntax, 'system', **kwargs)

def caption_element(settings):
    """
    Create a caption Element.

    Args:
        settings[dict]: Extension settings.
    """
    counter_name = settings.get('counter', 'unknown').lower()
    class_ = 'moose-{}-caption'.format(counter_name)

    p = etree.Element('p')
    p.set('class', class_)

    if settings['id']:
        h_span = etree.SubElement(p, 'span')
        h_span.set('class', '{}-heading'.format(class_))
        h_span.text = '{} {}: '.format(counter_name.title(), str(MooseDocs.MooseMarkdown.COUNTER[counter_name]))

    if settings['caption']:
        t_span = etree.SubElement(p, 'span')
        t_span.set('class', '{}-text'.format(class_))
        t_span.text = settings['caption']

    return p

def increment_counter(element, settings, counter_name):
    """
    If 'id' is given in the settings add the counter information to the supplied etree.Element and
    increment the global counter.

    Args:
        element[etree.Element]: The element to modify with counter data.
        settings[dict]: The MooseDocs extension settings, if 'id' is valid the counter increments.
        counter_name[str]: The counter name.
    """
    if settings['id']:
        counter_name = counter_name.lower()
        MooseDocs.MooseMarkdown.COUNTER[counter_name] += 1
        element.set('data-moose-count'.format(counter_name), str(MooseDocs.MooseMarkdown.COUNTER[counter_name]))
        element.set('data-moose-count-name', counter_name)
