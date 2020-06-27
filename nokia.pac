function FindProxyForURL(url, host)
{
    url  = url.toLowerCase();
    host = host.toLowerCase();

    if (shExpMatch(host, "*.nokia*") || shExpMatch(host, "*.nsn*")) {
        return "PROXY 127.0.0.1:443";
    }
    return "DIRECT";
}
