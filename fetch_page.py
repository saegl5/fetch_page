from playwright.sync_api import sync_playwright
import re
import os
import sys

if len(sys.argv) < 2:
    print("Usage: python3 fetch_page.py <url>")
    sys.exit(1)

URL = sys.argv[1]
from urllib.parse import urlparse
parsed = urlparse(URL)
BASE_URL = f"{parsed.scheme}://{parsed.netloc}"
OUTPUT_DIR = "output"
IMAGE_DIR = os.path.join(OUTPUT_DIR, "images")
os.makedirs(IMAGE_DIR, exist_ok=True)

def html_to_markdown(el_handle, page):
    return page.evaluate(r"""(el) => {
        function convert(el) {
            const tag = el.tagName?.toLowerCase();
            const children = () => Array.from(el.childNodes).map(convert).join('');

            if (el.nodeType === 3) return el.textContent;
            if (!tag) return '';

            if (tag === 'a') {
                const href = el.getAttribute('href');
                const img = el.querySelector('img');
                if (img) {
                    const src = img.getAttribute('src') || '';
                    const alt = img.getAttribute('alt') || '';
                    return `\n![${alt}](${src})\n`;
                }
                const text = el.innerText.trim();
                return href && text ? `[${text}](${href})` : text;
            }
            if (tag === 'img') {
                const src = el.getAttribute('src') || '';
                const alt = el.getAttribute('alt') || '';
                return `\n![${alt}](${src})\n`;
            }
            if (['h1','h2','h3','h4'].includes(tag)) {
                const level = '#'.repeat(parseInt(tag[1]));
                return `\n${level} ${el.innerText.trim()}\n`;
            }
            if (tag === 'table') {
                const rows = Array.from(el.querySelectorAll('tr'));
                if (!rows.length) return '';
                const toRow = cells => '| ' + cells.map(c => convert(c).replace(/\n/g, ' ').trim()).join(' | ') + ' |';
                const header = rows[0];
                const headerCells = Array.from(header.querySelectorAll('th, td'));
                const separator = '| ' + headerCells.map(() => '---').join(' | ') + ' |';
                const lines = [toRow(headerCells), separator];
                for (const row of rows.slice(1)) {
                    lines.push(toRow(Array.from(row.querySelectorAll('td'))));
                }
                return '\n' + lines.join('\n') + '\n';
            }
            if (['thead','tbody','tr','th','td'].includes(tag)) return children();
            if (tag === 'p') { const inner = children(); return inner.trim().startsWith('[') && !inner.trim().includes('\n') ? `\n${inner.trim()}` : `\n${inner}\n`; }
            if (tag === 'li') return `\n- ${children()}`;
            if (tag === 'br') return '\n';
            if (tag === 'strong' || tag === 'b') return `**${children()}**`;
            if (tag === 'em' || tag === 'i')     return `*${children()}*`;
            if (tag === 'code') return '`' + el.innerText + '`';
            if (tag === 'pre')  return `\n\`\`\`\n${el.innerText}\n\`\`\`\n`;
            if (['script','style','nav','footer','aside'].includes(tag)) return '';

            return children();
        }
        return convert(el);
    }""", el_handle)

def download_images(markdown, context, article_image_dir, safe_title):
    img_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    counter = 0
    encoded_safe_title = safe_title.replace(' ', '%20')

    def replace_img(match):
        nonlocal counter
        alt, src = match.group(1), match.group(2)
        if src.startswith('//'):
            src = 'https:' + src
        elif src.startswith('/'):
            src = BASE_URL + src
        counter += 1
        try:
            response = context.request.get(src)
            ct = response.headers.get('content-type', '')
            ext = 'jpg' if 'jpeg' in ct or 'jpg' in ct else 'gif' if 'gif' in ct else 'webp' if 'webp' in ct else 'png'
            filename = f"image_{counter:02d}.{ext}"
            with open(os.path.join(article_image_dir, filename), 'wb') as f:
                f.write(response.body())
            print(f"  Downloaded: {filename}")
            return f'![{alt}](images/{encoded_safe_title}/{filename})'
        except Exception as e:
            print(f"  Error: {e}")
            return match.group(0)

    return img_pattern.sub(replace_img, markdown)

def clean(markdown):
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    # Collapse blank lines between bare links (run twice for both sides)
    link = r'\[.+?\]\(.+?\)'
    markdown = re.sub(rf'({link})\n\n({link})', r'\1\n\2', markdown)
    markdown = re.sub(rf'({link})\n\n({link})', r'\1\n\2', markdown)
    return markdown.strip()

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    page.goto(URL)
    page.wait_for_load_state("networkidle")

    # Grab title and metadata
    meta = page.evaluate("""() => ({
        title:      (document.querySelector('h1') || {}).innerText || '',
        lastUpdated:(document.querySelector('[class*="date"]') || {}).innerText || '',
    })""")

    el = page.query_selector('.article__content')
    markdown = html_to_markdown(el, page)
    markdown = clean(markdown)

    # Prepend title and metadata
    header = f"# {meta['title']}\n"
    if meta['lastUpdated']:
        header += f"_{meta['lastUpdated']}_\n"
    markdown = header + '\n' + markdown

    safe_title = re.sub(r'[^\w\s-]', '', meta['title']).strip()
    out_path = os.path.join(OUTPUT_DIR, f"{safe_title}.md")
    article_image_dir = os.path.join(IMAGE_DIR, safe_title)
    os.makedirs(article_image_dir, exist_ok=True)

    print("Downloading images...")
    markdown = download_images(markdown, context, article_image_dir, safe_title)
    with open(out_path, "w") as f:
        f.write(markdown)

    print(f"\nSaved to {out_path}")
    browser.close()
