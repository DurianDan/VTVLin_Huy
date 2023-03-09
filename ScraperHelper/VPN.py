import subprocess
from typing import Literal

_VPN_PROVIDERS = Literal["hotspotshield", "nordvpn","protonvpn"]

class VPN_helper():
    def __init__(self,
                 vpn_provider:_VPN_PROVIDERS) -> None:
        self.provider = vpn_provider
    
    def autoConnect(self,ouput=True):
        if self.provider == "nordvpn":
            connect_handle = self.NordVPNconnect(capture_output=ouput)
            return formatVPNmessage(message=connect_handle, vpn_provider=self.provider)

    def NordVPNconnect(self,
                       capture_output=True):
        connect = subprocess.run(
                    "nordvpn c".split(), capture_output= capture_output
                )
        if capture_output:
            return connect.stdout
        else:
            return "NordVPN Connect Successfully"

class formatVPNmessage():
    def __init__(self,
                 message:bytes,
                 vpn_provider:_VPN_PROVIDERS
                 ) -> None:
        self.provider = vpn_provider
        self.message = message.decode("utf8")
    def autoFormat(self):
        if self.provider == "nordvpn":
            return self.NordVPN()
    def NordVPN(self):
        message_parts = self.message.split("\r")
        formated_output = ""
        for part in message_parts:
            if len(part)>4:
                formated_output += f"\n{part}"
        return formated_output.strip()