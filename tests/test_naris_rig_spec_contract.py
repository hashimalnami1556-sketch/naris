"""Pure Python contract tests for NARIS's 92-node Ash Wanderer hierarchy.
These are structural tests, not an approval of any rig's rest pose or skinning.
"""
from copy import deepcopy
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'repo_tools'))
from naris_rig_spec_contract import check_armature_contract


def make_spec():
    bones=[{'name':'root','parent':None,'role':'motion_root'}]
    bones += [{'name':f'deform_{i:02d}','parent':'root' if i==0 else f'deform_{i-1:02d}', 'role':'deform'} for i in range(75)]
    bones += [{'name':f'twist_{i:02d}','parent':f'deform_{i:02d}','role':'twist_deform'} for i in range(16)]
    return {'joint_count':92,'bones':bones}


def make_actual(spec):
    return [{'name':r['name'],'parent':r['parent'],'use_deform':r['role']!='motion_root'} for r in spec['bones']]


def test_accepts_92_nodes_91_deforming_root_not_skinning():
    s=make_spec();m=make_actual(s)
    r=check_armature_contract(m,s)
    assert r['contract_match'] is True
    assert r['expected_export_nodes']==92
    assert r['expected_deform_bones']==91
    assert r['observed_deform_bones']==91


def test_rejects_motion_root_set_to_deform():
    s=make_spec();m=make_actual(s);m[0]['use_deform']=True
    r=check_armature_contract(m,s)
    assert not r['contract_match'] and any('deform_flag:root' in x for x in r['issues'])


def test_rejects_missing_node_even_if_some_other_bone_exists():
    s=make_spec();m=make_actual(s);m.pop(4)
    r=check_armature_contract(m,s)
    assert not r['contract_match'] and r['missing_nodes']


def test_rejects_wrong_parent():
    s=make_spec();m=make_actual(s);m[-1]['parent']='root'
    r=check_armature_contract(m,s)
    assert not r['contract_match'] and any('parent:' in x for x in r['issues'])


def test_accepts_nonexported_non_deforming_control_bone():
    s=make_spec();m=make_actual(s)
    m.append({'name':'IK_Hand_Control','parent':'root','use_deform':False})
    r=check_armature_contract(m,s)
    assert r['contract_match'] and r['extra_non_deforming_controls']==['IK_Hand_Control']


def test_rejects_unlisted_deforming_bone():
    s=make_spec();m=make_actual(s)
    m.append({'name':'unregistered_skin_joint','parent':'root','use_deform':True})
    r=check_armature_contract(m,s)
    assert not r['contract_match'] and 'unregistered_skin_joint' in r['unexpected_deforming_bones']


def test_rejects_duplicate_casefold_names():
    s=make_spec();m=make_actual(s)
    m.append({'name':'ROOT','parent':'root','use_deform':False})
    r=check_armature_contract(m,s)
    assert not r['contract_match']


def test_rejects_malformed_role_count_even_if_nodes_match():
    s=make_spec();m=make_actual(s);s['bones'][1]['role']='motion_root'
    r=check_armature_contract(m,s)
    assert not r['contract_match']


def test_rejects_hierarchy_cycle_in_spec():
    s=make_spec();m=make_actual(s)
    s['bones'][0]['parent']=s['bones'][-1]['name'];m[0]['parent']=s['bones'][-1]['name']
    r=check_armature_contract(m,s)
    assert not r['contract_match'] and any('cycle' in x or 'root' in x for x in r['issues'])
