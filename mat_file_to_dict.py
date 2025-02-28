'''
created by: Siddhesh Shinde
location: Troy, MI
date: 09/12/2018
last modified: 09/12/2018
usage: matdata = loadmat(filename)
'''


import scipy.io as sio


__all__ = ['loadmat']


def loadmat(filename):
    '''
    this function should be called instead of direct spio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects

    from: `StackOverflow <http://stackoverflow.com/questions/7008608/scipy-io-loadmat-nested-structures-i-e-dictionaries>`_
    '''
    data = sio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_keys(data)


def _check_keys(ip_dict):
    '''
    checks if entries in dictionary are mat-objects. If yes
    todict is called to change them to nested dictionaries
    '''
    for key in ip_dict:
        if isinstance(ip_dict[key], sio.matlab.mio5_params.mat_struct):
            ip_dict[key] = _todict(ip_dict[key])

    selected_keys = list() # keys to delete from the dict

    for key in ip_dict.keys():
        if key.startswith('__'):
            selected_keys.append(key)

    # deleting selected keys from the dict
    for key in selected_keys:
        if key in ip_dict:
            del ip_dict[key]

    if len( ip_dict.keys() ) == 1:
        for key in ip_dict.keys():
            ip_dict = ip_dict[key]

    return ip_dict


def _todict(matobj):
    '''
    A recursive function which constructs from matobjects nested dictionaries
    '''
    dict = {}
    for strg in matobj._fieldnames:
        elem = matobj.__dict__[strg]
        if isinstance(elem, sio.matlab.mio5_params.mat_struct):
            dict[strg] = _todict(elem)
        else:
            dict[strg] = elem
    return dict
