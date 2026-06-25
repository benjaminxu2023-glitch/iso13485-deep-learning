from agents.rule_engine.base import BaseRuleEngine
from agents.rule_engine.zhejiang import ZhejiangRuleEngine
from agents.rule_engine.jiangsu import JiangsuRuleEngine
from agents.rule_engine.shanghai import ShanghaiRuleEngine


def get_rule_engine(province: str) -> BaseRuleEngine:
    engines = {
        "zhejiang": ZhejiangRuleEngine,
        "jiangsu": JiangsuRuleEngine,
        "shanghai": ShanghaiRuleEngine,
    }
    if province not in engines:
        raise ValueError(f"不支持的省份: {province}")
    return engines[province]()
