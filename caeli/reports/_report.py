#!/usr/bin/env python3

import requests
import datetime
import struct

##############################################################################

_dateRepr = lambda datestr: "<strong>%s</strong>" % datestr
_hourRepr = lambda dt: chr(0x3358+dt.hour)
_tempRepr = lambda i: "%3.1f\u2103" % i

def _windReprCN(ws):
    if type(ws) != float or ws < 0: return "风力未知"
    ws = round(ws, 1)
    lvls = [
        # display   min    max
        ("无风",     0.0,   0.3),
        ("软风",     0.3,   1.6),
        ("轻风",     1.6,   3.4),
        ("微风",     3.4,   5.5),
        ("和风",     5.5,   8.0),
        ("清风",     8.0,   10.8),
        ("强风",     10.8,  13.9),
        ("劲风",     13.9,  17.2),
        ("大风",     17.2,  20.8),
        ("烈风",     20.8,  24.5),
        ("狂风",     24.5,  28.5),
        ("暴风",     28.5,  32.6),
        ("台风",     32.6,  37.0),
        ("强台风",   37.0,  51.0),
        ("超强台风", 51.0,  9999),
    ]
    for name, smin, smax in lvls:
        if ws >= smin and ws < smax:
            return name
    return "风力未知"

def _wmoRepr(wmo):
    msg = {
        3: '云量增加',
        20: "雾", 21: "降水", 22: "毛毛雨雪", 23: "雨", 24: "雪", 25:
        "冻雨或冻毛毛雨", 26: "雷阵雨", 27: "沙尘暴或雪暴", 28:
        "沙尘暴或雪暴，能见度一般", 29: "沙尘暴或雪暴，能见度差",
        30: "雾", 31: "偶有雾或冰雾", 32: "雾或冰雾正在消散", 33:
        "雾或冰雾维持原状", 34: "雾或冰雾正在变浓", 35: "降霜",
        40: "降水", 41: "有降水", 42: "强烈降水", 43: "液态降水", 44:
        "强烈液态降水", 45: "固态降水", 46: "强烈固态降水", 47: "冻雨", 48:
        "强烈冻雨",
        50: "毛毛雨", 51: "轻微毛毛雨", 52: "中等毛毛雨", 53: "强烈毛毛雨", 54:
        "轻微冻毛毛雨", 55: "中等冻毛毛雨", 56: "强烈冻毛毛雨", 57: "轻微降雨",
        58: "较多降雨",
        60: "降雨", 61: "小雨", 62: "中雨", 63: "大雨", 64: "冻雨小雨", 65:
        "冻雨中雨", 66: "冻雨大雨", 67: "轻微雨雪", 68: "较多雨雪",
        70: "降雪", 71: "小雪", 72: "中雪", 73: "大雪", 74: "轻微冰珠", 75:
        "中等冰珠", 76: "强烈冰珠", 77: "雪雾", 78: "冰粒",
        80: "阵雨", 81: "间有小雨", 82: "间有中雨", 83: "间有大雨", 84:
        "间有暴雨", 85: "间有小雪", 86: "间有中雪", 87: "间有大学", 89: "冰雹",
        90: "雷阵雨", 91: "雷电天气", 92: "雷阵雨", 93: "雷阵雨伴有冰雹", 94:
        "强烈雷电天气", 95: "强烈雷阵雨", 96: "强烈雷阵雨伴有冰雹", 99:
        "龙卷风"
    }
    if wmo in msg: return msg[wmo]
    return ''

def _clctRepr(clct):
    if clct >= 80: 
        return "阴"
    elif clct >= 40:
        return "多云"
    else:
        return "晴"

def _pRepr(p):
    return "%.1f m\u3374" % (p / 100.0)

def _dayForecast(forecast):
    ret = ""

    ret += _hourRepr(forecast["forecast"]) + " "
    ret += _tempRepr(forecast["t_2m"]) + " ,"
    ret += _pRepr(forecast["p_surface"]) + ","
    ret += _clctRepr(forecast["clct"]) + ","
    ret += _windReprCN(forecast["vmax_10m"])
    wmo = _wmoRepr(forecast["ww"])
    if wmo: ret += "," + wmo

    return ret

##############################################################################

strptime = lambda i: datetime.datetime.strptime(i, "%Y-%m-%dT%H:%M:%S")

def report(lat, lng):
    url = "http://intell.neoatlantis.org/nwp/%f/%f/" % (lat, lng)
    print(url)
    q = requests.get(url)
    data = q.json()

    dayForecasts = {}

    for key in data:
        data[key]["forecast"] = strptime(data[key]["forecast"])
        data[key]["runtime"] = strptime(data[key]["runtime"])
        date = key[:10]
        if date not in dayForecasts:
            dayForecasts[date] = [] 
        dayForecasts[date].append(data[key])

    for date in dayForecasts:
        dayForecasts[date] = sorted(\
            dayForecasts[date], key=lambda i: i["forecast"])

    randomForecast = data[key]

    ret = ""
    ret += "预报地点: 经度 %f, 纬度 %f\n" % \
            (randomForecast["lng"], randomForecast["lat"])
    ret += "\n"
    for date in sorted(dayForecasts.keys())[:3]:
        ret += _dateRepr(date) + "\n"
        for forecast in dayForecasts[date]:
            ret += _dayForecast(forecast) + "\n"
    return ret 


if __name__ == "__main__":
    print(report(10, 110))
