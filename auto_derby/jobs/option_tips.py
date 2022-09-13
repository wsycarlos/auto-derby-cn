import time
import cv2

import numpy as np

import re

import threading

from PIL.Image import Image
import PySimpleGUI as sg
import easyocr
from zhconv import convert

from .. import action, app, templates, mathtools, terminal, wintools
from ..urarawin import UraraOption, UraraWin
from typing import List, Text
from thefuzz import process

ALL_OPTIONS = [
    templates.SINGLE_MODE_OPTION1,
    templates.SINGLE_MODE_OPTION2,
    templates.SINGLE_MODE_OPTION3,
    templates.SINGLE_MODE_OPTION4,
    templates.SINGLE_MODE_OPTION5,
]

ocr_reader = easyocr.Reader(['ch_tra', 'en'])

skillset = re.compile('『(.*?)』')
nameset = re.compile('\n(.*)の絆ゲージ')
gooutset = re.compile('\n(.*)とお出かけできるようになる')

def stop_for_watching(target_hwnd, window, offset_y):
    while True:
        time.sleep(0.1)
        new_rect = wintools.GetWindowRect(target_hwnd)
        window.move(new_rect.left, new_rect.top + offset_y)
        count_option_1 = action.count_image(templates.SINGLE_MODE_OPTION1)
        if count_option_1 <= 0:
            window.write_event_value('-THREAD-', 0)
            return

def find_game_window():
    target_window: wintools.WinWindow = None
    while True:
        windows = wintools.GetAllWindows()
        found = False
        for window in windows:
            if "賽馬娘Pretty Derby" in window.Title:
                target_window = window
                found = True
        if found:
            sg.set_options(font=("黑体", 10))
            sg.set_options(background_color='white')
            sg.set_options(text_color='red')
            return target_window
        else:
            terminal.pause("Cannot find target window")

def prompt_for_events(name_text: Text, choice_list: List[Text])-> Text:
    event_choices = process.extractBests(name_text, choice_list, limit = 5)
    ans = ""
    while ans not in ["1", "2", "3", "4", "5"]:
        app.log.text(("OCR Result: [%s]")%(name_text))
        for c in event_choices:
            events = UraraWin.GetEventFromTranslatedText(c[0])
            if len(events) <= 1:
                o_str = ""
                for o in events[0].Options:
                    o_str += UraraWin.Translated(o.Option)
                app.log.text(("Potential Option: [%s]:[%s] with score of %s")%(c[0], o_str, c[1]))
            else:
                app.log.text(("Potential Option: [%s] with score of %s")%(c[0], c[1]))
        ans = terminal.prompt("Choose pairing option\n(1/2/3/4/5/r for reload):")
        if ans == "R" or ans == "r":
            return "reload", True
    ret = int(ans) - 1
    return event_choices[ret][0], False

def prompt_for_options(options_text: Text, choice_list: List[Text]):
    option_choices = process.extractBests(options_text, choice_list, limit = 5)
    ans = ""
    while ans not in ["1", "2", "3", "4", "5"]:
        app.log.text(("OCR Result: [%s]")%(options_text))
        for c in option_choices:
            app.log.text(("Potential Option: [%s] with score of %s")%(c[0], c[1]))
        ans = terminal.prompt("Choose pairing option\n(1/2/3/4/5/r for reload):")
        if ans == "R" or ans == "r":
            return "reload", True
    ret = int(ans) - 1
    return option_choices[ret][0], False

def rewrite_translation(old_text:Text, default_text:Text):
    _rewrite = ""
    while _rewrite not in ["Y", "n"]:
        _rewrite = terminal.prompt("Do you want to rewrite translation for [%s]?\n(Y/n/Enter for yes)"%old_text)
        if _rewrite == "":
            _rewrite = "Y"
    if _rewrite == "Y":
        _new_text = terminal.prompt("Choose which text to put into translation data(Enter to use [%s]):\n"%default_text)
        if _new_text == "":
            _new_text = default_text
        UraraWin.AddTranslation(old_text, _new_text)
        UraraWin.Reload()
        return _new_text
    return old_text

def get_ocr_result(event_screen: Image):
        
    rp = mathtools.ResizeProxy(event_screen.width)
    event_name_bbox = rp.vector4((75, 155, 305, 180), 466)
    options_bbox = rp.vector4((50, 200, 400, 570), 466)
    cv_event_name_img = np.asarray(event_screen.crop(event_name_bbox).convert("L"))
    _, cv_event_name_img = cv2.threshold(cv_event_name_img, 220, 255, cv2.THRESH_TOZERO)
    
    cv_options_img = np.asarray(event_screen.crop(options_bbox).convert("L"))
    
    option_rows = (cv2.reduce(cv_options_img, 1, cv2.REDUCE_MAX) == 255).astype(
        np.uint8
    )
    
    option_mask = np.repeat(option_rows, cv_options_img.shape[1], axis=1)
    cv_options_img = 255 - cv_options_img
    cv_options_img *= option_mask
    
    _, cv_options_img = cv2.threshold(cv_options_img, 128, 255, cv2.THRESH_BINARY)

    name_result = ocr_reader.readtext(cv_event_name_img)
    options_result = ocr_reader.readtext(cv_options_img)

    return name_result, options_result

def select_option(options_text:Text, option_choice_list: List[Text]):
    option_choice = process.extractOne(options_text, option_choice_list)
    if option_choice[1] < 80:
        option_text, need_reload = prompt_for_options(options_text, option_choice_list)
        return option_text, need_reload, True
    else:
        return option_choice[0], False, False

def layout_padding(x: int, y: int):
    return [sg.Column([], size=(x, y))]

def layout_text(text: Text, x: int, option_height_y: float, option_offset_x: float):
    return [sg.Column([], size=(x, option_height_y)), sg.Text(text, background_color='white'), sg.Column([], size=(option_offset_x, option_height_y))]

def pos_y_one_option(image: Text, size_height_ratio:float):
    _, pos = action.wait_image(image)
    return (int)((pos[1])*size_height_ratio)

def translate_effect(effect:Text) -> Text:
    effect = effect.replace("「","『")
    effect = effect.replace("」","』")
    effect = effect.replace("・","·")
    effect = effect.replace("〇","○")
    effect = effect.replace("◯","○")
    skill_group = skillset.findall(effect)
    for _sg in skill_group:
        cn_sg = UraraWin.Translated(_sg)
        effect = effect.replace(_sg, cn_sg)
    name_group = nameset.findall(effect)
    for _ng in name_group:
        cn_ng = UraraWin.Translated(_ng)
        effect = effect.replace(_ng, cn_ng)
    goout_group = gooutset.findall(effect)
    for _gg in goout_group:
        cn_gg = UraraWin.Translated(_gg)
        effect = effect.replace(_gg, cn_gg)
    effect = effect.replace("スピード(速度)","速度")
    effect = effect.replace("賢さ(智力)","智力")
    effect = effect.replace("根性(毅力)","意志力")
    effect = effect.replace("パワー(力量)","力量")
    effect = effect.replace("スタミナ(耐力)","耐力")
    effect = effect.replace("スキルPt(技能点数)","技能点数")
    effect = effect.replace("やる気(干劲)","干劲")
    effect = effect.replace("アップ(提升)","提升")
    effect = effect.replace("ダウン(下降)","下降")
    effect = effect.replace("ランダムで(有概率)","有概率")
    effect = effect.replace("になる","获得")
    effect = effect.replace("絆ゲージ","羁绊")
    effect = effect.replace("もしくは","或者")
    effect = effect.replace("ヒントLv","灵感Lv")
    effect = effect.replace("とお出かけできるようになる","可以一起出行")
    effect = effect.replace("直前のトレーニングに応じた","根据之前的训练")
    effect = effect.replace("ステータス(能力)","能力")
    effect = effect.replace("からランダムに(随机)","随机")
    effect = effect.replace("※サポート効果により数値が変動","※数值因支援效应而波动")
    effect = effect.replace("バ場状況や出場したレース場に関係するスキルのヒント","相关赛道技能")
    effect = effect.replace("の","的")
    effect = effect.replace("スピード","速度")
    effect = effect.replace("賢さ","智力")
    effect = effect.replace("根性","意志力")
    effect = effect.replace("パワー","力量")
    effect = effect.replace("スタミナ","耐力")
    effect = effect.replace("スキルPt","技能点数")
    effect = effect.replace("やる気","干劲")
    effect = effect.replace("アップ","提升")
    effect = effect.replace("ダウン","下降")
    effect = effect.replace("ランダムで","有概率")
    effect = effect.replace("ステータス","能力")
    effect = effect.replace("からランダムに","随机")
    effect = effect.replace("絆","羁绊")
    return effect

def process_ocr(event_screen: Image):
    name_result, options_result = get_ocr_result(event_screen)
    
    name_text = ""
    options_text = ""
    
    for i in name_result:
        name_text += i[1]
        
    for j in options_result:
        options_text += j[1] + ";"

    return convert(name_text, "zh-cn"), convert(options_text, "zh-cn"), options_result

def display_window(hwnd, layout, size_x: int, size_y: int, border_size_y):

    win_rect = wintools.GetWindowRect(hwnd)

    bg_last = [sg.Column([], size=(size_x, size_y))]
    layout.append(bg_last)
    
    window = sg.Window('', layout, background_color='white', transparent_color='white', keep_on_top=True, size=(size_x, size_y), location=(win_rect.left, win_rect.top + border_size_y), margins=(0, 0), no_titlebar=True, element_padding=(0,0), element_justification='right', finalize=True)
    threading.Thread(target=stop_for_watching, args=(hwnd, window, border_size_y), daemon=True).start()
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == '-THREAD-':
            break
    window.close()

def process_window(event_screen: Image, target_window: wintools.WinWindow, options: List[UraraOption]):

    c_rect = wintools.GetClientRect(target_window.hwnd)

    size_x = c_rect.right - c_rect.left
    #size_y = c_rect.bottom - c_rect.top

    event_screen_width = event_screen.width
    event_screen_height = event_screen.height

    event_screen_aspect_ratio = event_screen_height / event_screen_width
    real_size_y = (int)(size_x * event_screen_aspect_ratio)
    
    border_size_y = 50

    size_height_ratio = real_size_y / event_screen_height

    should_create_window = False
    layout = []

    options_length = len(options)

    if options_length == 0:
        pass
    elif options_length == 1:
        pass
    else:
        should_create_window = True
        
        option_offset_y = (int)(16 * size_height_ratio)
        option_height_y = (int)(55 * size_height_ratio)
        option_offset_x = (int)(19 * size_height_ratio)

        pos1_y = pos_y_one_option(templates.SINGLE_MODE_OPTION1, size_height_ratio)
        pos2_y = pos_y_one_option(templates.SINGLE_MODE_OPTION2, size_height_ratio)
        
        layout.append(layout_padding(size_x, pos1_y - option_offset_y))

        layout.append(layout_text(translate_effect(options[0].Effect), (int)(size_x / 2), option_height_y, option_offset_x))

        layout.append(layout_padding(size_x, pos2_y - pos1_y - option_height_y))

        layout.append(layout_text(translate_effect(options[1].Effect), (int)(size_x / 2), option_height_y, option_offset_x))

        if options_length > 2:
            
            pos3_y = pos_y_one_option(templates.SINGLE_MODE_OPTION3, size_height_ratio)
            layout.append(layout_padding(size_x, pos3_y - pos2_y - option_height_y))
            layout.append(layout_text(translate_effect(options[2].Effect), (int)(size_x / 2), option_height_y, option_offset_x))

            if options_length > 3:

                pos4_y = pos_y_one_option(templates.SINGLE_MODE_OPTION3, size_height_ratio)
                layout.append(layout_padding(size_x, pos4_y - pos3_y - option_height_y))
                layout.append(layout_text(translate_effect(options[3].Effect), (int)(size_x / 2), option_height_y, option_offset_x))

                if options_length > 4:

                    pos5_y = pos_y_one_option(templates.SINGLE_MODE_OPTION3, size_height_ratio)
                    layout.append(layout_padding(size_x, pos5_y - pos4_y - option_height_y))
                    layout.append(layout_text(translate_effect(options[4].Effect), (int)(size_x / 2), option_height_y, option_offset_x))

                    if options_length > 5:
                        terminal.pause("More than 5 options available!")

    if should_create_window:
        display_window(target_window.hwnd, layout, size_x, real_size_y, border_size_y)

def find_event_options(name_text: Text, options_text: Text, options_result):
    found = False
    options = None
    ocr_pairing = UraraWin.GetOCRPairing(name_text)
    if ocr_pairing != None:
        if len(ocr_pairing) <= 1:
            found = True
            options = ocr_pairing[0].Options
        else:
            _event_text = UraraWin.GetOCRPair(name_text)
            _o_choice_list = UraraWin.GetOptionChoices(_event_text)
            _o_choice_text, _need_reload, _need_rewrite = select_option(options_text, _o_choice_list)
            if _need_reload:
                return False, None
            _o_index = _o_choice_list.index(_o_choice_text)

            _event = UraraWin.GetEventFromTranslatedText(_event_text)[_o_index]

            if _need_rewrite:
                for i in range(len(_event.Options)):
                    _old_o = UraraWin.Translated(_event.Options[i].Option)
                    _ocr_o = convert(options_result[i][1], "zh-cn")
                    _old_o = rewrite_translation(_old_o, _ocr_o)
            
            found = True
            options = _event.Options
    else:

        _event_choice_text, _need_reload = prompt_for_events(name_text, UraraWin.GetEventsChoices())
        
        if _need_reload:
            return False, None

        _o_choice_list = UraraWin.GetOptionChoices(_event_choice_text)

        _o_choice_text, _need_reload = prompt_for_options(options_text, _o_choice_list)

        if _need_reload:
            return False, None
        
        _o_index = _o_choice_list.index(_o_choice_text)
        _event = UraraWin.GetEventFromTranslatedText(_event_choice_text)[_o_index]

        _event_choice_text = rewrite_translation(_event_choice_text, name_text)
        
        for i in range(len(_event.Options)):
            _old_o = UraraWin.Translated(_event.Options[i].Option)
            _ocr_o = convert(options_result[i][1], "zh-cn")
            _old_o = rewrite_translation(_old_o, _ocr_o)

        found = True
        UraraWin.AddOCRPairing(name_text, _event_choice_text)
        UraraWin.Reload()
        ocr_pairing = UraraWin.GetOCRPairing(name_text)
        if ocr_pairing == None:
            terminal.pause("Something went wrong for OCR Pairing in Option selection")
        else:
            if len(ocr_pairing) <= 1:
                found = True
                options = ocr_pairing[0].Options
            else:
                _event_text = UraraWin.GetOCRPair(name_text)
                _o_choice_list = UraraWin.GetOptionChoices(_event_text)
                _o_choice_text, _need_reload, _need_rewrite = select_option(options_text, _o_choice_list)
                if _need_reload:
                    return False, None
                _o_index = _o_choice_list.index(_o_choice_text)
                
                _event = UraraWin.GetEventFromTranslatedText(_event_text)[_o_index]
                
                if _need_rewrite:
                    for i in range(len(_event.Options)):
                        _old_o = UraraWin.Translated(_event.Options[i].Option)
                        _ocr_o = convert(options_result[i][1], "zh-cn")
                        _old_o = rewrite_translation(_old_o, _ocr_o)
            
                found = True
                options = _event.Options

    return found, options

def option_tips():
    
    target_window: wintools.WinWindow = find_game_window()

    while True:

        tmpl, _ = action.wait_image(templates.SINGLE_MODE_OPTION1, templates.SINGLE_MODE_FINISH_BUTTON)
        
        if tmpl.name == templates.SINGLE_MODE_FINISH_BUTTON:
            break
        
        time.sleep(0.2)  # wait animation
        
        event_screen = app.device.screenshot(max_age=0)

        name_text, options_text, options_result = process_ocr(event_screen)

        found, options = find_event_options(name_text, options_text, options_result)

        if found:
            process_window(event_screen, target_window, options)
        else:
            terminal.pause(("No Available Option Found for %s")%name_text)
            UraraWin.Reload()