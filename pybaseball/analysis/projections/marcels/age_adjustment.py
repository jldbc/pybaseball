from typing import Optional

from pandas import isnull


def age_adjustment(age: Optional[float]) -> float:
    """
    Marcel age adjustment

    :param age: numeric
    :return: float
    """
    if isnull(age):
        return float("nan")
    
    assert age
    
    if age <= 0:
        return 1
    elif age >= 29:
        return 1 / (1 + 0.003 * (age - 29))
    else: # if age < 29:
        return 1 + 0.006 * (29 - age)
