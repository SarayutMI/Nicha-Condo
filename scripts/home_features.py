"""Homepage presentation, rendered from the existing property catalog."""
from pathlib import Path
import html,re
root = Path(__file__).resolve().parent.parent

def render_home_slideshow(listings):
    by_id = {project['id']: project for project in listings}
    slides, dots = [], []
    for project_id in [9, 20, 18, 11, 1, 10]:
        project = by_id.get(project_id)
        if not project or not project['images']:
            continue
        number = len(slides)
        image = html.escape(project['images'][0], quote=True)
        name = html.escape(project['name'], quote=True)
        slides.append('<div class="hero-slide'+(' is-active' if number == 0 else '')+'" data-hero-slide aria-hidden="'+('false' if number == 0 else 'true')+'"><img class="hero-photo" src="'+image+'" alt="ภาพประกอบ '+name+'" '+('fetchpriority="high"' if number == 0 else 'loading="lazy"')+'><a class="hero-caption" href="condo-'+str(project_id)+'.html"'+(' tabindex="-1"' if number else '')+'>'+name+' ↗</a></div>')
        dots.append('<button type="button" class="hero-dot'+(' is-active' if number == 0 else '')+'" data-hero-dot="'+str(number)+'" aria-label="ดูภาพ '+name+'" aria-pressed="'+('true' if number == 0 else 'false')+'"></button>')
    return '<section class="home-hero home-slideshow" data-slideshow aria-roledescription="ภาพสไลด์" aria-label="ภาพที่พักแนะนำ">'+''.join(slides)+'<div class="home-hero-copy"><p class="eyebrow">A PLACE FOR YOUR EVERYDAY</p><h1>ที่พักที่ใช่<br>ให้ชีวิตลงตัวกว่าเดิม</h1><p>ใกล้ที่ทำงาน ใกล้มหาวิทยาลัย หรือใกล้ทะเล<br>เลือกทำเลที่เข้ากับคุณ แล้วให้เราช่วยประสานรายละเอียดห้อง</p><div class="hero-actions"><a class="button gold" href="#thailand-map">ค้นหาจากแผนที่ ↗</a><a class="hero-catalog-link" href="#properties">ดูที่พักทั้งหมด</a></div></div><div class="hero-slide-controls" hidden><button type="button" data-hero-prev aria-label="ภาพก่อนหน้า">‹</button><div class="hero-dots">'+''.join(dots)+'</div><button type="button" data-hero-next aria-label="ภาพถัดไป">›</button><button type="button" class="hero-pause" data-hero-pause aria-label="หยุดสไลด์อัตโนมัติ" aria-pressed="false">หยุดภาพ Ⅱ</button><span data-hero-counter aria-live="off">1 / '+str(len(slides))+'</span></div></section>'


def render_home_map(listings):
    areas = [
        ('bangkok', 'กรุงเทพฯ', 13.756, 100.502, 370, 290),
        ('nonthaburi', 'นนทบุรี', 13.86, 100.514, 20, 240),
        ('pattaya', 'พัทยา / จอมเทียน', 12.924, 100.877, 390, 390),
        ('kamphaeng-saen', 'กำแพงแสน', 14.02, 99.97, 12, 320),
        ('puektian', 'ปึกเตียน · เพชรบุรี', 12.9468, 100.0336, 35, 445),
    ]
    def area_for(project):
        if project['id'] == 18:
            return 'puektian'
        return {'กรุงเทพฯ':'bangkok', 'นนทบุรี':'nonthaburi', 'พัทยา':'pattaya', 'กำแพงแสน':'kamphaeng-saen'}.get(project['region'], 'pending')
    counts = {area:sum(area_for(p) == area for p in listings) for area, *_ in areas}
    chips = '<button class="map-area-chip is-active" type="button" data-map-area="all" aria-pressed="true">ทุกทำเล</button>'
    points = []
    for key, label, latitude, longitude, lx, ly in areas:
        if not counts[key]:
            continue
        x, y = 60+(longitude-97)*49, 60+(20.5-latitude)*43.4
        short_label = html.escape({'pattaya':'พัทยา', 'puektian':'ปึกเตียน'}.get(key, label))
        label = html.escape(label)
        chips += '<button class="map-area-chip" type="button" data-map-area="'+key+'" aria-pressed="false">'+label+' <span>'+str(counts[key])+'</span></button>'
        edge = lx+180 if lx < x else lx
        points.append('<a href="#map-results" class="thailand-pin" data-map-area="'+key+'" role="button" aria-pressed="false" aria-label="'+label+' '+str(counts[key])+' รายการ"><path class="pin-leader" d="M'+f'{x:.1f},{y:.1f} L{edge},{ly+27}'+'"/><circle class="pin-halo" cx="'+f'{x:.1f}'+'" cy="'+f'{y:.1f}'+'" r="11"/><circle class="pin-dot" cx="'+f'{x:.1f}'+'" cy="'+f'{y:.1f}'+'" r="5"/><rect x="'+str(lx)+'" y="'+str(ly)+'" width="180" height="54" rx="8"/><text x="'+str(lx+14)+'" y="'+str(ly+22)+'">'+short_label+'</text><text class="pin-total" x="'+str(lx+14)+'" y="'+str(ly+41)+'">'+str(counts[key])+' รายการ · ดูที่พัก ↗</text></a>')
    pending = sum(area_for(p) == 'pending' for p in listings)
    if pending:
        chips += '<button class="map-area-chip" type="button" data-map-area="pending" aria-pressed="false">สอบถามทำเล <span>'+str(pending)+'</span></button>'
    cards = []
    for project in listings:
        name = html.escape(project['name'])
        photo = ''
        if project['images']:
            image = project['images'][0]
            thumbnail = project.get('imageDetails', {}).get(image, {}).get('thumbnail', image)
            photo = '<img src="'+html.escape(thumbnail,quote=True)+'" alt="" loading="lazy">'
        else:
            photo = '<span class="map-photo-placeholder">NICHA</span>'
        cards.append('<a class="map-property" data-map-property="'+area_for(project)+'" href="condo-'+str(project['id'])+'.html">'+photo+'<span><strong>'+name+'</strong><small>'+html.escape(project['region'] if area_for(project) != 'puektian' else 'ปึกเตียน · เพชรบุรี')+'</small></span><span aria-hidden="true">↗</span></a>')
    outline = re.search(r'<path .*?/>', (root/'assets/thailand-outline.svg').read_text()).group(0)
    return '<section id="thailand-map" class="section destination-section"><div class="destination-heading"><div><p class="eyebrow">FIND YOUR PLACE IN THAILAND</p><h2>เริ่มต้นจากจุดหมาย<br>ที่คุณอยากใช้ชีวิต</h2></div><p class="muted">เลือกหมุดบนแผนที่ แล้วค้นพบที่พักในทำเลนั้น<br>จากชีวิตในเมือง สู่วันพักผ่อนริมทะเล</p></div><div class="destination-layout"><div class="thailand-map-panel"><span class="map-kicker">THAILAND · OUR DESTINATIONS</span><svg class="thailand-map" viewBox="0 0 620 760" role="group" aria-label="แผนที่ประเทศไทย เลือกทำเลเพื่อดูที่พัก"><g class="thailand-land">'+outline+'</g><text class="map-sea" x="370" y="555">อ่าวไทย</text>'+''.join(points)+'</svg><p class="map-area-note">หมุดแสดงตำแหน่งทำเลโดยประมาณ<br>ดูตำแหน่งที่พักแต่ละแห่งในหน้ารายละเอียด</p></div><div class="destination-browser"><div class="map-area-chips" role="group" aria-label="เลือกทำเลบนแผนที่">'+chips+'</div><div id="map-results" class="map-results-heading"><h3 data-map-title>ที่พักทุกทำเล</h3><span data-map-count aria-live="polite">'+str(len(listings))+' รายการ</span></div><div class="map-property-list">'+''.join(cards)+'</div><p class="map-footnote">แผนที่ประเทศไทย: <a href="https://www.naturalearthdata.com/" target="_blank" rel="noopener">Natural Earth ↗</a></p></div></div></section>'
