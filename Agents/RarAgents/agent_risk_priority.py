from Models.RarModels.DomainModels.rar_domain_models import RarData, RiskMatrix


async def calculate_risk_priority(data: RarData) -> None:
    """
    计算风险优先级

    Args:
        data: RAR数据对象
    """
    risklevel_value = data.risk_level if data.risk_level is not None else ""
    detectability_value = data.detectability if data.detectability is not None else ""

    if len(risklevel_value) != 1 or len(detectability_value) != 1:
        data.risk_priority = "出现错误,存在错误：风险等级、可检测性"
    else:
        data.risk_priority = RiskMatrix.risk_priority_matrix[risklevel_value][detectability_value]