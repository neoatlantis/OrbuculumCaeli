#!/usr/bin/env python3

import requests
import datetime
import struct

##############################################################################

strptime = lambda i: datetime.datetime.strptime(i, "%Y-%m-%dT%H:%M:%SZ")

def _dtRepr(dt, tzOffset, short=False):
    if type(dt) == str: dt = strptime(dt)
    if short:
        return "%02d:%02d" % (dt+tzOffset).timetuple()[3:5]
    else:
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
        lvl = lvls.index((name, smin, smax))
        if ws >= smin and ws < smax:
            if lvl > 0:
                return "%d级(%s)" % (lvl, name)
            else:
                return name
    return "风力未知"

def _wmoRepr(wmo):
    msg = {
        1: '云在消散', 2: '云量不变', 3: '云在形成',

        40: "远处有雾", 41: "团雾", 42: "雾在消散", 43: "浓雾在消散", 44: "雾",
        45: "浓雾", 46: "雾在变浓", 47: "浓雾变浓", 48: "雾且有霜", 49:
        "浓雾有霜",

        50: "时有轻微毛毛雨", 51: "持续轻微毛毛雨", 52: "时有中等毛毛雨", 53:
        "持续中等毛毛雨", 54: "时有强烈毛毛雨", 55: "持续强烈毛毛雨", 56:
        "轻微冻毛毛雨", 57: "中等或强烈冻毛毛雨", 58: "轻微毛毛雨伴随小雨", 59:
        "中等或强烈毛毛雨伴随降雨",

        60: "时有小雨", 61: "持续小雨", 62: "时有中雨", 63: "持续中雨", 64:
        "时有大雨", 65: "持续大雨", 66: "时有冻雨小雨", 67: "中等或强烈冻雨",
        68: "轻微雨夹雪", 69: "中等或强烈雨夹雪",

        70: "偶有小雪", 71: "持续小雪", 72: "时有中雪", 73: "持续中雪", 74:
        "时有大雪", 75: "持续大雪", 76: "霰", 77: "冰晶", 78: "冰粒",
        
        80: "轻微阵雨", 81: "中等或强烈阵雨", 82: "极强烈阵雨", 83:
        "轻微阵雨夹雪", 84: "中等或强烈阵雨夹雪", 85: "轻微阵雪", 86:
        "中等或强烈阵雪", 87: "轻微霰雪", 88: "中等或强烈霰雪", 89: "轻微冰雹",
        90: "中等或强烈冰雹",
        
        91: "雷电伴随小雨", 92: "雷电伴随中雨或大雨", 93: "雷电伴随固态降水",
        94: "强烈雷电伴随固态降水", 95: "轻微雷雨或雪", 96: "轻微雷雨伴随冰雹",
        97:"强烈雷电和雨雪", 98: "强烈雷雨伴随沙暴", 99: "雷雨伴随冰雹"
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
    return "%d m\u3374" % (p / 100.0)

def _dayForecast(forecast):
    ret = ""

    ret += _hourRepr(forecast["forecast"]) + " "
    ret += _tempRepr(forecast["t_2m"]) + " ,"
    #ret += _pRepr(forecast["p_surface"]) + ","
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

    filltime = lambda i:\
        _dtRepr(i, tzOffset=tzOffset, short=True) if i != None else "不适用"
    return ("""
<pre>
日出 %s 日落 %s
月出 %s 月落 %s
天文晨光始 %s 昏影终 %s
航海晨光始 %s 昏影终 %s
民用晨光始 %s 昏影终 %s
</pre>
    """ % (
        filltime(data["heaven"]["sun"]["rising"]),
        filltime(data["heaven"]["sun"]["setting"]),
        filltime(data["heaven"]["moon"]["rising"]), 
        filltime(data["heaven"]["moon"]["setting"]), 
        filltime(data["observer"]["twilight"]["astronomical"]["begin"]),
        filltime(data["observer"]["twilight"]["astronomical"]["end"]),
        filltime(data["observer"]["twilight"]["nautical"]["begin"]),
        filltime(data["observer"]["twilight"]["nautical"]["end"]),
        filltime(data["observer"]["twilight"]["civil"]["begin"]),
        filltime(data["observer"]["twilight"]["civil"]["end"]),
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
