import re

with open('backend/core/PhantomInfrastructure.tsx', 'r') as f:
    content = f.read()

# Replace .text() with .arrayBuffer() to support binary data cache
content = content.replace('const cache = new Map<string, { data: string; timestamp: number; headers: Headers }>();',
                          'const cache = new Map<string, { data: ArrayBuffer; timestamp: number; headers: Headers }>();')

content = content.replace('cacheClone.text().then(text => {', 'cacheClone.arrayBuffer().then(buffer => {')
content = content.replace('data: text,', 'data: buffer,')

with open('backend/core/PhantomInfrastructure.tsx', 'w') as f:
    f.write(content)
