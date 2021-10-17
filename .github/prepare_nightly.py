import re
from datetime import datetime

# Open setup nightly
with open('setup.py', 'r') as f:
    setup_file=f.read()

#Change scaledown to sd-nightly
setup_file=re.sub(r'name="scaledown"', f'name="sd-nightly"', setup_file)
print(setup_file)

with open('setup.py', 'w') as f:
    f.write(setup_file)

with open('scaledown/__init__.py', 'r') as f:
    init_file=f.read()

version=re.findall(r'__version__=\"([\d\.\w]+)\"', init_file)[0]

now = datetime.utcnow()
now_date = now.strftime("%Y%m%d")

version=f"{version}.dev{now_date}"
print(version)

init_file=re.sub(r'__version__=\"([\d\.\w]+)\"', f'__version__="{version}"', init_file)
print(init_file)

with open('scaledown/__init__.py', 'w') as f:
    f.write(init_file)
