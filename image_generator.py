from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import pandas
from json import loads, dumps

u_font = ImageFont.truetype('Ultimatum Bold Italic.otf', size=157)


def add_logo(card_p, logo_p, save_p):
    card_image = Image.open(card_p)
    logo_image = Image.open(logo_p)

    logo_image_n = logo_image.resize((1194, 597), Image.Resampling.LANCZOS)
    logo_temp = Image.new('RGBA', (1080, 1460))
    logo_temp.paste(logo_image_n, (-57, 744, 1137, 1341), logo_image_n)
    card_image_new = Image.alpha_composite(card_image, logo_temp)
    card_image_new.save(save_p)

    card_image_new.close()
    card_image.close()
    logo_image.close()


def batch_add_logo():
    _p0 = r'D:\Desktop\0\0028SNAP\角色精选\1白清中'
    _p1 = r'D:\Desktop\0\0028SNAP\角色精选\Logos'
    _p2 = r'D:\Desktop\0\0028SNAP\角色精选'
    files = os.listdir(_p0)
    for file in files:
        cardname = file[:-4]
        card_path = '\\'.join((_p0, file))
        logo_path = '\\'.join((_p1, cardname, cardname + '_Logo.png'))
        save_path = '\\'.join((_p2, file))
        if not os.path.exists(logo_path):
            print(file)
        else:
            add_logo(card_path, logo_path, save_path)


def alpha_paste(_path, paste_up: bool, _old, _resize_turple, _crop_turple, mask=False):
    with Image.open(_path) as _im:
        _crop = _im.resize(_resize_turple, Image.Resampling.LANCZOS).crop(_crop_turple)
        if mask:
            _mask = _crop.convert('L')
            _crop.putalpha(_mask)
            enhancer = ImageEnhance.Brightness(_crop)
            _enhancered = enhancer.enhance(1.8)
            _crop = Image.alpha_composite(_enhancered, _enhancered)
        if paste_up:
            _result = Image.alpha_composite(_old, _crop)
        else:
            _result = Image.alpha_composite(_crop, _old)
    return _result


def create_png(logo_p, back_p, back01_p, back02_p, fore_p, foresc_p, save_p, cost=None, power=None, rarity=0):
    if rarity != 0:
        return

    frame_img = Image.new('RGBA', (960, 1340))
    frame_img = alpha_paste('Common.png', True, frame_img, (960, 1340), (0, 0, 960, 1340))
    logo_img = Image.new('RGBA', (960, 1340))
    with Image.open(logo_p) as _im:
        logo_crop = _im.resize((1194, 597), Image.Resampling.LANCZOS)
        logo_img.paste(logo_crop, (-117, 764, 1077, 1361), logo_crop)
    frame_img = Image.alpha_composite(frame_img, logo_img)

    art_img = Image.new('RGBA', (738, 1048))
    art_img = alpha_paste(back_p, True, art_img, (1212, 1165), (237, 60, 975, 1108))
    art_img = alpha_paste(fore_p, True, art_img, (1305, 1305), (283, 129, 1021, 1177))
    if back02_p:
        art_img = alpha_paste(back02_p, False, art_img, (1212, 1165), (237, 60, 975, 1108))
    if back01_p:
        art_img = alpha_paste(back01_p, False, art_img, (1212, 1165), (237, 60, 975, 1108))
    if foresc_p:
        art_img = alpha_paste(foresc_p, True, art_img, (1305, 1305), (283, 129, 1021, 1177), mask=True)

    image_temp = Image.new('RGBA', (960, 1340))
    image_temp.paste(art_img, (111, 124), art_img)
    last_combine = Image.alpha_composite(image_temp, frame_img)

    draw = ImageDraw.Draw(last_combine)
    if cost is not None:
        draw.text(xy=(128, 80), text=str(cost), fill='white', font=u_font, anchor='mt', align='center',
                  stroke_fill='#11147b', stroke_width=9)
    if power is not None:
        draw.text(xy=(831, 80), text=str(power), fill='white', font=u_font, anchor='mt',  align='center',
                  stroke_fill='#73351c', stroke_width=9)

    last_combine.save(save_p)


def batch_create_png():
    pandas.read_excel('data.xlsx').to_json('data0.json')
    data = []
    with open('data0.json', 'r', encoding='utf-8') as f:
        raw = loads(f.read())
        keys = list(raw.keys())
        for key in list(raw[keys[0]].keys()):
            item = {}
            for main_key in keys:
                item[main_key] = raw[main_key][key]
            data.append(item)
    with open('data.json', 'w', encoding='utf-8') as f:
        print(dumps(data, ensure_ascii=False, indent=2), file=f)

    for item in data:
        short_name = item['short']

        # if short_name not in ['Armor']:
        #     continue

        quality = item['quality']
        logo_path, back_path, back01_path, back02_path, fore_path, foresc_path = [None] * 6

        if quality == 2:
            to_create = False
        elif quality == 1:
            to_create = True
            logo_path = item['p_logo']
            back_path = item['p_back']
            back01_path = item['p_back01']
            back02_path = item['p_back02']
            fore_path = item['p_fore']
            foresc_path = item['p_foresc']
        elif quality == 0:
            to_create = True
            logo_path = '\\'.join(('Baked', 'Logos', short_name, short_name + '_Logo.png'))
            if not os.path.exists(logo_path):
                print(short_name, 'logo path not exists')
                to_create = False

            back_path = '\\'.join(('Baked', 'Cards', short_name, short_name + '_Background_Common.png'))
            if not os.path.exists(back_path):
                back_path = '\\'.join(('Baked', 'Cards', short_name, short_name + '_Background.png'))
                if not os.path.exists(back_path):
                    print(short_name, 'back path not exists')
                    to_create = False
                back01_path = '\\'.join(('Cards', short_name, short_name + '_Background01.png'))
                if not os.path.exists(back01_path):
                    back01_path = '\\'.join(('Cards', short_name, short_name + '_Background_01.png'))
                    if not os.path.exists(back01_path):
                        back01_path = '\\'.join(('Cards', short_name, short_name + '_Bacground1.png'))
                        if not os.path.exists(back01_path):
                            back01_path = '\\'.join(('Cards', short_name, short_name + '3_Background01.png'))
                            if not os.path.exists(back01_path):
                                back01_path = '\\'.join(('Cards', short_name, "Widow's Bite_Background_01.png"))
                                if not os.path.exists(back01_path):
                                    back01_path = '\\'.join(('Cards', short_name, "Agent 13_Background_01.png"))
                                    if not os.path.exists(back01_path):
                                        back01_path = '\\'.join(('Cards', short_name, "Spider-Woman_Background_01.png"))
                                        if not os.path.exists(back01_path):
                                            back01_path = '\\'.join(('Cards', 'Mysterio', 'Mysterio_Background01.png'))
                                            if not os.path.exists(back01_path):
                                                print(short_name, 'back 01 path not exists')
            else:
                back01_path = None

            back02_path = '\\'.join(('Cards', short_name, short_name + '_Background02.png'))
            if not os.path.exists(back02_path):
                back02_path = None
            else:
                back02_path = None

            fore_path = '\\'.join(('Baked', 'Cards', short_name, short_name + '_Foreground_Common.png'))
            if not os.path.exists(fore_path):
                fore_path = '\\'.join(('Baked', 'Cards', short_name, short_name + '_Foreground.png'))
                if not os.path.exists(fore_path):
                    print(short_name, 'fore path not exists')
                    to_create = False

            foresc_path = '\\'.join(('Baked', 'Cards', short_name, short_name + '_ForegroundScreen_Common.png'))
            if not os.path.exists(foresc_path):
                foresc_path = '\\'.join(('Baked', 'Cards', short_name, short_name + '_ForegroundScreen.png'))
                if not os.path.exists(foresc_path):
                    foresc_path = None
        else:
            to_create = False

        if to_create:
            # print(short_name, logo_path, back_path, back01_path, back02_path, fore_path, foresc_path)
            create_png(logo_path, back_path, back01_path, back02_path, fore_path, foresc_path,
                       '\\'.join(('Render', short_name + '.png')),
                       item['cost'], item['power'], 0)


if __name__ == '__main__':
    pass
    batch_create_png()
    # batch_add_logo()
