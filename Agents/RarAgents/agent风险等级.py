from Models.RarModels.DomainModels.rarDomainModels import RarData, RiskMatrix


async def calculate_risk_level(data: RarData) -> None:
    """
    计算风险等级

    Args:
        data: RAR数据对象
    """
    severity_value = data.Severity if data.Severity is not None else ""
    probability_value = data.Probability if data.Probability is not None else ""

    if len(severity_value) != 1 or len(probability_value) != 1:
        data.RiskLevel = "出现错误,存在错误：严重性、可能性"
    else:
        data.RiskLevel = RiskMatrix.risk_level_matrix[severity_value][probability_value]