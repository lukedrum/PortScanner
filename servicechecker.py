import socket
import importlib
import os

HOST = '10.11.12.1'
PORT = 21

if __name__ == '__main__':
    module_names = os.listdir('./service_modules')

    module_names.remove('__pycache__') # ugly fix

    for name in module_names:
        path = './service_modules/' + name

        if os.path.isdir(path) or not path.endswith('.py'):
            module_names.remove(name)

    module_names = [ 'service_modules.' + name[:-3] for name in module_names ] # trim .py, append subdir

    port_map = {}
    services = {}

    for module_name in module_names:
        mod = importlib.import_module(module_name)
        
        desc = mod.SERVICE_DESC

        if not 'name' in desc:
            print('MOD LOADER - omitting module ' + module_name + ' - missing "name" attribute')
            break

        if desc['name'] in services:
            print('MOD LOADER - omitting module ' + module_name + ' - service name "' + desc['name'] + '" already occupied by another module')
            break

        if not 'ConnChecker' in mod.__dict__ or not isinstance(mod.ConnChecker, type):
            print('MOD LOADER - omitting module ' + module_name + ' - missing class ConnChecker')
            break

        services[desc['name']] = mod

        if not 'default_ports' in desc:
            print('MOD LOADER - module ' + module_name + ' loaded, but no "default_ports" provided - no mapping created')
        else:
            ports = desc['default_ports']

            for p in ports:
                if not p in port_map:
                    port_map[p] = [{ 'ssl': False, 'service_name': desc['name'] }]
                else:
                    port_map[p].append({ 'ssl': False, 'service_name': desc['name'] })

        if not 'default_ports_ssl' in desc:
            print('MOD LOADER - module ' + module_name + ' loaded, but no "default_ports_ssl" provided - no mapping created')
        else:
            ports = desc['default_ports_ssl']
            
            for p in ports:
                if not p in port_map:
                    port_map[p] = [{ 'ssl': True, 'service_name': desc['name'] }]
                else:
                    port_map[p].append({ 'ssl': True, 'service_name': desc['name'] })

    if PORT in port_map:
        for mapping in port_map[PORT]:
            if not mapping['ssl']:
                service_name = mapping['service_name']
                mod = services[service_name]

    s = socket.socket()
    s.connect((HOST, PORT))

    conn = mod.ConnChecker(s)

    if not conn.is_valid():
        print("it's not " + service_name)
    else:
        print("it's " + service_name)
        print('Info string: "' + conn.get_info_string() + '"')
    


