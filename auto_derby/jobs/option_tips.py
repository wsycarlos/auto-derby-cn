from email.mime import image
from threading import local
import time
import cv2

import numpy as np

import threading

import PySimpleGUI as sg
import easyocr
from zhconv import convert

from .. import action, app, templates, mathtools, terminal, wintools
from ..urarawin import UraraOption, UraraWin
from typing import List, Text
from thefuzz import fuzz, process

ALL_OPTIONS = [
    templates.SINGLE_MODE_OPTION1,
    templates.SINGLE_MODE_OPTION2,
    templates.SINGLE_MODE_OPTION3,
    templates.SINGLE_MODE_OPTION4,
    templates.SINGLE_MODE_OPTION5,
]

def stop_for_watching(target_hwnd, window, offset_y):
    while True:
        time.sleep(0.1)
        new_rect = wintools.GetWindowRect(target_hwnd)
        window.move(new_rect.left, new_rect.top + offset_y)
        count_option_1 = action.count_image(templates.SINGLE_MODE_OPTION1)
        if count_option_1 <= 0:
            window.write_event_value('-THREAD-', 0)
            return

def option_tips():
    
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
            break
        else:
            terminal.pause("Cannot find target window")

    while True:

        tmpl, _ = action.wait_image(templates.SINGLE_MODE_OPTION1, templates.SINGLE_MODE_FINISH_BUTTON)
        
        if tmpl.name == templates.SINGLE_MODE_FINISH_BUTTON:
            break
        
        time.sleep(0.2)  # wait animation
        event_screen = app.device.screenshot(max_age=0)
        
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

        reader = easyocr.Reader(['ch_tra', 'en'])

        name_result = reader.readtext(cv_event_name_img)
        options_result = reader.readtext(cv_options_img)

        name_text = ""
        options_text = ""

        for i in name_result:
            name_text += i[1]

        for j in options_result:
            options_text += j[1]

        name_text = convert(name_text, "zh-cn")
        options_text = convert(options_text, "zh-cn")

        found = False
        options = None

        ocr_pairing = UraraWin.Get_OCRPairing(name_text)

        if ocr_pairing != None:
            if len(ocr_pairing) <= 1:
                found = True
                options = ocr_pairing[0].Options
            else:
                for e in ocr_pairing:
                    o_str = ""
                    for o in e.Options:
                        o_str += UraraWin.Translated(o.Option)
                    if fuzz.token_set_ratio(o_str, options_text) > 85:
                        found = True
                        options = e.Options
        else:
            for event in UraraWin.Get_Events():
                if fuzz.ratio(name_text, UraraWin.Translated(event.Name)) > 85:
                    app.log.text(("Found Matched Name: [%s] vs. [%s]")%(name_text, UraraWin.Translated(event.Name)))
                    o_str = ""
                    for o in event.Options:
                        o_str += UraraWin.Translated(o.Option)
                    app.log.text(("Available Options: [%s] vs. [%s]")%(options_text, o_str))
                    if fuzz.token_set_ratio(o_str, options_text) > 70:
                        found = True
                        options = event.Options

            if found:
                UraraWin.Add_OCRPairing(name_text, UraraWin.Translated(event.Name))
                UraraWin.Reload()
            else:
                event_choices = process.extractBests(name_text, UraraWin.GetEventsChoices(), limit = 5)
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
                    ans = terminal.prompt("Choose pairing option\n(1/2/3/4/5):")
                ret = int(ans) - 1
                _c = event_choices[ret][0]

                options_for_choice = UraraWin.GetOptionChoices(_c)
                option_choices = process.extractBests(options_text, options_for_choice, limit = 5)
                ans = ""
                while ans not in ["1", "2", "3", "4", "5"]:
                    app.log.text(("OCR Result: [%s]")%(options_text))
                    for c in option_choices:
                        app.log.text(("Potential Option: [%s] with score of %s")%(c[0], c[1]))
                    ans = terminal.prompt("Choose pairing option\n(1/2/3/4/5):")
                ret = int(ans) - 1
                _o_choice_text = option_choices[ret][0]
                _o_index = options_for_choice.index(_o_choice_text)
                _e = UraraWin.GetEventFromTranslatedText(_c)[_o_index]

                _rewrite = ""
                while _rewrite not in ["Y", "n"]:
                    _rewrite = terminal.prompt("Do you want to rewrite translation for [%s]?\n(Y/n)"%_c)
                if _rewrite == "Y":
                    _new_c = terminal.prompt("Choose which text to put into translation data(Enter to use [%s]):\n"%name_text)
                    if _new_c == "":
                        _new_c = name_text
                    UraraWin.AddTranslation(_c, _new_c)
                    _c = _new_c
                for i in range(len(_e.Options)):
                    _old_o = UraraWin.Translated(_e.Options[i].Option)
                    _ocr_o = convert(options_result[i][1], "zh-cn")
                    _rewrite = ""
                    while _rewrite not in ["Y", "n"]:
                        _rewrite = terminal.prompt("Do you want to rewrite translation for [%s]?\n(Y/n)"%_old_o)
                    if _rewrite == "Y":
                        _new_o = terminal.prompt("Choose which text to put into translation data(Enter to use [%s])\n"%_ocr_o)
                        if _new_o == "":
                            _new_o = _ocr_o
                        UraraWin.AddTranslation(_old_o, _new_o)

                found = True
                UraraWin.Add_OCRPairing(name_text, _c)
                UraraWin.Reload()
                ocr_pairing = UraraWin.Get_OCRPairing(name_text)
                if ocr_pairing == None:
                    terminal.pause("Something went wrong for OCR Pairing in Option selection")
                else:
                    if len(ocr_pairing) <= 1:
                        found = True
                        options = ocr_pairing[0].Options
                    else:
                        for e in ocr_pairing:
                            o_str = ""
                        for o in e.Options:
                            o_str += UraraWin.Translated(o.Option)
                        if fuzz.token_set_ratio(o_str, options_text) > 85:
                            found = True
                            options = e.Options

        if found:
            
            win_rect = wintools.GetWindowRect(target_window.hwnd)
            c_rect = wintools.GetClientRect(target_window.hwnd)

            size_x = c_rect.right - c_rect.left
            size_y = c_rect.bottom - c_rect.top

            event_screen_width = event_screen.width
            event_screen_height = event_screen.height
            event_screen_aspect_ratio = event_screen_height / event_screen_width
            real_size_y = (int)(size_x * event_screen_aspect_ratio)
            #offset_size_y = size_y - real_size_y
            #border_size_y = wintools.GetWindowTitleBarHeight()
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
                _, pos1 = action.wait_image(templates.SINGLE_MODE_OPTION1)
                _, pos2 = action.wait_image(templates.SINGLE_MODE_OPTION2)
                
                pos1_y = (int)((pos1[1])*size_height_ratio)
                pos2_y = (int)((pos2[1])*size_height_ratio)

                option_height_y = (int)(55 * size_height_ratio)
                option_offset_y = (int)(16 * size_height_ratio)
                option_offset_x = (int)(19 * size_height_ratio)
                
                bg_top = [sg.Column([], size=(size_x, pos1_y - option_offset_y))]
                layout.append(bg_top)
                bg_1 = [sg.Column([], size=((int)(size_x / 2), option_height_y)), sg.Text(options[0].Effect, background_color='white'), sg.Column([], size=(option_offset_x, option_height_y))]
                layout.append(bg_1)
                bg_gap = [sg.Column([], size=(size_x, pos2_y - pos1_y - option_height_y))]
                layout.append(bg_gap)
                bg_2 = [sg.Column([], size=((int)(size_x / 2), option_height_y)), sg.Text(options[1].Effect, background_color='white'), sg.Column([], size=(option_offset_x, option_height_y))]
                layout.append(bg_2)

                if options_length > 2:

                    _, pos3 = action.wait_image(templates.SINGLE_MODE_OPTION3)
                    pos3_y = (int)((pos3[1])*size_height_ratio)                    
                    bg_gap = [sg.Column([], size=(size_x, pos3_y - pos2_y - option_height_y))]
                    layout.append(bg_gap)
                    bg_3 = [sg.Column([], size=((int)(size_x / 2), option_height_y)), sg.Text(options[2].Effect, background_color='white'), sg.Column([], size=(option_offset_x, option_height_y))]
                    layout.append(bg_3)

                    if options_length > 3:

                        _, pos4 = action.wait_image(templates.SINGLE_MODE_OPTION4)
                        pos4_y = (int)((pos4[1])*size_height_ratio)
                        bg_gap = [sg.Column([], size=(size_x, pos4_y - pos3_y - option_height_y))]
                        layout.append(bg_gap)
                        bg_4 = [sg.Column([], size=((int)(size_x / 2), option_height_y)), sg.Text(options[3].Effect, background_color='white'), sg.Column([], size=(option_offset_x, option_height_y))]
                        layout.append(bg_4)

                        if options_length > 4:

                            _, pos5 = action.wait_image(templates.SINGLE_MODE_OPTION5)
                            pos5_y = (int)((pos5[1])*size_height_ratio)
                            bg_gap = [sg.Column([], size=(size_x, pos5_y - pos4_y - option_height_y))]
                            layout.append(bg_gap)
                            bg_5 = [sg.Column([], size=((int)(size_x / 2), option_height_y)), sg.Text(options[4].Effect, background_color='white'), sg.Column([], size=(option_offset_x, option_height_y))]
                            layout.append(bg_5)

                            if options_length > 5:
                                terminal.pause("More than 5 options available!")

            if should_create_window:
                bg_last = [sg.Column([], size=(size_x, real_size_y))]
                layout.append(bg_last)
                
                window = sg.Window('', layout, background_color='white', transparent_color='white', keep_on_top=True, size=(size_x, real_size_y), location=(win_rect.left, win_rect.top + border_size_y), margins=(0, 0), no_titlebar=True, element_padding=(0,0), element_justification='right', finalize=True)
                threading.Thread(target=stop_for_watching, args=(target_window.hwnd, window, border_size_y), daemon=True).start()
                while True:
                    event, values = window.read()
                    if event == sg.WIN_CLOSED:
                        break
                    elif event == '-THREAD-':
                        break
                window.close()
        else:
            terminal.pause(("No Available Option Found for %s")%name_text)
            UraraWin.Reload()