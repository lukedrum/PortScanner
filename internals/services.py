import importlib
import os

# check if mod exposes proper interface
def _is_module_compatible(mod, module_name, debug=False):
    desc = mod.SERVICE_DESC

    if not isinstance(desc, dict):
        if debug:
            print('MOD LOADER - omitting module ' + module_name + ' - SERVICE_DESC is not a dictionary')
        return False

    if not 'name' in desc or not isinstance(desc['name'], str):
        if debug:
            print('MOD LOADER - omitting module ' + module_name + ' - missing "name" attribute')
        return False

    if not 'ConnChecker' in mod.__dict__ or not isinstance(mod.ConnChecker, type):
        if debug:
            print('MOD LOADER - omitting module ' + module_name + ' - missing class ConnChecker')
        return False

    return True

def _get_module_candidates(debug=False):
    module_names = os.listdir('./service_modules')

    module_names.remove('__pycache__') # ugly fix to not include pycache

    for name in module_names:
        path = './service_modules/' + name

        if os.path.isdir(path) or not path.endswith('.py'): # only include actual python files
            module_names.remove(name)

    module_names = [ 'service_modules.' + name[:-3] for name in module_names ] # trim .py, append subdir

    return module_names

def load(debug=False):
    services = {}

    module_names = _get_module_candidates(debug)

    for module_name in module_names:
        mod = importlib.import_module(module_name)
        desc = mod.SERVICE_DESC
        
        if not _is_module_compatible(mod, module_name, debug):
            continue

        if desc['name'] in services:
            if debug:
                print('MOD LOADER - omitting module ' + module_name + ' - service name "' + desc['name'] + '" already occupied by another module')
            continue

        services[desc['name']] = mod
        
        if debug:
            print('MOD LOADER - module ' + module_name + ' added to services{}')

    return services

def map_ports(services, debug=False):
    port_map = {}

    for name in services:
        mod = services[name]
        desc = mod.SERVICE_DESC

        if 'default_ports' in desc:
            ports = desc['default_ports']

            for p in ports:
                if not p in port_map:
                    port_map[p] = [{ 'ssl': False, 'service_name': name }]
                else:
                    port_map[p].append({ 'ssl': False, 'service_name': name })
        elif debug:
            print('PORT MAPPER - no "default_ports" provided in service ' + name + ' - no mapping created')

        if 'default_ports_ssl' in desc:
            ports = desc['default_ports_ssl']
            
            for p in ports:
                if not p in port_map:
                    port_map[p] = [{ 'ssl': True, 'service_name': name }]
                else:
                    port_map[p].append({ 'ssl': True, 'service_name': name })
            print('PORT MAPPER - no "default_ports_ssl" provided in service ' + name + ' - no ssl mapping created')

    return port_map
