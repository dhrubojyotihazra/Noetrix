with open(r'c:\Users\HP\Desktop\dhruv\Resume screener\home.full-page.Woblo\home\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
names = re.findall(r'data-framer-name="([^"]+)"', text)
print('Framer names:', list(dict.fromkeys(names)))

# Let's inspect the entire navigation markup
nav_start = text.find('<nav')
nav_end = text.find('</nav>')
if nav_start != -1 and nav_end != -1:
    print('\n=== NAV MARKUP ===')
    print(text[nav_start:nav_end+6])
