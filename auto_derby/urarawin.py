# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Any, Dict, List, Text

import json
import csv

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

class UraraWin:

    instance: UraraWin
    _data: UraraData
    _localized_data: Dict[Text, Text]
    json_data_path: Any = None
    json_localized_path: Any = None
    json_pair_data_path = None
    events: List[UraraEvent]
    _dict: Dict[Text, UraraEvent]
    _pair: Dict[Text, Text]

    def __init__(self, path: Text, localized_path: Text, pair_data_path: Text) -> None:
        self.json_data_path = data.path(path)
        self.json_localized_path = data.path(localized_path)
        self.json_pair_data_path = data.path(pair_data_path)
        with open(self.json_data_path, "r", encoding="utf-8") as f:
            self._data = self.from_file(json.load(f))
        with open(self.json_localized_path, "r", encoding="utf-8") as ff:
            self._localized_data = json.load(ff)
        with open(self.json_pair_data_path, "r", encoding="utf-8") as fff:
            self._pair: Dict[Text, Text] = {}
            for k, v in csv.reader(fff):
                self._pair[k] = str(v)
        self.combine_events()

    def combine_events(self):
        self.events: List[UraraEvent] = []
        self._dict: Dict[Text, UraraEvent] = {}
        for c1 in self._data.Charactor.three_star.values():
            self.events.extend(c1.Event)
            for e in c1.Event:
                self._dict[self.translated(e.Name)]=e
        for c2 in self._data.Charactor.two_star.values():
            self.events.extend(c2.Event)
            for e in c2.Event:
                self._dict[self.translated(e.Name)]=e
        for c3 in self._data.Charactor.one_star.values():
            self.events.extend(c3.Event)
            for e in c3.Event:
                self._dict[self.translated(e.Name)]=e

        for s1 in self._data.Support.SSR.values():
            self.events.extend(s1.Event)
            for e in s1.Event:
                self._dict[self.translated(e.Name)]=e
        for s2 in self._data.Support.SR.values():
            self.events.extend(s2.Event)
            for e in s2.Event:
                self._dict[self.translated(e.Name)]=e
        for s3 in self._data.Support.R.values():
            self.events.extend(s3.Event)
            for e in s3.Event:
                self._dict[self.translated(e.Name)]=e

    @staticmethod
    def Get_OCRPairing(key: Text):
        if key in UraraWin.instance._pair:
            p = UraraWin.instance._pair[key]
            if p in UraraWin.instance._dict:
                return UraraWin.instance._dict[p]
        return None

    @staticmethod
    def GetEventFromTranslatedText(cn: Text):
        if cn in UraraWin.instance._dict:
            return UraraWin.instance._dict[cn]
        return None

    @staticmethod
    def Add_OCRPairing(key: Text, value: Text):
        UraraWin.instance.add_ocr(key, value)

    @staticmethod
    def GetEventsChoices():
        return UraraWin.instance._dict.keys()
    
    @staticmethod
    def Get_Events()-> List[UraraEvent]: 
        return UraraWin.instance.events
    
    @staticmethod
    def Translated(jp: Text)-> Text:
        return UraraWin.instance.translated(jp)

    @staticmethod
    def AddTranslation(cn_old: Text, cn_new: Text):
        UraraWin.instance.add_translation(cn_old, cn_new)
        
    @staticmethod
    def Reload():
        UraraWin.instance = UraraWin("UmaMusumeLibrary.json", "UmaMusumeLibrary_zh_CN.json", "UmaMusumeOCRPair.csv")

    def translated(self, jp: Text)-> Text:
        cn = self._localized_data.get(jp, jp)
        if cn == "":
            cn = jp
        return cn

    def add_translation(self, cn_old: Text, cn_new: Text):
        e = self._dict[cn_old]
        jp = e.Name
        self._localized_data[jp]=cn_new
        path = self.json_localized_path
        if not path:
            raise ValueError("localized file path is empty")
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self._localized_data))

    def add_ocr(self, key: Text, value: Text):
        path = self.json_pair_data_path
        if not path:
            raise ValueError("ocr pair save path is empty")
        with open(path, "a", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow((key, value))

    def from_file(self, _data: Dict[Text, Any]) -> UraraData:
        ud = UraraData()
        ud.Charactor = self.to_charactors(_data["Charactor"])
        ud.Support = self.to_supports(_data["Support"])
        return ud

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


UraraWin.instance = UraraWin("UmaMusumeLibrary.json", "UmaMusumeLibrary_zh_CN.json", "UmaMusumeOCRPair.csv")