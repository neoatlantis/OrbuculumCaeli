#!/usr/bin/env python3

import requests
import datetime
import struct

##############################################################################

strptime = lambda i: datetime.datetime.strptime(i, "%Y-%m-%dT%H:%M:%SZ")

def _dtRepr(dt, tzOffset):
    if type(dt) == str: dt = strptime(dt)
    return "%04d-%02d-%02d %02d:%02d:%02d" % (dt+tzOffset).timetuple()[:6]
_dateRepr = lambda dt: "%04d-%02d-%02d" % dt.timetuple()[0:3]
_hourRepr = lambda dt: chr(0x3358+dt.hour)
_tempRepr = lambda i: "%3.1f\u2103" % i

def _tzRepr(timeDelta):
    absSeconds = abs(timeDelta.total_seconds())
    isMinus = (timeDelta.total_seconds() < 0)
    hours = int(absSeconds / 3600)
    minutes = int((absSeconds % 3600) / 60)
    return "UTC%s%02d:%02d" % (isMinus and "-" or "+", hours, minutes)

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

def translateCoordinates(coordinates):
    lat, lng = coordinates[0], coordinates[1]
    latRet, lngRet = "赤道", "本初子午线"
    if lat > 0:
        latRet = "%.4f N" % abs(lat)
    elif lat < 0:
        latRet = "%4.f S" % abs(lat)
    if lng > 0:
        lngRet = "%.4f E" % abs(lng)
    elif lng < 0:
        lngRet = "%.4f W" % abs(lng)
    return "%s, %s" % (latRet, lngRet)

def averagePressureAndTemperatureIn24hrs(forecasts):
    now = datetime.datetime.utcnow()
    pn, Tn = [], []

    for forecast in forecasts[:24]:
        forecastTime = forecast["forecast"]
        if (forecastTime - now).total_seconds() <= 86400:
            pressure = forecast["p_surface"]
            temperature = forecast["t_2m"]
            pn.append(pressure)
            Tn.append(temperature)

    p = sum(pn) / len(pn)
    T = sum(Tn) / len(Tn) + 273.15
    return p, T

##############################################################################


# ---- Routine for getting observer's astronomical info from Project Orbuculum
#      Celesti.

def astroData(lat, lng, pressureFix=None, temperatureFix=None):
    """Returns a tuple of (`report`, `timezone`), the first is a string
    containing human-readable reports on astro data, the second is for
    calculation of observer's timezones."""
    try:
        url = "http://intell.neoatlantis.org/astro/%f/%f/json" % (lat, lng)
        args = []
        if pressureFix: args.append("pressure=%f" % pressureFix)
        if temperatureFix: args.append("temperature=%f" % temperatureFix)
        if args: url += "?" + "&".join(args)
        q = requests.get(url)
        data = q.json()
    except Exception as e:
        print(e)
        return "No available astronomical data.", {
            'status': 'default',
            'dstOffset': 0,
            'rawOffset': 0,
            'timeZoneId': 'Etc/UTC',
            'timeZoneName': 'Coordinated Universal Time',
        } 

    tzInfo = data["observer"]["timezone"] 
    tzOffset = datetime.timedelta(
        seconds=(tzInfo["rawOffset"] + tzInfo["dstOffset"]))

    return ("""
<pre>
日     出: %s
日     落: %s
月     出: %s
月     落: %s
民用晨光始: %s
民用昏影终: %s
航海晨光始: %s
航海昏影终: %s
天文晨光始: %s
天文昏影终: %s
</pre>
    """ % (
        _dtRepr(data["heaven"]["sun"]["rising"], tzOffset=tzOffset),
        _dtRepr(data["heaven"]["sun"]["setting"], tzOffset=tzOffset),
        _dtRepr(data["heaven"]["moon"]["rising"], tzOffset=tzOffset), 
        _dtRepr(data["heaven"]["moon"]["setting"], tzOffset=tzOffset), 
        _dtRepr(data["observer"]["twilight"]["civil"]["begin"], tzOffset=tzOffset),
        _dtRepr(data["observer"]["twilight"]["civil"]["end"], tzOffset=tzOffset),
        _dtRepr(data["observer"]["twilight"]["nautical"]["begin"], tzOffset=tzOffset),
        _dtRepr(data["observer"]["twilight"]["nautical"]["end"], tzOffset=tzOffset),
        _dtRepr(data["observer"]["twilight"]["astronomical"]["begin"], tzOffset=tzOffset),
        _dtRepr(data["observer"]["twilight"]["astronomical"]["end"], tzOffset=tzOffset),
    )).strip(), tzInfo


# ---- Routine for generating a full report.

def report(lat, lng, maxDays=3):
    
    # -------- Fetch weather reports and prepare them for processing.
    
    url = "http://intell.neoatlantis.org/nwp/%f/%f/" % (lat, lng)
    q = requests.get(url)
    data = q.json()
    forecasts = sorted(
        [data["forecasts"][i] for i in data["forecasts"]],
        key=lambda i: i["forecast"]
    )
    for each in forecasts:
        each["forecast"] = strptime(each["forecast"])
        each["runtime"] = strptime(each["runtime"])
    metadata = data["metadata"]

    # -------- Fetch astronomical info on queried place, providing timezone and
    #          information on rise/set time of celestial bodies. Query will be
    #          fixed using averaged pressure and temperature given by weather
    #          forecasts.
    
    avgP, avgT = averagePressureAndTemperatureIn24hrs(forecasts)
    astroReport, tzInfo = astroData(\
        lat, lng, pressureFix=avgP, temperatureFix=avgT)
    tzOffset = datetime.timedelta(
        seconds=(tzInfo["rawOffset"] + tzInfo["dstOffset"]))

    # -------- Generate text report

    ret = ""
    ret += "请求地点: %s\n" %\
            translateCoordinates(metadata["queryCoordinates"])
    ret += "预报地点: %s\n" %\
            translateCoordinates(metadata["forecastCoordinates"])
    ret += "找到 %d 条预报。\n" % metadata["count"]
    ret += "\n本报告使用时区:\n  %s (%s%s)\n\n" % (
        _tzRepr(tzOffset),
        tzInfo["timeZoneId"],
        tzInfo["dstOffset"] != 0 and " 夏令时" or ""
    )

    ret += "**** <strong>日月及晨昏蒙影时刻</strong> ****\n"
    ret += astroReport 

    # All datetime are added with offsets, so that the splitting of days also
    # works. Datetimes are used here in native form(no internal timezone info
    # stored).

    for each in forecasts:
        each["forecast"] += tzOffset
        each["runtime"] += tzOffset

    currentDay = None
    dayCount = 0
    for forecast in forecasts:
        dayRepr = forecast["forecast"].timetuple()[0:3]
        if dayRepr != currentDay: # one new day. Print splitter.
            dayCount += 1
            if dayCount > maxDays:
                break
            ret += "\n"
            ret += "**** <strong>" +\
                _dateRepr(forecast["forecast"]) + "</strong> ****\n"
            currentDay = dayRepr
        ret += _dayForecast(forecast) + "\n"

    ret += "\n报告生成时间: %s\n\n" %\
        _dtRepr(datetime.datetime.utcnow(), tzOffset)
    ret += "气象数据来自 Deutscher Wetterdienst 并经过算法处理\n"
    ret += "时区数据来自 Google API"
    return ret 


if __name__ == "__main__":
    print(report(30, 120))
