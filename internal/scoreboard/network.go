package scoreboard

import (
	"net"
	"sort"
	"strings"
)

// NetworkAddress is a possible Companion destination on the same trusted LAN.
// The address is returned only to a local browser, never remote API clients.
type NetworkAddress struct {
	Name      string `json:"name"`
	IP        string `json:"ip"`
	Preferred bool   `json:"preferred"`
}
type NetworkInterfaces struct {
	PreferredIP string           `json:"preferred_ip"`
	Interfaces  []NetworkAddress `json:"interfaces"`
}

func isUsablePrivateIPv4(ip net.IP) bool {
	x := ip.To4()
	if x == nil || x.IsLoopback() || x.IsLinkLocalUnicast() || x.IsUnspecified() {
		return false
	}
	// Private LAN plus Tailscale/CGNAT overlay destinations (100.64.0.0/10).
	return x.IsPrivate() || (x[0] == 100 && x[1] >= 64 && x[1] <= 127)
}
func detectNetworkInterfaces() NetworkInterfaces {
	out := NetworkInterfaces{Interfaces: []NetworkAddress{}}
	// UDP dialing doesn't send packets; it only asks the OS for the selected route.
	// If offline, users can pick an available private interface manually.
	preferred := ""
	if conn, err := net.Dial("udp4", "1.1.1.1:53"); err == nil {
		if u, ok := conn.LocalAddr().(*net.UDPAddr); ok && isUsablePrivateIPv4(u.IP) {
			preferred = u.IP.String()
		}
		_ = conn.Close()
	}
	interfaces, _ := net.Interfaces()
	for _, iface := range interfaces {
		if iface.Flags&net.FlagUp == 0 || iface.Flags&net.FlagLoopback != 0 {
			continue
		}
		addrs, err := iface.Addrs()
		if err != nil {
			continue
		}
		for _, a := range addrs {
			var ip net.IP
			switch x := a.(type) {
			case *net.IPNet:
				ip = x.IP
			case *net.IPAddr:
				ip = x.IP
			}
			if !isUsablePrivateIPv4(ip) {
				continue
			}
			candidate := NetworkAddress{Name: strings.TrimSpace(iface.Name), IP: ip.To4().String()}
			if candidate.Name == "" {
				candidate.Name = "Network adapter"
			}
			candidate.Preferred = candidate.IP == preferred
			out.Interfaces = append(out.Interfaces, candidate)
		}
	}
	sort.SliceStable(out.Interfaces, func(i, j int) bool {
		a, b := out.Interfaces[i], out.Interfaces[j]
		if a.Preferred != b.Preferred {
			return a.Preferred
		}
		// Physical Ethernet/WiFi is usually a better starting point than VPN,
		// but keep every selectable candidate for field network changes.
		vpn := func(n string) bool {
			n = strings.ToLower(n)
			return strings.Contains(n, "tail") || strings.Contains(n, "tun") || strings.Contains(n, "tap") || strings.Contains(n, "vpn") || strings.Contains(n, "docker") || strings.Contains(n, "veth")
		}
		if vpn(a.Name) != vpn(b.Name) {
			return !vpn(a.Name)
		}
		return a.Name < b.Name
	})
	if len(out.Interfaces) > 0 {
		out.PreferredIP = out.Interfaces[0].IP
	}
	return out
}
