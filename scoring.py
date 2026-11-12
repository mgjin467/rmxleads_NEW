\
def est_concrete_by_keywords(title: str) -> float:
    s = (title or "").lower()
    base = 100.0
    if any(k in s for k in ["물류","창고","센터"]): base *= 1.6
    if any(k in s for k in ["공장","산업","산단"]): base *= 1.5
    if any(k in s for k in ["아파트","주거","주상복합","오피스텔"]): base *= 1.4
    if any(k in s for k in ["학교","병원","관사","체육"]): base *= 1.2
    if any(k in s for k in ["리모델","보수","유지보수"]): base *= 0.6
    return base

def lead_score(distance_km: float, est_m3: float, dday: int, search_radius_km: float) -> float:
    w_dist, w_m3, w_time = 0.45, 0.4, 0.15
    dist_component = max(0, (search_radius_km - distance_km) / search_radius_km)
    m3_component   = min(1.0, est_m3 / 300.0)
    time_component = max(0, 1 - (dday/30))
    return round(100*(w_dist*dist_component + w_m3*m3_component + w_time*time_component), 2)
