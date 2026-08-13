"""
Utility for building and sending Wake-on-LAN "magic packets".

No third-party dependencies required - uses only the standard library.
"""
import re
import socket

MAC_RE = re.compile(r'^([0-9A-Fa-f]{2}[:\-]?){5}([0-9A-Fa-f]{2})$')


def normalize_mac(mac_address):
    """
    Strip separators and return a clean, lowercase, colon-separated MAC
    address, e.g. "AA-BB-CC-DD-EE-FF" -> "aa:bb:cc:dd:ee:ff".

    Raises ValueError if the input isn't a valid MAC address.
    """
    cleaned = re.sub(r'[.\-:\s]', '', mac_address or '')
    if len(cleaned) != 12 or not re.fullmatch(r'[0-9A-Fa-f]{12}', cleaned):
        raise ValueError(f'"{mac_address}" is not a valid MAC address')
    cleaned = cleaned.lower()
    return ':'.join(cleaned[i:i + 2] for i in range(0, 12, 2))


def is_valid_mac(mac_address):
    try:
        normalize_mac(mac_address)
        return True
    except ValueError:
        return False


def build_magic_packet(mac_address):
    """Build the raw bytes of a Wake-on-LAN magic packet for the given MAC."""
    hex_mac = normalize_mac(mac_address).replace(':', '')
    mac_bytes = bytes.fromhex(hex_mac)
    return b'\xff' * 6 + mac_bytes * 16


def send_magic_packet(mac_address, broadcast_ip='255.255.255.255', port=9):
    """
    Send a Wake-on-LAN magic packet as a UDP broadcast.

    mac_address: the target device's MAC address (any common format)
    broadcast_ip: the broadcast address to send to (e.g. 255.255.255.255
                  or a subnet-specific broadcast address like 192.168.1.255)
    port: UDP port to send to (7 or 9 are conventional)
    """
    packet = build_magic_packet(mac_address)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(packet, (broadcast_ip, int(port)))
    finally:
        sock.close()

    return packet
