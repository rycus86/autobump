import re


def parse_jetbrains_product_version(version):
    # patterns:
    #   2019.2.2 (192.6603.35)
    #   2019.2.2 (192.6603.24 rc)
    #   2019.3 (193.2956.43 eap)

    new_version = re.sub(r'(\S+) \((\S+)( .+)?\)', r'\1', version)
    display_version = new_version
    main_version = re.sub(r'(20[0-9]{2}\.[0-9]+).*', r'\1', new_version)
    build_version = re.sub(r'(\S+) \((\S+)( .+)?\)', r'\2', version)

    modifier = re.sub(r'(\S+) \((\S+)( .+)?\)', r'\3', version).strip()
    if modifier:
        new_version = '%s-%s-%s' % (new_version, modifier, build_version)
    else:
        build_version = new_version

    return new_version, display_version, main_version, build_version
