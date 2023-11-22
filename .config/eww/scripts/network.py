#!/bin/python
from subprocess import check_output, CalledProcessError, run, DEVNULL
import json
from argparse import ArgumentParser
import time

def get_active_ssid():
    active = ["nmcli", "-t", "-f", "ssid,active", "device", "wifi"]
    res = check_output(active).decode().strip()

    ssid = None
    for entry in res.split("\n"):
        entry = entry.split(":")
        if entry[-1] == "yes":
            ssid = ":".join(entry[:-1])
            break

    return ssid

def get_known():
    known = ["nmcli", "-t", "-f", "name", "connection"]
    res = check_output(known).decode().strip().split("\n")

    return set(res)


def get_available(rescan=False):
    scan = ["nmcli", "-t", "-f", "ssid,security,signal", "device", "wifi", "list"]

    if rescan:
        scan += ["--rescan", "yes"]

    res = check_output(scan).decode().strip().split("\n")

    seen_ssids = set()
    networks = {}
    known = get_known()

    for entry in res:
        entry = entry.split(":")

        signal = int(entry[-1])
        security = entry[-2]
        ssid = ":".join(entry[:-2])

        # If we have seen the network before, update it's signal strength
        if ssid in seen_ssids:
            networks[ssid]["signal"] = max(
                networks[ssid]["signal"], 
                signal
            )
            continue

        seen_ssids.add(ssid)

        networks[ssid] = {
                "signal": signal,
                "security": security,
                "known": ssid in known
            }
    
    # Flatten into array for output
    out = [
        {
            "ssid": key, 
            "signal": val["signal"], 
            "security": val["security"],
            "known": val["known"]
        } for key, val in networks.items()
    ]

    return json.dumps(out)

def connect(ssid, password=None):
    if get_active_ssid() == ssid:
        disconnect = ["nmcli", "device", "disconnect", "wlan0"]
        check_output(disconnect)
        return

    connect = ["nmcli", "device", "wifi", "connect", ssid]

    if password is not None:
        connect += ["password", password]

    try:
        check_output(connect, stderr=DEVNULL)
        with open("/home/kenzie/log.log", "a") as f:
            f.write("connect")

    except CalledProcessError:
        remove = ["nmcli", "connection", "delete", ssid]

        check_output(remove)
        with open("/home/kenzie/log.log", "a") as f:
            f.write("remove")

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--close", action="store_true")

    subparsers = parser.add_subparsers(dest="action")

    parser_active = subparsers.add_parser("active")

    parser_list = subparsers.add_parser("list")
    parser_list.add_argument("--rescan", action="store_true")

    parser_connect = subparsers.add_parser("connect")
    parser_connect.add_argument("ssid")
    parser_connect.add_argument("--password", action="store")

    res = ""
    args = parser.parse_args()


    if args.action == "active":
        res = get_active_ssid()
        print(res)

    elif args.action == "list":
        res = get_available(rescan=args.rescan)
        print(res)

    elif args.action == "connect":
        res = connect(args.ssid, password=args.password)

    if args.close:
        try:
            close    = ["eww", "close", "network_list_window"]
            check_output(close, stderr=DEVNULL)

            update = ["eww", "update", "display_network_list=false"]
            check_output(update, stderr=DEVNULL)
        except CalledProcessError:
            pass

        selected = ["eww", "update", "selected_network=false"]
        check_output(selected)

    exit()
