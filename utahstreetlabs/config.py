import json
import subprocess
from pprint import pprint

def parents(config):
    while config.parent:
        yield config.parent
        config = config.parent

def xcproject_to_json(filename):
    output = subprocess.check_output(['plutil', '-convert', 'json', '-o', '-', filename])
    return json.loads(output)

def subdict(pfile, type):
    return dict((k,v) for k,v in pfile['objects'].iteritems() if v['isa'] == type)

def build_configurations(pfile):
    return subdict(pfile, 'XCBuildConfiguration')

def projects(pfile):
    return subdict(pfile, 'PBXProject')

def native_targets(pfile):
    return subdict(pfile, 'PBXNativeTarget')

def configuration_lists(pfile):
    return subdict(pfile, 'XCConfigurationList')

def full_build_settings(parent, lists, configurations):
    list_id = parent['buildConfigurationList']
    config_ids = lists[list_id]['buildConfigurations']
    configs = (configurations[id] for id in config_ids)
    return dict((c['name'], c['buildSettings']) for c in configs)

def intersect_two(d1, d2):
    return dict((k,v) for k,v in d1.iteritems() if k in d2 and d2[k] == v)

def intersect(first, *rest):
    if rest:
        return reduce(intersect_two, rest, first)
    return first

def minus(d1, d2):
    keys = set(d2.iterkeys())
    return dict((k,v) for k,v in d1.iteritems() if k not in keys or d2[k] != v)

def merge(*dicts):
    return dict((k,v) for d in dicts for k,v in d.iteritems())

def partition_project(jsondata):
    return (projects(jsondata).items()[0][1],
        build_configurations(jsondata),
        configuration_lists(jsondata))

def format_setting(key, value):
    # since strings are also iterable, we have to try a little harder
    # to avoid treating them as lists
    string_value = value if str(value) == value else ' '.join(value)
    return '{0} = {1}\n'.format(key, string_value)


def write_file(prefix, settings, include=None):
    with open('{0}.xcconfig'.format(prefix), 'w+') as outfile:
        if include:
            outfile.write('#include "{0}.xcconfig"\n'.format(include))
        outfile.writelines(format_setting(k,v) for k,v in settings.iteritems())

def write_files(common, defaults, targets):
    write_file('Default', common)
    for configuration, values in defaults.iteritems():
        write_file('Default{0}'.format(configuration), values, 'Default')
    for name, configs in targets.iteritems():
        for configuration, values in configs.iteritems():
            write_file('{0}{1}'.format(name, configuration), values,
                'Default{0}'.format(configuration))

def process(filename):
    jsondata = xcproject_to_json(filename)
    project, configurations, lists = partition_project(jsondata)
    project_settings = full_build_settings(project, lists, configurations)
    common = intersect(*project_settings.values())

    target_configs = native_targets(jsondata).values()
    target_settings = [(c['name'], full_build_settings(c, lists, configurations)) for c in target_configs]
    common = merge(common, intersect(*[d for s in target_settings for d in s[1].itervalues()]))

    defaults = dict((k, minus(v, common)) for k,v in project_settings.iteritems())
    targets = {}
    for name, data in target_settings:
        targets.setdefault(name, {})
        for configuration, settings in data.iteritems():
            overrides = minus(settings, merge(defaults[configuration], common))
            targets[name][configuration] = overrides
    write_files(common, defaults, targets)
