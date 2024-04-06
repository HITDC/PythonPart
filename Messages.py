# -*- coding: UTF-8 -*-


def init_request(Timestamp, Role, Purpose=None, Info=None):
    dic = {'Timestamp': Timestamp, 'Role': Role, 'Purpose': Purpose, 'Info': Info}
    return dic


def attack_request(Timestamp, action_ID, action_type='Attack'):
    dic = {'action_type': action_type, 'Timestamp': Timestamp, 'action_ID': action_ID}
    return dic


def defence_request(Timestamp, action_ID, action_type='Defence'):
    dic = {'action_type': action_type, 'Timestamp': Timestamp, 'action_ID': action_ID}
    return dic


def sys_info(isExposed: bool, isSucceed: bool):
    dic = {'isExposed': isExposed, 'isSucceed': isSucceed}
    return dic


def init_response(isExposed: bool, isSucceed: bool):
    dic = {'res': "Successfully initialized!", 'isExposed': isExposed, 'isSucceed': isSucceed}
    return dic


def attack_response(Tar, opSucceed: bool, isExposed: bool, isSucceed: bool, Reason=None):
    dic = {'tar': Tar,
           'opSucceed': opSucceed,
           'res': None,
           'isExposed': isExposed,
           'isSucceed': isSucceed,
           'Reason': Reason}
    if opSucceed:
        dic['res'] = "Successfully attacked!"
    return dic


def defence_response(Tar, opSucceed: bool, isExposed: bool, isSucceed: bool, Reason=None):
    dic = {'tar': Tar,
           'opSucceed': opSucceed,
           'res': None,
           'isExposed': isExposed,
           'isSucceed': isSucceed,
           'Reason': Reason}
    if opSucceed:
        dic['res'] = "Operated successfully!"
    return dic

