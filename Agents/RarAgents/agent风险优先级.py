from Models.RarModels.DomainModels.rarDomainModels import RarData, RiskMatrix


async def calculate_risk_priority(data: RarData) -> None:
    """
    计算风险优先级

    Args:
        data: RAR数据对象
    """
    risklevel_value = data.RiskLevel if data.RiskLevel is not None else ""
    detectability_value = data.Detectability if data.Detectability is not None else ""

    if len(risklevel_value) != 1 or len(detectability_value) != 1:
        data.RiskPriority = "出现错误,存在错误：风险等级、可检测性"
    else:
        data.RiskPriority = RiskMatrix.risk_priority_matrix[risklevel_value][detectability_value]