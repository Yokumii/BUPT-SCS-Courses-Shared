#include <cstring>
#include <cctype>

bool isDomainName(const char* addr) {
    if (addr == nullptr || *addr == '\0') {
        return false;
    }

    if (std::strchr(addr, ':') != nullptr) {
        return false; // 是 IPv6 地址
    }
    
    for (const char* p = addr; *p != '\0'; ++p) {
        if (std::isalpha(static_cast<unsigned char>(*p))) {
            return true; // 是域名
        }
    }
    return false; // 是 IPv4 地址
}