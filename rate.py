import twder

def list_currencies() -> None:
    """
    return a list of all supported currencies 
    """
    return twder.currencies()

def get_now_rate(currency: str) -> float:
    """
    return lastest rate (即期賣出) of the given currency
    :param: currency 3-letter code of the currency
    """
    rates = twder.now(currency)
    rate = -1
    try:
        rate = float(rates[-1])
    except ValueError:
        rate = float(rates[2])
    if rate == -1:
        raise ValueError("Rate is not available")
    
    print(f"Now: {currency}: {rate}")
    return rate

def get_yesterday_rate(currency: str) -> float:
    """
    return the earliest yesterday rate (即期賣出) of the given currency
    :param: currency 3-letter code of the currency
    """
    rates = twder.past_day(currency)[0]
    rate = -1
    try:
        rate = float(rates[-1])
    except ValueError:
        rate = float(rates[2])
    if rate == -1:
        raise ValueError("Rate is not available")
    
    print(f"Yesterday: {currency}: {rate}")
    return rate
    