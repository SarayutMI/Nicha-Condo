"""Regenerate static pages after editing assets/properties.json.
Source copy: Condo_Website_Content.docx, matched against existing listing names.
Run: python3 scripts/generate-site.py
The HTML includes all content so it works without JavaScript.
"""
from pathlib import Path
from urllib.parse import quote
import html,json,re
root=Path(__file__).resolve().parent.parent
listings=json.loads((root/'assets/properties.json').read_text())
def shell(title,desc,body,id=None):
    return '<!doctype html>\n<html lang="th">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>'+html.escape(title)+'</title>\n<meta name="description" content="'+html.escape(desc,quote=True)+'">\n<meta name="theme-color" content="#102b35">\n<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">\n<link rel="stylesheet" href="assets/site.css">\n<script src="assets/site.js" defer></script>\n</head>\n<body'+(' data-property-id="'+str(id)+'"' if id else '')+'>\n<a class="skip" href="#main">ข้ามไปเนื้อหา</a>\n<header class="header"><a class="brand" href="index.html">NICHA<span>CONDO · FIND YOUR PLACE</span></a><nav aria-label="เมนูหลัก"><a href="index.html#properties">เลือกที่พัก</a><a href="#contact">ติดต่อเรา</a><a class="nav-call" href="tel:0863429855">086 342 9855</a></nav></header>\n'+body+'\n<footer class="footer"><a class="brand" href="index.html">NICHA CONDO</a><p>พื้นที่ที่ใช่ สำหรับชีวิตของคุณ</p><a href="tel:0863429855">โทร 086 342 9855</a><span>© '+str(2026)+' NICHA CONDO</span></footer>\n<dialog id="lightbox" aria-label="ภาพขยาย"><button class="lightbox-close" aria-label="ปิดภาพ">✕</button><div class="lightbox-stage"><button type="button" class="lightbox-prev" aria-label="ภาพก่อนหน้า">‹</button><img alt=""><button type="button" class="lightbox-next" aria-label="ภาพถัดไป">›</button></div><p></p><a class="lightbox-source" hidden target="_blank" rel="noopener">ดูแหล่งที่มาภาพ ↗</a></dialog>\n</body>\n</html>\n'
CATEGORIES = {'building':'อาคารและบรรยากาศ','facilities':'ส่วนกลาง','interior':'ห้องและพื้นที่ภายใน','plan':'ผังและแผนที่'}
SOURCE_NAMES = {'propertyhub.in.th':'PropertyHub','www.noblehome.com':'Noble Development','www.lpn.co.th':'LPN','www.coloursdevelopment.com':'Colours Development','copacabanagroup.com':'Copacabana Group','secretgardencondo.com':'Secret Garden','embassypattaya.com':'Embassy Pattaya','www.homenayoo.com':'HOMENAYOO','beverlymountainbay.com':'Beverly Mountain Bay','www.beverlymountainbayhotel.com':'Beverly Mountain Bay Hotel'}
SOURCE_NAMES['sarayutmi.github.io'] = 'เว็บไซต์ที่พัก NICHA CONDO'

def image_info(project, image):
    details=dict(project.get('imageDetails',{}).get(image,{}))
    if not details:
        name=image.lower()
        if any(word in name for word in ['roomplan','planroom','room-plan']):category='plan'
        elif any(word in name for word in ['bedroom','bathroom','living','kitchen','toilet','room','table','tv','barcony']):category='interior'
        elif any(word in name for word in ['pool','fitness','garden','yard','space','lobby','facility','cowork']):category='facilities'
        else:category='building'
        details={'category':category,'type':'ผังโครงการ / ผังห้อง' if category=='plan' else 'ภาพจำลองโครงการ' if project['status']=='planning' else 'ภาพประกอบโครงการ','thumbnail':image}
    return details

def render_gallery(project, section=None):
    from urllib.parse import urlsplit
    images=project['images'];details=[image_info(project,image) for image in images]
    available={item['category'] for item in details}
    filters='<button type="button" class="filter active" data-gallery-filter="all" aria-pressed="true">ทุกภาพ</button>'
    filters+=''.join('<button type="button" class="filter" data-gallery-filter="'+key+'" aria-pressed="false">'+label+'</button>' for key,label in CATEGORIES.items() if key in available)
    cards=[]
    for number,(image,item) in enumerate(zip(images,details),1):
        kind=item['type'];category=item['category'];source=item.get('sourcePage','')
        label=kind+' · '+project['name']+' · ภาพ '+str(number)
        credit=''
        if source:
            host=urlsplit(source).netloc
            credit='<a class="photo-credit" href="'+html.escape(source,quote=True)+'" target="_blank" rel="noopener">ที่มา: '+html.escape(SOURCE_NAMES.get(host,host))+' ↗</a>'
        cards.append('<figure class="gallery-card" data-photo-category="'+category+'"><button class="gallery-image" data-full-image="'+html.escape(image,quote=True)+'" data-source-url="'+html.escape(source,quote=True)+'" aria-label="ขยาย '+html.escape(label,quote=True)+'"><img loading="lazy" decoding="async" src="'+html.escape(item.get('thumbnail',image),quote=True)+'" alt="'+html.escape(label,quote=True)+'"></button><figcaption><span>'+html.escape(kind)+'</span>'+credit+'</figcaption></figure>')
    if section:
        section_id, eyebrow, title, intro = section
        plan = section_id == 'floor-plan'
        single_plan = plan and len(images) == 1
        summary = '<div class="photo-section-heading"><div><p class="eyebrow">'+eyebrow+'</p><h2 id="'+section_id+'-title">'+title+'</h2><p class="muted">'+intro+'</p></div><span class="photo-total">'+str(len(images))+' ภาพ</span></div>'
        note = '<aside class="plan-notes"><span class="detail-tag">ROOM LAYOUT</span><h3>มองเห็นพื้นที่<br>ก่อนเข้าชมห้อง</h3><p>ดูตำแหน่งห้องนอน ห้องน้ำ และพื้นที่นั่งเล่นจากแปลนที่ผู้ดูแลจัดเตรียมไว้</p><a class="text-link" href="#room-photos">ชมรูปห้องพักต่อ ↓</a></aside>' if single_plan else ''
        return '<section id="'+section_id+'" class="section photo-section '+('pale plan-section' if plan else 'pale' if section_id == 'more-photos' else '')+'" data-gallery data-gallery-limit="'+('1' if single_plan else '2' if plan else '6')+'" aria-labelledby="'+section_id+'-title">'+summary+'<p class="gallery-count muted" aria-live="polite">ทั้งหมด '+str(len(images))+' ภาพ</p><div class="'+('plan-layout' if single_plan else 'plan-collection' if plan else 'photo-layout')+'"><div class="gallery">'+''.join(cards)+'</div>'+note+'</div><button type="button" class="button gallery-more" data-gallery-more hidden>ดูภาพทั้งหมด</button></section>'
    return '<section id="gallery" class="section pale" data-gallery><p class="eyebrow">A CLOSER LOOK</p><h2>ชมโครงการให้ครบทุกมุม</h2><p class="muted">รวมภาพโครงการ ส่วนกลาง ภาพห้องตัวอย่าง และผังที่มีให้ชม ภาพจากเว็บไซต์โครงการอาจเป็นภาพจำลองหรือห้องตัวอย่าง กรุณาขอภาพห้องที่สนใจจากผู้ดูแลเพื่อยืนยันวิว เฟอร์นิเจอร์ และสภาพห้องก่อนนัดชม</p><div class="filters gallery-filters" data-gallery-controls hidden role="group" aria-label="เลือกประเภทภาพ">'+filters+'</div><p class="gallery-count muted" aria-live="polite">ทั้งหมด '+str(len(images))+' ภาพ</p><div class="gallery">'+''.join(cards)+'</div><button type="button" class="button gallery-more" data-gallery-more hidden>ดูภาพทั้งหมด</button></section>'

def render_location_map(project):
    name = html.escape(project['name'], quote=True)
    query = quote(project.get('mapQuery', project['name'] + ' ' + project['region']))
    embed = html.escape(project.get('mapEmbedUrl', 'https://maps.google.com/maps?q='+query+'&z=16&output=embed'), quote=True)
    directions = 'https://www.google.com/maps/dir/?api=1&amp;destination='+query
    caption = html.escape(project.get('mapCaption', project['name'] + ' · ' + project['region']))
    return '<div class="location-map"><iframe title="ตำแหน่ง '+name+' บน Google Maps" src="'+embed+'" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe><div class="map-caption"><span>'+caption+'</span><a class="text-link" href="'+directions+'" target="_blank" rel="noopener">เปิดเส้นทางใน Google Maps ↗</a></div></div>'



def nearby_icon(kind):
    paths = {
        'education': '<path d="m2 9 10-6 10 6-10 6ZM6 12v6q6 5 12 0v-6M22 9v8"/>',
        'transit': '<rect x="5" y="2" width="14" height="16" rx="3"/><path d="M5 10h14M8 6h8M8 21l2-3m6 3-2-3M8 14h1m6 0h1"/>',
        'attraction': '<path d="m3 9 9-6 9 6ZM5 10v9m5-9v9m4-9v9m5-9v9M3 21h18"/>',
        'beach': '<circle cx="17" cy="6" r="3"/><path d="M2 15q3-3 6 0t6 0t6 0M2 20q3-3 6 0t6 0t6 0M3 8l5-5 5 5M8 3v9"/>',
        'nightlife': '<path d="m12 2 2.8 6.2L22 11l-7.2 2.8L12 21l-2.8-7.2L2 11l7.2-2.8ZM20 2v4m-2-2h4"/>',
        'shopping': '<path d="M5 7h14l2 14H3ZM8 8V6a4 4 0 0 1 8 0v2"/>',
        'hospital': '<path d="M8 3h8v5h5v8h-5v5H8v-5H3V8h5Z"/>',
        'driving': '<path d="m5 7 2-4h10l2 4 2 3v8H3v-8ZM3 10h18M6 14h2m8 0h2M6 18v3m12-3v3"/>',
        'walking': '<circle cx="13" cy="3" r="2"/><path d="m8 21 3-7-2-4 4-3 3 5 4 1M4 12l3-4 4-1m2 7 4 7"/>',
    }
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+paths[kind]+'</svg>'


def render_nearby_metric(place, guide):
    if place.get('minutes') is not None:
        return '<span class="nearby-time"><small>ประมาณ</small><strong>'+str(place['minutes'])+'</strong> นาที</span>'
    if place.get('distanceMeters') is not None:
        metres = place['distanceMeters']
        value, unit = (format(metres / 1000, 'g'), 'กม.') if metres >= 1000 else (format(metres, 'g'), 'ม.')
        basis = place.get('distanceBasis', guide.get('distanceBasis', 'published'))
        label = 'เส้นตรงโดยประมาณ' if basis == 'straight-line' else 'ระยะทางโดยประมาณ'
        return '<span class="nearby-time"><small>'+label+'</small><strong>'+value+'</strong> '+unit+'</span>'
    return '<span class="nearby-unconfirmed">ดูระยะทาง<br>ใน Google Maps</span>'


def render_nearby_guide(project):
    guide = project.get('nearbyGuide', {})
    places = guide.get('places', [])
    heading = '<div class="nearby-heading"><div><p class="eyebrow">YOUR NEIGHBOURHOOD</p><h3 id="nearby-title">จากบ้าน ไปจุดหมายใกล้คุณ</h3><p>สำรวจสถานที่รอบที่พัก เลือกจุดหมายแล้วเปิดเส้นทางใน Google Maps</p></div>'
    if not places:
        return '<section id="nearby-guide" class="nearby-guide nearby-pending" aria-labelledby="nearby-title">'+heading+'</div><div class="nearby-pending-content"><span class="nearby-pending-icon">'+nearby_icon('transit')+'</span><div><h4>วางแผนการเดินทางรอบที่พัก</h4><p>ติดต่อผู้ดูแลเพื่อยืนยันตำแหน่งของ '+html.escape(project['name'])+' และขอข้อมูลสถานที่ใกล้เคียง</p><a class="text-link" href="#contact">ขอพิกัดและข้อมูลการเดินทาง ↗</a></div></div></section>'
    origin = quote(project.get('mapQuery', project['name']+' '+project['region']))
    cards = []
    for number, place in enumerate(places, 1):
        destination = quote(place['mapQuery'])
        mode = place['mode']
        route = 'https://www.google.com/maps/dir/?api=1&amp;origin='+origin+'&amp;destination='+destination+'&amp;travelmode='+mode
        mode_label = 'เดิน' if mode == 'walking' else 'ขับรถ'
        label = 'เปิดเส้นทางจาก '+project['name']+' ไป '+place['name']+' ใน Google Maps'
        cards.append('<a class="nearby-stop nearby-stop-'+str(number)+' nearby-'+place['kind']+'" href="'+route+'" target="_blank" rel="noopener" aria-label="'+html.escape(label,quote=True)+'"><div class="nearby-stop-top"><span class="nearby-icon">'+nearby_icon(place['kind'])+'</span><span class="nearby-mode">'+nearby_icon(mode)+mode_label+'</span></div><h4>'+html.escape(place['name'])+'</h4><p>'+html.escape(place['description'])+'</p><div class="nearby-stop-bottom">'+render_nearby_metric(place,guide)+'<span class="nearby-go">ดูเส้นทาง ↗</span></div></a>')
    name = html.escape(project['name'])
    region = html.escape(guide.get('areaLabel', project['region']))
    photo = ''
    if project['images']:
        cover = html.escape(image_info(project,project['images'][0]).get('thumbnail',project['images'][0]),quote=True)
        photo = '<div class="nearby-hub-photo"><img src="'+cover+'" alt="" loading="lazy" decoding="async"></div>'
    hub = '<div class="nearby-hub">'+photo+'<span>เริ่มต้นที่นี่</span><p>'+name+'</p><small>'+region+'</small></div>'
    lines = '<svg class="nearby-connections" viewBox="0 0 1000 500" preserveAspectRatio="none" aria-hidden="true"><ellipse cx="500" cy="250" rx="225" ry="215"/><ellipse cx="500" cy="250" rx="145" ry="145"/><path class="connection-1" d="M450 220C350 220 360 110 250 110"/><path class="connection-2" d="M550 220C650 220 640 110 750 110"/><path class="connection-3" d="M450 280C350 280 360 390 250 390"/><path class="connection-4" d="M550 280C650 280 640 390 750 390"/></svg>'
    sources = {guide['sourceUrl']: guide['sourceName']}
    sources.update({place['sourceUrl']: place['sourceName'] for place in places if place.get('sourceUrl')})
    credits = ' · '.join('<a href="'+html.escape(url,quote=True)+'" target="_blank" rel="noopener">'+html.escape(source_name)+' ↗</a>' for url, source_name in sources.items())
    notes = ['แผนภาพแสดงการเชื่อมต่อ ไม่อิงทิศทางหรือมาตราส่วน']
    if any(place.get('distanceMeters') is not None for place in places):
        notes.append('ระยะทางโดยประมาณตามแหล่งอ้างอิง ระยะเส้นตรงและเส้นทางจริงอาจต่างกัน')
    if any(place.get('minutes') is not None for place in places):
        notes.append('เวลาโดยประมาณอาจเปลี่ยนตามเส้นทางและการจราจร ไม่ใช่เวลาจราจรสดจาก Google Maps')
    notes.append('กดดูเส้นทางเพื่อตรวจระยะทางและเวลาปัจจุบัน')
    return '<section id="nearby-guide" class="nearby-guide" aria-labelledby="nearby-title">'+heading+'<span class="nearby-count">'+str(len(places))+' จุดหมายใกล้คุณ</span></div><div class="nearby-atlas">'+lines+hub+''.join(cards)+'</div><div class="nearby-footnote"><p>'+' · '.join(notes)+'</p><div class="nearby-sources">ข้อมูลการเดินทาง: '+credits+'</div></div></section>'


def render_property_location(project):
    heading = '<section id="location" class="section pale" aria-labelledby="location-title"><p class="eyebrow">01 · LOCATION</p><h2 id="location-title">ตำแหน่งที่พักบน Google Maps</h2>'
    if not project['location']:
        return heading+'<div class="section-placeholder"><p>ติดต่อผู้ดูแลเพื่อยืนยันตำแหน่งและขอเส้นทางของ '+html.escape(project['name'])+'</p><a class="text-link" href="#contact">สอบถามตำแหน่งที่พัก ↗</a></div>'+render_nearby_guide(project)+'</section>'
    query = quote(project.get('mapQuery', project['name']+' '+project['region']))
    nearby = '<article><h3>จุดหมายรอบโครงการ</h3><p>'+html.escape(project['nearby'])+'</p></article>' if project['nearby'] else ''
    return heading+'<div class="two-columns"><article><h3>เดินทางและใช้ชีวิต</h3><p>'+html.escape(project['location'])+'</p><a class="text-link" target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&amp;query='+query+'">ค้นหาที่พักบน Google Maps ↗</a></article>'+nearby+'</div>'+render_location_map(project)+render_nearby_guide(project)+'</section>'


def render_room_types(project):
    rooms = project.get('roomTypes', [])
    if not rooms:
        return ''
    cards = []
    for room in rooms:
        photo = image_info(project, room['image']).get('thumbnail', room['image'])
        cards.append('<article class="room-type-card"><img src="'+html.escape(photo,quote=True)+'" loading="lazy" alt="'+html.escape(room['name'],quote=True)+'"><div><h3>'+html.escape(room['name'])+'</h3><p class="muted">'+html.escape(room['area'])+' · '+html.escape(room['guests'])+'</p><p>'+html.escape(room['description'])+'</p><p class="room-type-price">'+format(room['nightlyRate'], ',')+' บาท <small>/ คืน</small></p><a class="text-link" href="'+html.escape(room['sourceUrl'],quote=True)+'" target="_blank" rel="noopener">ดูรายละเอียดห้องพัก ↗</a></div></article>')
    return '<section id="room-types" class="section"><p class="eyebrow">FIND YOUR ROOM</p><h2>เลือกห้องให้เข้ากับวันพักผ่อน</h2><p class="muted">ราคาอ้างอิงจากเว็บไซต์ที่พัก ไม่รวมอาหารเช้า สอบถามราคาตามวันเข้าพักและจำนวนผู้เข้าพักกับผู้ดูแล</p><div class="room-type-grid">'+''.join(cards)+'</div></section>'


def render_property_sections(project):
    groups = [
        ('floor-plan', '02 · ROOM PLAN', 'แปลนห้อง', 'เริ่มจากทำความรู้จักสัดส่วนและการจัดวางพื้นที่ภายในห้อง', ['plan']),
        ('room-photos', '03 · YOUR LIVING SPACE', 'รูปห้องพัก', 'สำรวจห้องนอน มุมนั่งเล่น และรายละเอียดภายในห้อง กดที่ภาพเพื่อดูขนาดใหญ่', ['interior']),
        ('more-photos', '04 · EXPLORE MORE', 'รูปเพิ่มเติม', 'ชมอาคาร ส่วนกลาง และบรรยากาศรอบโครงการ ทั้งภาพโครงการและภาพจำลอง', ['building', 'facilities']),
    ]
    if project.get('propertyType') == 'house':
        groups = [
            ('floor-plan', '02 · HOUSE PLANS', 'แปลนบ้านและผังโครงการ', 'เปรียบเทียบแบบบ้านทั้ง 4 แบบ พร้อมผังโครงการจากโบรชัวร์ Noble', ['plan']),
            ('room-photos', '03 · YOUR LIVING SPACE', 'รูปภายในบ้าน', 'ชมภาพประกอบพื้นที่นั่งเล่น ห้องนอน และรายละเอียดภายในบ้านจากสื่อโครงการ', ['interior']),
            ('more-photos', '04 · EXPLORE MORE', 'รูปบ้านและบรรยากาศโครงการ', 'ชมสถาปัตยกรรมและบรรยากาศจากภาพจำลองโครงการ กดที่ภาพเพื่อดูขนาดใหญ่', ['building', 'facilities']),
        ]
    result = ''
    for section_id, eyebrow, title, intro, categories in groups:
        images = [image for image in project['images'] if image_info(project, image)['category'] in categories]
        if images:
            result += render_gallery(dict(project, images=images), (section_id, eyebrow, title, intro))
        else:
            request = {'floor-plan': ('แปลนห้อง', 'ขอแปลนห้อง'), 'room-photos': ('รูปห้องพัก', 'ขอรูปห้องพัก'), 'more-photos': ('ภาพอาคารและส่วนกลาง', 'สอบถามภาพเพิ่มเติม')}[section_id]
            pale = ' pale' if section_id != 'room-photos' else ''
            result += '<section id="'+section_id+'" class="section photo-section'+pale+'" aria-labelledby="'+section_id+'-title"><p class="eyebrow">'+eyebrow+'</p><h2 id="'+section_id+'-title">'+title+'</h2><div class="section-placeholder"><p>สอบถาม'+request[0]+'ของ '+html.escape(project['name'])+' จากผู้ดูแล</p><a class="text-link" href="#contact">'+request[1]+' ↗</a></div></section>'
    return result


for d in listings:
    image_label='ภาพจำลองและผังโครงการ' if d['status']=='planning' else 'ภาพประกอบโครงการ'
    # Core content is present in HTML for search engines and when JavaScript is unavailable.
    body='<main id="main"><section class="property-hero"><div class="property-hero-copy"><a class="back" href="index.html#properties">← กลับไปเลือกที่พัก</a><p class="eyebrow">'+html.escape(d['region'])+' · '+d['reference']+'</p><h1>'+html.escape(d['name'])+'</h1><p class="hero-tagline">'+html.escape(d['tagline'])+'</p><a class="button gold" href="#contact">สอบถามรายละเอียดห้อง ↗</a></div><div class="property-hero-image">'
    if d['images']:body+='<img src="'+html.escape(d['images'][0],quote=True)+'" alt="'+image_label+' '+html.escape(d['name'],quote=True)+'" fetchpriority="high">'
    else:body+='<div class="no-photo"><span>NICHA CONDO</span><p>ขอภาพและรายละเอียดทรัพย์<br>จากผู้ดูแลได้โดยตรง</p></div>'
    body+='</div></section><div class="property-bar"><span>'+('สอบถามกำหนดพร้อมเข้าอยู่' if d['status']=='planning' else 'สอบถามห้องว่างและราคา')+'</span><a href="#overview">จุดเด่น</a>'+'<a href="#location">ตำแหน่งที่พัก</a><a href="#nearby-guide">สถานที่ใกล้เคียง</a><a href="#floor-plan">แปลนห้อง</a><a href="#room-photos">รูปห้องพัก</a><a href="#more-photos">รูปเพิ่มเติม</a>'+'<a href="#contact">นัดชม / สอบถาม</a></div><section id="overview" class="section overview"><div><p class="eyebrow">YOUR NEXT CHAPTER</p><h2>พื้นที่ที่เข้ากับ<br>จังหวะชีวิตของคุณ</h2></div><div><p class="lead">'+html.escape(d['description'])+'</p><div class="highlights">'+''.join('<article><span>0'+str(i+1)+'</span><h3>'+html.escape(h)+'</h3></article>' for i,h in enumerate(d['highlights']))+'</div></div></section>'
    if d.get('sources'):
        references = ' · '.join('<a href="'+html.escape(source['url'],quote=True)+'" target="_blank" rel="noopener">'+html.escape(source['name'])+' ↗</a>' for source in d['sources'])
        body = body.removesuffix('</div></section>') + '<p class="muted">ข้อมูลโครงการ: '+references+'</p></div></section>'
    body+=render_property_location(d)
    if d['amenities'] or d['audience']:
        body+='<section class="section amenities"><div><p class="eyebrow">MORE THAN A ROOM</p><h2>เติมความสุข<br>ให้วันธรรมดา</h2></div><div><h3>สิ่งอำนวยความสะดวก'+('ตามแผนโครงการ' if d['status']=='planning' else 'ของโครงการ')+'</h3><p>'+html.escape(d['amenities'])+'</p><h3>เหมาะกับไลฟ์สไตล์ของใคร</h3><p>'+html.escape(d['audience'])+'</p></div></section>'
    body+=render_room_types(d)
    body+=render_property_sections(d)
    body+='<section class="section"><p class="eyebrow">MAKE IT YOURS</p><h2>เลือกห้องให้ตรงใจ ก่อนตัดสินใจ</h2><div class="steps"><article><span>01</span><h3>บอกความต้องการ</h3><p>ส่งชื่อโครงการ งบประมาณ วันที่ต้องการเข้าอยู่ และจำนวนผู้พัก</p></article><article><span>02</span><h3>ดูรายละเอียดห้อง</h3><p>สอบถามราคา พื้นที่ ชั้น ภาพห้อง เฟอร์นิเจอร์ และเงื่อนไขสัญญา</p></article><article><span>03</span><h3>วางแผนเข้าอยู่</h3><p>ยืนยันความพร้อมของห้องและนัดชมกับผู้ดูแลก่อนตัดสินใจ</p></article></div><div class="faq"><details><summary>ห้องยังว่างไหม และค่าเช่าเท่าไร?</summary><p>ติดต่อผู้ดูแลพร้อมชื่อโครงการและวันที่ต้องการเข้าอยู่ เพื่อรับราคาและสถานะห้องล่าสุด'+(' รวมถึงกำหนดส่งมอบและความพร้อมเข้าอยู่' if d['status']=='planning' else '')+'</p></details><details><summary>ใช้ส่วนกลาง จอดรถ หรือเลี้ยงสัตว์ได้ไหม?</summary><p>สิทธิส่วนกลาง ที่จอดรถ และเงื่อนไขสัตว์เลี้ยงขึ้นอยู่กับห้องและข้อกำหนดโครงการ สอบถามผู้ดูแลเพื่อยืนยันรายละเอียดก่อนทำสัญญา</p></details></div></section><section id="contact" class="contact section"><div><p class="eyebrow">LET’S FIND YOUR PLACE</p><h2>สนใจ '+html.escape(d['name'])+'?</h2><p>ส่งชื่อโครงการพร้อมงบประมาณและวันเข้าอยู่ที่ต้องการ<br>ให้เราช่วยประสานรายละเอียดห้องที่เหมาะกับคุณ</p><div class="contact-actions"><a class="button gold" href="https://line.me/R/ti/p/@779fsbjm" target="_blank" rel="noopener">คุยกับเราทาง LINE ↗</a><a class="button outline" href="tel:0863429855">โทร 086 342 9855</a></div><a class="email" href="mailto:jew.scb18@gmail.com">jew.scb18@gmail.com</a></div><div class="inquiry"><h3>เตรียมข้อความสำหรับสอบถาม</h3><label for="inquiry-message">แก้ไขข้อความแล้วคัดลอกไปส่งใน LINE ได้เลย</label><textarea id="inquiry-message" rows="6">สวัสดีค่ะ/ครับ สนใจ '+html.escape(d['name'])+' ('+d['reference']+')\nงบประมาณ:\nวันที่ต้องการเข้าอยู่:\nจำนวนผู้พัก:\nขอทราบราคา รายละเอียดห้อง และวันสะดวกนัดชมค่ะ/ครับ</textarea><button class="button cream" id="copy-inquiry" type="button">คัดลอกข้อความ</button><p id="copy-status" role="status"></p></div></section></main><div class="mobile-contact"><a href="tel:0863429855">โทรสอบถาม</a><a href="https://line.me/R/ti/p/@779fsbjm" target="_blank" rel="noopener">สอบถามทาง LINE ↗</a></div>'
    if d.get('propertyType') == 'house':
        for old, new in [('แปลนห้อง','แปลนบ้าน'), ('รูปห้องพัก','รูปภายในบ้าน'), ('รายละเอียดห้อง','รายละเอียดบ้าน'), ('ห้องว่าง','บ้านว่าง'), ('ห้องยังว่าง','บ้านยังว่าง'), ('เลือกห้อง','เลือกบ้าน'), ('ภาพห้อง','ภาพบ้าน'), ('ของห้อง','ของบ้าน'), ('สถานะห้อง','สถานะบ้าน'), ('กับห้อง','กับบ้าน'), ('พื้นที่ ชั้น','พื้นที่ แบบบ้าน')]:
            body = body.replace(old, new)
    descriptor = 'บ้านและที่พัก' if d.get('propertyType') == 'house' else 'คอนโดและที่พักให้เช่า'
    (root/('condo-'+str(d['id'])+'.html')).write_text(shell(d['name']+' | '+descriptor+' · NICHA CONDO',d['tagline'],body,d['id']))
# Server-render the complete catalog; browser code filters these cards.
cards=[]
for d in listings:
    image_label='ภาพจำลองและผังโครงการ' if d['status']=='planning' else 'ภาพประกอบโครงการ'
    picture='<img loading="lazy" src="'+html.escape(d['images'][0],quote=True)+'" alt="'+image_label+' '+html.escape(d['name'],quote=True)+'">' if d['images'] else '<div class="card-placeholder">NICHA<span>สอบถามภาพและรายละเอียดทรัพย์</span></div>'
    cards.append('<article class="property-card" data-region="'+html.escape(d['region'],quote=True)+'" data-search="'+html.escape(d['name']+' '+d['region']+' '+d['tagline']+' '+' '.join(d.get('searchAliases',[])),quote=True)+'"><a class="card-photo" href="condo-'+str(d['id'])+'.html">'+picture+'<span class="badge">'+html.escape(d['region'])+'</span></a><div class="card-content"><p class="card-status">'+('สอบถามกำหนดพร้อมเข้าอยู่' if d['status']=='planning' else 'สอบถามรายละเอียดบ้าน' if d.get('propertyType') == 'house' else 'สอบถามรายละเอียดห้อง')+' · '+d['reference']+'</p><h3><a href="condo-'+str(d['id'])+'.html">'+html.escape(d['name'])+'</a></h3><p>'+html.escape(d['tagline'])+'</p><a class="text-link" href="condo-'+str(d['id'])+'.html">ดูรายละเอียดและสอบถาม ↗</a></div></article>')
body='''<main id="main"><section class="home-hero"><img class="hero-photo" src="Copacabana/Homepage-copacabana-02.webp" alt="ภาพประกอบโครงการ Copacabana Beach Jomtien" fetchpriority="high"><div class="home-hero-copy"><p class="eyebrow">A PLACE FOR YOUR EVERYDAY</p><h1>ที่พักที่ใช่<br>ให้ชีวิตลงตัวกว่าเดิม</h1><p>ใกล้ที่ทำงาน ใกล้มหาวิทยาลัย หรือใกล้ทะเล<br>เลือกทำเลที่เข้ากับคุณ แล้วให้เราช่วยประสานรายละเอียดห้อง</p><a class="button gold" href="#properties">ค้นพบที่พักของคุณ ↗</a></div><span class="hero-caption">ภาพประกอบโครงการ Copacabana Beach Jomtien</span></section><section class="intro section"><p class="eyebrow">NICHA CONDO</p><h2>ทุกไลฟ์สไตล์<br>มีพื้นที่ที่เหมาะกับคุณ</h2><p class="lead">ค้นหาคอนโดและที่พักในกรุงเทพฯ นนทบุรี พัทยา และกำแพงแสน เปรียบเทียบจุดเด่นของทำเล การเดินทาง และส่วนกลาง เพื่อเลือกที่พักสำหรับชีวิตทำงาน การเรียน และวันพักผ่อนของคุณ</p></section><section id="properties" class="section pale"><div class="catalog-heading"><div><p class="eyebrow">EXPLORE OUR COLLECTION</p><h2>เริ่มต้นจากทำเลที่คุณชอบ</h2></div><p>เลือกโครงการที่สนใจ<br>สอบถามรายละเอียดห้องและวันพร้อมเข้าอยู่</p></div><div class="catalog-tools"><div class="filters" role="group" aria-label="เลือกทำเล">'''+''.join('<button type="button" class="filter'+(' active' if r=='all' else '')+'" data-filter="'+r+'" aria-pressed="'+('true' if r=='all' else 'false')+'">'+label+'</button>' for r,label in [('all','ทุกทำเล'),('กรุงเทพฯ','กรุงเทพฯ'),('นนทบุรี','นนทบุรี'),('พัทยา','พัทยา / จอมเทียน'),('กำแพงแสน','กำแพงแสน'),('บ้านและที่พักอื่น','บ้านและที่พักอื่น')])+'''</div><label class="search-label">ค้นหาชื่อโครงการ<input type="search" id="property-search" placeholder="เช่น CIELA, Noble, จอมเทียน"></label></div><p id="result-count" class="muted" aria-live="polite">พบ '''+str(len(listings))+''' รายการ</p><div class="property-grid">'''+''.join(cards)+'''</div><p id="empty-results" hidden>ไม่พบรายการที่ตรงกับการค้นหา ลองเปลี่ยนชื่อหรือเลือกทุกทำเล</p></section><section class="section"><p class="eyebrow">THOUGHTFULLY CHOSEN</p><h2>เลือกที่พักจากชีวิตที่คุณอยากมี</h2><div class="steps"><article><span>01 · CITY LIVING</span><h3>เดินทางคล่องในเมือง</h3><p>สำรวจทำเลรัชดา พหลโยธิน และสุขุมวิท 71 พร้อมทางเลือกเดินทางที่เข้ากับกิจวัตรของคุณ</p></article><article><span>02 · COASTAL LIFE</span><h3>เติมบรรยากาศทะเล</h3><p>มองหาพื้นที่พักผ่อนในพัทยาและจอมเทียน พร้อมสอบถามห้องและกำหนดพร้อมเข้าอยู่</p></article><article><span>03 · CAMPUS DAYS</span><h3>ใกล้ชีวิตมหาวิทยาลัย</h3><p>เลือกทำเลศรีปทุมหรือกำแพงแสน โดยพิจารณาเส้นทางไปคณะและจุดหมายที่ใช้จริง</p></article></div></section><section class="section pale"><p class="eyebrow">YOUR NEXT MOVE</p><h2>เริ่มต้นง่าย ๆ ใน 3 ขั้นตอน</h2><div class="steps"><article><span>01</span><h3>เลือกโครงการ</h3><p>ดูข้อมูลทำเล จุดเด่น และภาพประกอบ เลือกรายการที่เข้ากับชีวิตคุณ</p></article><article><span>02</span><h3>บอกสิ่งที่ต้องการ</h3><p>แจ้งงบประมาณ วันเข้าอยู่ และจำนวนผู้พัก เพื่อสอบถามห้องที่ตรงกับความต้องการ</p></article><article><span>03</span><h3>ดูห้องก่อนตัดสินใจ</h3><p>ขอรายละเอียดห้องจริง ราคา และเงื่อนไข พร้อมประสานวันนัดชมกับผู้ดูแล</p></article></div></section><section id="contact" class="section contact"><p class="eyebrow">LET’S FIND YOUR PLACE</p><h2>ยังไม่แน่ใจว่าโครงการไหนเหมาะ?</h2><p>บอกทำเล งบประมาณ และวันที่ต้องการเข้าอยู่<br>ให้เราช่วยประสานข้อมูลที่พักสำหรับคุณ</p><div class="contact-actions"><a class="button gold" href="https://line.me/R/ti/p/@779fsbjm" target="_blank" rel="noopener">สอบถามทาง LINE ↗</a><a class="button outline" href="tel:0863429855">โทร 086 342 9855</a></div><a class="email" href="mailto:jew.scb18@gmail.com">jew.scb18@gmail.com</a></section></main>'''
(root/'index.html').write_text(shell('NICHA CONDO | เลือกคอนโดและที่พักให้เช่าที่เหมาะกับคุณ','ค้นหาคอนโดและที่พักให้เช่าในกรุงเทพฯ นนทบุรี พัทยา และกำแพงแสน ดูจุดเด่นโครงการและสอบถามห้องกับ NICHA CONDO',body))
# Keep generated HTML readable for review and direct inspection.
for page in [root/'index.html', *root.glob('condo-*.html')]:
    page.write_text(re.sub(r'><', '>\n<', page.read_text()))
print(f'Generated homepage and {len(listings)} property pages from assets/properties.json.')
