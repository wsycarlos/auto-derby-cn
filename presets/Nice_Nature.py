import auto_derby
from auto_derby import single_mode, constants


from typing import Text, Dict, Tuple

_VALUES: Dict[Text, int] = {
    "阪神新手級賽馬娘賽":0,
    "朝日盃未來錦標賽":0,
    "希望錦標賽":80,
    "全日本ジュニア優駿":0,
    "櫻花賞":0,
    "皋月賞":80,
    "NHK一哩賽":0,
    "奧克斯":0,
    "東京優駿（日本ダービー）":80,
    "安田紀念":0,
    "寶塚紀念":50,
    "日本沙地打比":0,
    "短途跑者錦標賽":0,
    "秋華賞":0,
    "菊花賞":60,
    "マイルチャンピオンシップ南部杯":0,
    "天皇賞（秋）":80,
    "伊麗莎白女王盃":80,
    "JBC經典賽":0,
    "JBC短途賽":0,
    "JBC女士經典賽":0,
    "一哩冠軍賽":0,
    "日本盃":60,
    "東京大賞典":0,
    "日本冠軍盃":0,
    "有馬紀念":30,
    "川崎記念":0,
    "二月錦標賽":0,
    "高松宮紀念":0,
    "大阪盃":80,
    "天皇賞（春）":30,
    "維多利亞一哩賽":0,
    "かしわ記念":0,
    "帝王賞":0,
}

class Preset(auto_derby.Preset):

    def score(self, old_score: float, match_name: str, ctx: single_mode.Context) -> float:
        _value = _VALUES.get(match_name, 0)
        return old_score + _value
    
    def value(self) -> Dict[constants.TrainingType, int]:
        return {
            constants.TrainingType.SPEED:900,
            constants.TrainingType.STAMINA:800,
            constants.TrainingType.POWER:800,
            constants.TrainingType.GUTS:300,
            constants.TrainingType.WISDOM:300,
            }


auto_derby.preset.register(__name__, Preset())
