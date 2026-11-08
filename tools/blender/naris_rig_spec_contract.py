"""Pure-Python structural contract checker for rig *names / hierarchy / deform flags*.

Consumes the source-spec-v1 JSON and an explicit list of observed Blender bones.
It deliberately does NOT accept/reject rest matrices, constraints, weights or Unreal exports.
Exactly 92 specified nodes (1 motion root, 75 deform, 16 twist_deform)
means 91 *deforming* bones, not 92.
"""
from collections import Counter
from pathlib import Path
import json

VALID_ROLES={'motion_root','deform','twist_deform'}


def load_ash_spec(repo_root):
    p=Path(repo_root)/'docs'/'characters'/'char-001'/'ash-wanderer-source-spec-v1.json'
    return json.loads(p.read_text(encoding='utf-8'))


def _casefold_collisions(names):
    c=Counter(str(n).casefold() for n in names)
    return sorted(n for n,k in c.items() if k>1)


def _cycle_nodes(rows):
    by_name={r['name']:r['parent'] for r in rows}
    found=[]
    for name in by_name:
        visited=set();next_node=name
        while next_node is not None and next_node in by_name:
            if next_node in visited:
                found.append(name);break
            visited.add(next_node);next_node=by_name[next_node]
    return sorted(set(found))


def check_armature_contract(observed, spec):
    """Return factual field checks; `contract_match` is NOT a production approval.

    observed: [{'name', 'parent', 'use_deform'}] for ALL armature bones.
    spec: complete source JSON incl bones:[{'name','parent','role'}].
    Unlisted *nondeforming* control bones are allowed in authoring but MUST be excluded
    by the downstream game export filter. Unlisted deforming bones are rejected.
    """
    rows=list(observed);expected=list(spec.get('bones',[]))
    roles=Counter(r.get('role') for r in expected)
    exp={r['name']:r for r in expected};actual={r['name']:r for r in rows}
    issues=[]
    for kind,names in [('source', [x['name'] for x in expected]),('armature', [x['name'] for x in rows])]:
        dup=_casefold_collisions(names)
        if dup:issues.append(f'duplicate_{kind}_names:'+','.join(dup))
    if not expected or len(expected)!=spec.get('joint_count'):
        issues.append('declared_node_count_mismatch')
    if roles['motion_root']!=1:issues.append('motion_root_count_not_one')
    if any(x not in VALID_ROLES for x in roles):issues.append('unknown_source_role')
    if roles['deform']+roles['twist_deform']+roles['motion_root']!=len(expected):
        issues.append('source_role_count_mismatch')
    roots=[r for r in expected if r.get('parent') is None]
    if len(roots)!=1 or roots[0].get('role')!='motion_root':issues.append('source_hierarchy_root_invalid')
    for row in expected:
        if row.get('parent') is not None and row['parent'] not in exp:
            issues.append('source_missing_parent:'+str(row['name']))
    if _cycle_nodes(expected):issues.append('source_cycle')
    missing=sorted(n for n in exp if n not in actual)
    if missing:issues.append('missing_export_nodes:'+','.join(missing))
    for name,source in exp.items():
        node=actual.get(name)
        if node is None:continue
        if node.get('parent')!=source.get('parent'):
            issues.append('parent:'+name)
        should_deform=source['role']!='motion_root'
        if bool(node.get('use_deform'))!=should_deform:
            issues.append('deform_flag:'+name)
    extra_deforming=sorted(n for n,row in actual.items() if n not in exp and bool(row.get('use_deform')))
    extra_controls=sorted(n for n,row in actual.items() if n not in exp and not bool(row.get('use_deform')))
    if extra_deforming:issues.append('unexpected_deforming_bones:'+','.join(extra_deforming))
    actual_deform=sum(bool(row.get('use_deform')) for row in rows)
    return {'contract_match':not issues,'issues':issues,'missing_nodes':missing,
            'unexpected_deforming_bones':extra_deforming,'extra_non_deforming_controls':extra_controls,
            'expected_export_nodes':len(expected),
            'expected_deform_bones':roles['deform']+roles['twist_deform'],
            'expected_motion_roots':roles['motion_root'],
            'observed_armature_bones':len(rows),'observed_deform_bones':actual_deform,
            'limitation':'NAME_PARENT_FLAG_CHECK_ONLY_REST_MATRIX_SKIN_MOTION_ENGINE_PENDING'}
