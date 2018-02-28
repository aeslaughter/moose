import os
import subprocess
import re

import anytree

import MooseDocs
from MooseDocs.tree import syntax, app_syntax




def update_content(filename):
    with open(filename, 'r') as fid:
        content = fid.read()

    content = re.sub(r'^(#+.*?)$(?=\n^\S)', r'\1\n', content, flags=re.MULTILINE)
    content = re.sub(r'^!syntax objects (\S+)', r'!syntax list \1 objects=True actions=False subsystems=False', content, flags=re.MULTILINE)
    content = re.sub(r'^!syntax actions (\S+)', r'!syntax list \1 objects=False actions=True subsystems=False', content, flags=re.MULTILINE)
    content = re.sub(r'^!syntax subsystems (\S+)', r'!syntax list \1 objects=False actions=False subsystems=True', content, flags=re.MULTILINE)
  #  content = re.sub(r'^!syntax complete', r'!syntax list', content, flags=re.MULTILINE)
    content = re.sub(r'^!listing\s*(.*?) *label=\w+ *(.*?)$', r'!listing \1 \2', content, flags=re.MULTILINE)
    content = re.sub(r'^!syntax list\s*(.*?) *title=\w+ *(.*?)$', r'!syntax list \1 \2', content, flags=re.MULTILINE)
    content = re.sub(r'suffix=(\S+)', 'footer=\1', content)
    content = re.sub(r'include_end=(\S+)', 'include-end=\1', content)
    content = re.sub(r'\\(cite|citet|citep)\{(.*?)\}', r'[\1:\2]', content)
    content = re.sub(r'\\ref\{(.*?)\}', r'[\1]', content)

    with open(filename, 'w') as fid:
        content = fid.write(content)

def update(node, group, group_dir_name, prefix, old_dir, new_dir):

    new = None; old = None
    if group in node.groups:
        md = node.markdown(prefix)

        if md.endswith('index.md') and (group != 'Framework') and ('Framework' in node.groups):
            return

        new = os.path.join(MooseDocs.MOOSE_DIR, new_dir, md)
        if isinstance(node, syntax.SyntaxNode):
            old = os.path.join(MooseDocs.MOOSE_DIR, old_dir, md)

        elif isinstance(node, syntax.ObjectNode):
            x = md.split('/')
            x.insert(-1, group_dir_name)
            old = os.path.join(MooseDocs.MOOSE_DIR, old_dir, *x)

        if os.path.exists(old):
            loc = os.path.dirname(new)
            if not os.path.exists(loc):
                os.makedirs(loc)
            print "{}:\n    OLD: {}\n    NEW: {}\n".format(node.name, old, new)

            subprocess.call(['git', 'mv', old, new])
        #subprocess.call(['cp', old, new])

        #if os.path.exists(old):
        #    update_content(new)

if __name__ == '__main__':

    """
    exe = os.path.join(MooseDocs.MOOSE_DIR, 'modules', 'combined')
    root = app_syntax(exe)

    prefix = 'documentation/systems'
    old_dir = 'docs/content'

    locations = dict()
    locations['XFEM'] = ('xfem', 'modules/xfem/doc/content')
    locations['NavierStokes'] = ('navier_stokes', 'modules/navier_stokes/doc/content')
    locations['TensorMechanics'] = ('tensor_mechanics', 'modules/tensor_mechanics/doc/content')
    locations['PhaseField'] = ('phase_field', 'modules/phase_field/doc/content')
    locations['Rdg'] = ('rdg', 'modules/rdg/doc/content')
    locations['Contact'] = ('contact', 'modules/contact/doc/content')
    locations['SolidMechanics'] = ('solid_mechanics', 'modules/solid_mechanics/doc/content')
    locations['HeatConduction'] = ('heat_conduction', 'modules/heat_conduction/doc/content')
    locations['Framework'] = ('framework', 'framework/doc/content')
    locations['StochasticTools'] = ('stochastic_tools', 'modules/stochastic_tools/doc/content')
    locations['Misc'] = ('misc', 'modules/misc/doc/content')
    locations['FluidProperties'] = ('fluid_properties', 'modules/fluid_properties/doc/content')
    locations['ChemicalReactions'] = ('chemical_reactions', 'modules/chemical_reactions/doc/content')
    locations['LevelSet'] = ('level_set', 'modules/level_set/doc/content')
    locations['PorousFlow'] = ('porous_flow', 'modules/porous_flow/doc/content')
    locations['Richards'] = ('richards', 'modules/richards/doc/content')
    for group in root.groups:
        new_dir = locations[group][1]
        group_dir_name = locations[group][0]
        for node in anytree.PreOrderIter(root):
            update(node, group, group_dir_name, prefix, old_dir, new_dir)
    """

    for root, dirs, files in os.walk(MooseDocs.MOOSE_DIR):
        for name in files:
            if name.endswith('.md'):
                filename = os.path.join(root, name)
                print 'Update:', filename
                update_content(filename)
