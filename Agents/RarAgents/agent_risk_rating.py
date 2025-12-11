from Models.RarModels.DomainModels.rar_domain_models import RarData, RiskMatrix


async def calculate_risk_level(data: RarData) -> None:
    """
    计算风险等级

    Args:
        data: RAR数据对象
    """
    severity_value = data.severity if data.severity is not None else ""
    probability_value = data.probability if data.probability is not None else ""

    if len(severity_value) != 1 or len(probability_value) != 1:
        data.risk_level = "出现错误,存在错误：严重性、可能性"
    else:
        data.risk_level = RiskMatrix.risk_level_matrix[severity_value][probability_value]