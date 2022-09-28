# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Any, Dict, List, Text

import json
import csv
import re

from . import data


class UraraOption:
    Option: Text
    Effect: Text

class UraraEvent:
    Name: Text
    Options: List[UraraOption]

    def __str__(self) -> str:
        return "[%s]:%s"%(self.Name, self.Options)

class UraraCharactor:
    Event: List[UraraEvent]

class UraraSupport:
    Event: List[UraraEvent]

class UraraCharactors:
    three_star: Dict[Text, UraraCharactor]
    two_star: Dict[Text, UraraCharactor]
    one_star: Dict[Text, UraraCharactor]

class UraraSupports:
    SSR: Dict[Text, UraraSupport]
    SR: Dict[Text, UraraSupport]
    R: Dict[Text, UraraSupport]

class UraraData:
    Charactor: UraraCharactors
    Support: UraraSupports

class UraraStory:
    Event: List[UraraEvent]

class UraraStories:
    URA: UraraStory
    YOUTH_CUP: UraraStory
    NEW_TRACK: UraraStory

class UraraWin:

    instance: UraraWin
    _data: UraraData
    _stories: UraraStories
    _localized_data: Dict[Text, Text]
    _correction_data: Dict[Text, Text]
    json_data_path: Any = None
    json_stories_path: Any = None
    json_localized_path: Any = None
    json_correction_localized_path: Any = None
    json_pair_data_path = None
    summer_camp_text = ["夏令营中：", "夏季集训中：","夏天集训中：","夏天合宿中：","夏天集训时：","夏季合宿中："]
    summer_camp_re = [[re.compile(r'(.*)（夏令营中：(.*?)）'), re.compile(r'(.*)（夏令营中：(.*?)\)'), re.compile(r'(.*)夏令营中：(.*?)）')], [re.compile(r'(.*)（夏季集训中：(.*?)）')], [re.compile(r'(.*)（夏天集训中：(.*?)）')], 
                        [re.compile(r'(.*)（夏天合宿中：(.*?)）')], [re.compile(r'(.*)（夏天集训时：(.*?)）')], [re.compile(r'(.*)（夏季合宿中：(.*?)）')]]
    _dict: Dict[Text, List[UraraEvent]]
    _pair: Dict[Text, Text]

    def __init__(self, path: Text, stories_path: Text, localized_path: Text, correction_path: Text, pair_data_path: Text) -> None:
        self.json_data_path = data.path(path)
        self.json_stories_path = data.path(stories_path)
        self.json_localized_path = data.path(localized_path)
        self.json_correction_localized_path = data.path(correction_path)
        self.json_pair_data_path = data.path(pair_data_path)
        with open(self.json_data_path, "r", encoding="utf-8") as f0:
            self._data = self.parse_data(json.load(f0))
        with open(self.json_stories_path, "r", encoding="utf-8") as f1:
            self._stories = self.parse_stories(json.load(f1))
        with open(self.json_localized_path, "r", encoding="utf-8") as f2:
            self._localized_data = json.load(f2)
        with open(self.json_correction_localized_path, "r", encoding="utf-8") as f3:
            self._correction_data: Dict[Text, Text] = {}
            for k, v in csv.reader(f3):
                if k in self._correction_data:
                    raise ValueError("Same text is already existed: %s"%k)
                self._correction_data[k] = str(v)
        with open(self.json_pair_data_path, "r", encoding="utf-8") as f4:
            self._pair: Dict[Text, Text] = {}
            for k, v in csv.reader(f4):
                self._pair[k] = str(v)
        self.combine_events()

    def has_event(self, events: List[UraraEvent], e: UraraEvent):
        for _e in events:
            if len(_e.Options) == len(e.Options):
                diff = False
                for i in range(len(e.Options)):
                    if _e.Options[i].Option != e.Options[i].Option:
                        diff = True
                    #if _e.Options[i].Effect != e.Options[i].Effect:
                        #diff = True
                if not diff:
                    return True
        return False

    def process_post_translation_text(self, cn: Text):
        size = len(self.summer_camp_text)
        for i in range(size):
            txt = self.summer_camp_text[i]
            if txt in cn:
                res = self.summer_camp_re[i]
                for r in res:
                    g = r.findall(cn)
                    if len(g) > 0:
                        return g[0]
                print(txt)
                print(cn)
        return cn, cn

    def pre_process(self, e: UraraEvent):
        if e.Name == "お大事に！":
            e1 = UraraEvent()
            e2 = UraraEvent()
            e1.Name = e.Name
            e2.Name = e.Name
            e1.Options = []
            e2.Options = []
            for o in e.Options:
                o.Option = self.translated(o.Option)
                o1 = UraraOption()
                o2 = UraraOption()
                o1.Option, o2.Option = self.process_post_translation_text(o.Option)
                o1.Effect = o.Effect
                o2.Effect = o.Effect
                e1.Options.append(o1)
                e2.Options.append(o2)
            return e1, e2
        elif e.Name == "無茶は厳禁！":
            e1 = UraraEvent()
            e2 = UraraEvent()
            e1.Name = e.Name
            e2.Name = e.Name
            e1.Options = []
            e2.Options = []
            for o in e.Options:
                o.Option = self.translated(o.Option)
                o1 = UraraOption()
                o2 = UraraOption()
                o1.Option, o2.Option = self.process_post_translation_text(o.Option)
                o1.Effect = o.Effect
                o2.Effect = o.Effect
                e1.Options.append(o1)
                e2.Options.append(o2)
            return e1, e2
        elif e.Name in ["レース勝利","レース勝利！","レース勝利！(G1)","レース勝利！(G2)","レース勝利！(1着)","レース勝利！(クラシック10月後半以前1着)","レース勝利！(クラシック11月前半以降1着)","レース勝利！(シニア5月前半以降1着)","レース勝利(G1)","レース勝利(G2)","レース勝利(G3)","レース勝利(OP)"]:
            e.Name = "竞赛获胜"
        elif e.Name in ["レース入着","レース入着(G2)","レース入着(2~5着)","レース入着(2/4/5着)","レース入着(クラシック10月後半以前2~5着)","レース入着(クラシック11月前半以降2~5着)","レース入着(シニア5月前半以降2~5着)"]:
            e.Name = "竞赛上榜"
        elif e.Name in ["レース敗北","レース敗北(6着以下)","レース敗北(クラシック10月後半以前6着以下)","レース敗北(クラシック11月前半以降6着以下)","レース敗北(シニア5月前半以降6着以下)"]:
            e.Name = "竞赛败北"
        elif e.Name in ["夏合宿（2年目）にて","夏合宿(2年目)にて"]:
            e.Name = "夏季集训第二年|途中"
        elif e.Name in ["夏合宿（2年目）終了","夏合宿(2年目)終了"]:
            e.Name = "夏季集训（第二年）结束"
        elif e.Name in ["夏合宿（3年目）終了","夏合宿(3年目)終了"]:
            e.Name = "夏季集训（第三年）结束"
        return e, None

    def combine_events(self):
        self._dict: Dict[Text, List[UraraEvent]] = {}
        for c1 in self._data.Charactor.three_star.values():
            for e in c1.Event:
                e1, e2 = self.pre_process(e)
                if e2 == None:
                    cn = self.translated(e1.Name)
                    if cn not in self._dict:
                        self._dict[cn] = []
                    if not self.has_event(self._dict[cn], e1):
                        self._dict[cn].append(e1)
                else:
                    cn1 = self.translated(e1.Name)
                    cn2 = self.translated(e2.Name)
                    if cn1 not in self._dict:
                        self._dict[cn1] = []
                    if cn2 not in self._dict:
                        self._dict[cn2] = []
                    if not self.has_event(self._dict[cn1], e1):
                        self._dict[cn1].append(e1)
                    if not self.has_event(self._dict[cn2], e2):
                        self._dict[cn1].append(e2)
        for c2 in self._data.Charactor.two_star.values():
            for e in c2.Event:
                e1, e2 = self.pre_process(e)
                if e2 == None:
                    cn = self.translated(e1.Name)
                    if cn not in self._dict:
                        self._dict[cn] = []
                    if not self.has_event(self._dict[cn], e1):
                        self._dict[cn].append(e1)
                else:
                    cn1 = self.translated(e1.Name)
                    cn2 = self.translated(e2.Name)
                    if cn1 not in self._dict:
                        self._dict[cn1] = []
                    if cn2 not in self._dict:
                        self._dict[cn2] = []
                    if not self.has_event(self._dict[cn1], e1):
                        self._dict[cn1].append(e1)
                    if not self.has_event(self._dict[cn2], e2):
                        self._dict[cn1].append(e2)
        for c3 in self._data.Charactor.one_star.values():
            for e in c3.Event:
                e1, e2 = self.pre_process(e)
                if e2 == None:
                    cn = self.translated(e1.Name)
                    if cn not in self._dict:
                        self._dict[cn] = []
                    if not self.has_event(self._dict[cn], e1):
                        self._dict[cn].append(e1)
                else:
                    cn1 = self.translated(e1.Name)
                    cn2 = self.translated(e2.Name)
                    if cn1 not in self._dict:
                        self._dict[cn1] = []
                    if cn2 not in self._dict:
                        self._dict[cn2] = []
                    if not self.has_event(self._dict[cn1], e1):
                        self._dict[cn1].append(e1)
                    if not self.has_event(self._dict[cn2], e2):
                        self._dict[cn1].append(e2)

        for s1 in self._data.Support.SSR.values():
            for e in s1.Event:
                e1, e2 = self.pre_process(e)
                if e2 == None:
                    cn = self.translated(e1.Name)
                    if cn not in self._dict:
                        self._dict[cn] = []
                    if not self.has_event(self._dict[cn], e1):
                        self._dict[cn].append(e1)
                else:
                    cn1 = self.translated(e1.Name)
                    cn2 = self.translated(e2.Name)
                    if cn1 not in self._dict:
                        self._dict[cn1] = []
                    if cn2 not in self._dict:
                        self._dict[cn2] = []
                    if not self.has_event(self._dict[cn1], e1):
                        self._dict[cn1].append(e1)
                    if not self.has_event(self._dict[cn2], e2):
                        self._dict[cn1].append(e2)
        for s2 in self._data.Support.SR.values():
            for e in s2.Event:
                e1, e2 = self.pre_process(e)
                if e2 == None:
                    cn = self.translated(e1.Name)
                    if cn not in self._dict:
                        self._dict[cn] = []
                    if not self.has_event(self._dict[cn], e1):
                        self._dict[cn].append(e1)
                else:
                    cn1 = self.translated(e1.Name)
                    cn2 = self.translated(e2.Name)
                    if cn1 not in self._dict:
                        self._dict[cn1] = []
                    if cn2 not in self._dict:
                        self._dict[cn2] = []
                    if not self.has_event(self._dict[cn1], e1):
                        self._dict[cn1].append(e1)
                    if not self.has_event(self._dict[cn2], e2):
                        self._dict[cn1].append(e2)
        for s3 in self._data.Support.R.values():
            for e in s3.Event:
                e1, e2 = self.pre_process(e)
                if e2 == None:
                    cn = self.translated(e1.Name)
                    if cn not in self._dict:
                        self._dict[cn] = []
                    if not self.has_event(self._dict[cn], e1):
                        self._dict[cn].append(e1)
                else:
                    cn1 = self.translated(e1.Name)
                    cn2 = self.translated(e2.Name)
                    if cn1 not in self._dict:
                        self._dict[cn1] = []
                    if cn2 not in self._dict:
                        self._dict[cn2] = []
                    if not self.has_event(self._dict[cn1], e1):
                        self._dict[cn1].append(e1)
                    if not self.has_event(self._dict[cn2], e2):
                        self._dict[cn1].append(e2)
        
        for e in self._stories.URA.Event:
            cn = self.translated(e.Name)
            if cn not in self._dict:
                self._dict[cn] = []
            if not self.has_event(self._dict[cn], e):
                self._dict[cn].append(e)
        for e in self._stories.YOUTH_CUP.Event:
            cn = self.translated(e.Name)
            if cn not in self._dict:
                self._dict[cn] = []
            if not self.has_event(self._dict[cn], e):
                self._dict[cn].append(e)
        for e in self._stories.NEW_TRACK.Event:
            cn = self.translated(e.Name)
            if cn not in self._dict:
                self._dict[cn] = []
            if not self.has_event(self._dict[cn], e):
                self._dict[cn].append(e)

    @staticmethod
    def GetOCRPair(key: Text):
        if key in UraraWin.instance._pair:
            return UraraWin.instance._pair[key]
        else:
            return key

    @staticmethod
    def GetOCRPairing(key: Text):
        return UraraWin.GetEventFromTranslatedText(UraraWin.GetOCRPair(key))

    @staticmethod
    def GetEventFromTranslatedText(cn: Text):
        if cn in UraraWin.instance._dict:
            return UraraWin.instance._dict[cn]
        return None

    @staticmethod
    def AddOCRPairing(key: Text, value: Text):
        UraraWin.instance.add_ocr(key, value)

    @staticmethod
    def GetEventsChoices():
        return UraraWin.instance._dict.keys()

    @staticmethod
    def GetOptionChoices(cn: Text):
        if cn in UraraWin.instance._dict:
            _optionchoices:List[Text] = []
            _events = UraraWin.instance._dict[cn]
            for e in _events:
                o_str = ""
                for o in e.Options:
                    o_str += UraraWin.Translated(o.Option) + ";"
                _optionchoices.append(o_str)
            return _optionchoices
        return None
    
    @staticmethod
    def Translated(jp: Text)-> Text:
        return UraraWin.instance.translated(jp)

    @staticmethod
    def AddTranslation(cn_old: Text, cn_new: Text):
        UraraWin.instance.add_translation(cn_old, cn_new)
        
    @staticmethod
    def Reload():
        UraraWin.instance = UraraWin("UmaMusumeLibrary.json", "UmaMusumeLibraryMainStory.json", "UmaMusumeLibrary_zh_CN.json", "UmaMusumeLibrary_zh_CN_correction.csv", "UmaMusumeOCRPair.csv")

    def translated(self, jp: Text)-> Text:
        cn = self._localized_data.get(jp, jp)
        if cn == "":
            cn = jp
        cn = self._correction_data.get(cn, cn)
        return cn

    def add_translation(self, old_text: Text, new_text: Text):
        if old_text == new_text:
            return
        if old_text in self._correction_data:
            raise ValueError("same text is already existed: %s"%old_text)
        path = self.json_correction_localized_path
        if not path:
            raise ValueError("correction file path is empty")
        with open(path, "a", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow((old_text, new_text))

    def add_ocr(self, key: Text, value: Text):
        if key == value:
            return
        path = self.json_pair_data_path
        if not path:
            raise ValueError("ocr pair save path is empty")
        with open(path, "a", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow((key, value))

    def parse_data(self, _data: Dict[Text, Any]) -> UraraData:
        ud = UraraData()
        ud.Charactor = self.to_charactors(_data["Charactor"])
        ud.Support = self.to_supports(_data["Support"])
        return ud

    def to_story(self, _data: Dict[Text, Any]) -> UraraStory:
        us = UraraStory()
        us.Event = self.to_events(_data["Event"])
        return us

    def parse_stories(self, _data: Dict[Text, Any]) -> UraraStories:
        uss = UraraStories()
        uss.URA = self.to_story(_data["MainStory"]["None"]["メインシナリオイベント"])
        uss.YOUTH_CUP = self.to_story(_data["MainStory"]["None"]["アオハル杯"])
        uss.NEW_TRACK = self.to_story(_data["MainStory"]["None"]["Make a new track!!"])
        return uss

    def to_charactors(self, _data: Dict[Text, Any]) -> UraraCharactors:
        uc = UraraCharactors()
        uc.three_star = self.to_charactor_list(_data["☆3"])
        uc.two_star = self.to_charactor_list(_data["☆2"])
        uc.one_star = self.to_charactor_list(_data["☆1"])
        return uc

    def to_charactor_list(self, _data: Dict[Text, Any]) -> Dict[Text, UraraCharactor]:
        clist:Dict[Text, UraraCharactor]  = {}
        for n in _data:
            clist[n] = self.to_charactor(_data[n])
        return clist

    def to_charactor(self, _data: Dict[Text, Any]) -> UraraCharactor:
        c = UraraCharactor()
        c.Event = self.to_events(_data["Event"])
        return c

    def to_supports(self, _data: Dict[Text, Any]) -> UraraSupports:
        us = UraraSupports()
        us.SSR = self.to_support_list(_data["SSR"])
        us.SR = self.to_support_list(_data["SR"])
        us.R = self.to_support_list(_data["R"])
        return us

    def to_support_list(self, _data: Dict[Text, Any]) -> Dict[Text, UraraSupport]:
        slist:Dict[Text, UraraSupport]  = {}
        for n in _data:
            slist[n] = self.to_support(_data[n])
        return slist

    def to_support(self, _data: Dict[Text, Any]) -> UraraSupport:
        s = UraraSupport()
        s.Event = self.to_events(_data["Event"])
        return s

    def to_events(self, _data:List[Any]) -> List[UraraEvent]:
        l:List[UraraEvent] = []
        for e in _data:
            l.append(self.to_event(e))
        return l

    def to_event(self, _data:Dict[Text, Any]) -> UraraEvent:
        e = UraraEvent()
        for i in _data:
            e.Name = i
            e.Options = self.to_options(_data[i])
        return e

    def to_options(self, _data:List[Any]) -> List[UraraOption]:
        l:List[UraraOption] = []
        for o in _data:
            l.append(self.to_option(o))
        return l

    def to_option(self, _data:Dict[Text, Any]) -> UraraOption:
        o = UraraOption()
        o.Effect = _data["Effect"]
        o.Option = _data["Option"]
        return o


UraraWin.instance = UraraWin("UmaMusumeLibrary.json", "UmaMusumeLibraryMainStory.json", "UmaMusumeLibrary_zh_CN.json", "UmaMusumeLibrary_zh_CN_correction.csv", "UmaMusumeOCRPair.csv")