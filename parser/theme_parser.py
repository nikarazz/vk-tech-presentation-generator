from lxml import etree
from zipfile import ZipFile

NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}

def parse_theme(pptx_path: str) -> dict:
    with ZipFile(pptx_path) as z:
        theme_files = [n for n in z.namelist() if 'theme' in n and n.endswith('.xml')]
        if not theme_files:
            return {"clrScheme": {}, "fontScheme": {}}
        with z.open(theme_files[0]) as f:
            tree = etree.parse(f)
    
    clr_scheme = {}
    for child in tree.findall('.//a:clrScheme/*', NS):
        tag = etree.QName(child).localname
        srgb = child.find('a:srgbClr', NS)
        if srgb is not None:
            clr_scheme[tag] = f"#{srgb.get('val')}"
        sysclr = child.find('a:sysClr', NS)
        if sysclr is not None:
            clr_scheme[tag] = f"#{sysclr.get('lastClr', '000000')}"
    
    font_scheme = {}
    major = tree.find('.//a:majorFont/a:latin', NS)
    minor = tree.find('.//a:minorFont/a:latin', NS)
    if major is not None:
        font_scheme['major'] = major.get('typeface')
    if minor is not None:
        font_scheme['minor'] = minor.get('typeface')
    
    return {"clrScheme": clr_scheme, "fontScheme": font_scheme}
