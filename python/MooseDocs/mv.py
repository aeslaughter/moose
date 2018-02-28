import os
import subprocess
import re

import anytree

import MooseDocs
from MooseDocs.tree import syntax, app_syntax




def update_content(filename):
    with open(filename, 'r') as fid:
        content = fid.read()

    content = re.sub(r'^(#+.*?)$', r'\1\n', content, flags=re.MULTILINE)
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

def update(node, group, prefix, old_dir, new_dir):

    new = None; old = None
    if group in node.groups:
        md = node.markdown(prefix)

        if md.endswith('index.md') and group != 'Framework' and 'Framework' in node.groups:
            return

        new = os.path.join(MooseDocs.MOOSE_DIR, new_dir, md)
        if isinstance(node, syntax.SyntaxNode):
            old = os.path.join(MooseDocs.MOOSE_DIR, old_dir, md)

        elif isinstance(node, syntax.ObjectNode):
            x = md.split('/')
            x.insert(-1, group.lower())
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

    exe = os.path.join(MooseDocs.MOOSE_DIR, 'modules', 'combined')
    root = app_syntax(exe)

    prefix = 'documentation/systems'
    old_dir = 'docs/content'

    locations = dict()
    locations['XFEM'] = 'modules/xfem/doc/content'
    locations['NavierStokes'] = 'modules/navier_stokes/doc/content'
    locations['TensorMechanics'] = 'modules/tensor_mechanics/doc/content'
    locations['PhaseField'] = 'modules/phase_field/doc/content'
    locations['Rdg'] = 'modules/rdg/doc/content'
    locations['Contact'] = 'modules/contact/doc/content'
    locations['SolidMechanics'] = 'modules/solid_mechanics/doc/content'
    locations['HeatConduction'] = 'modules/heat_conduction/doc/content'
    locations['Framework'] = 'framework/doc/content'
    locations['StochasticTools'] = 'modules/stochastic_tools/doc/content'
    locations['Misc'] = 'modules/misc/doc/content'
    locations['FluidProperties'] = 'modules/fluid_properties/doc/content'
    locations['ChemicalReactions'] = 'modules/chemical_reactions/doc/content'
    locations['LevelSet'] = 'modules/level_set/doc/content'
    locations['PorousFlow'] = 'modules/porous_flow/doc/content'
    locations['Richards'] = 'modules/richards/doc/content'
    for group in root.groups:
        new_dir = locations[group]
        for node in anytree.PreOrderIter(root):
            update(node, group, prefix, old_dir, new_dir)
