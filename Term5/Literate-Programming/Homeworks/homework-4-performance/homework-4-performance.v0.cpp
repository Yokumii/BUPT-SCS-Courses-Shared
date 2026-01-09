#include <cstring>
#include <cctype>

/**
 * 判断字符串是否为域名
 * 已知输入只有三种可能：IPv4地址、IPv6地址、域名
 * 
 * @param addr 待判断的地址字符串
 * @return true 如果是域名，false 如果是IP地址
 */
bool isDomainName(const char* addr) {
    if (addr == nullptr || *addr == '\0') {
        return false;
    }
    
    int len = std::strlen(addr);
    
    // IPv6地址包含冒号
    for (int i = 0; i < len; i++) {
        if (addr[i] == ':') {
            return false;  // 是IPv6地址
        }
    }
    
    // 检查是否为IPv4地址
    // IPv4地址只包含数字和点
    bool hasLetter = false;
    
    for (int i = 0; i < len; i++) {
        if (std::isalpha(static_cast<unsigned char>(addr[i]))) {
            hasLetter = true;
            break;
        }
    }
    
    // 如果没有字母，可能是IPv4地址，需要进一步验证
    if (!hasLetter) {
        // 简单检查：IPv4有3个点，且都是数字
        int dots = 0;
        int digitCount = 0;
        bool allValid = true;
        
        for (int i = 0; i < len; i++) {
            if (addr[i] == '.') {
                dots++;
                if (digitCount == 0 || digitCount > 3) {
                    allValid = false;
                    break;
                }
                digitCount = 0;
            } else if (std::isdigit(static_cast<unsigned char>(addr[i]))) {
                digitCount++;
            } else {
                allValid = false;
                break;
            }
        }
        
        // 最后一段也要检查
        if (digitCount == 0 || digitCount > 3) {
            allValid = false;
        }
        
        // 如果有3个点且格式正确，是IPv4
        if (dots == 3 && allValid) {
            return false;  // 是IPv4地址
        }
    }
    
    // 否则是域名
    // 域名包含字母、数字、连字符和点
    for (int i = 0; i < len; i++) {
        char c = addr[i];
        if (!std::isalnum(static_cast<unsigned char>(c)) && c != '.' && c != '-' && c != '_') {
            return false;  // 包含非法字符
        }
    }
    
    return true;  // 是域名
}

