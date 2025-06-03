

def search_match(response):
    candidates = [response]

    if "alternatives" in response:
        candidates += response["alternatives"]

    while candidates and candidates[0]["matchType"] not in ("EXACT", "FUZZY"):
        candidates.pop(0)

    if candidates:
        return candidates[0]["scientificName"]

    return ""