#include <cstring>
#include <cctype>

/**
 * 判断字符串是否为域名
 * 核心假设：输入字符串保证是以下三种合法格式之一：
 * 1. 合法的 IPv4 地址 (只含数字和点)
 * 2. 合法的 IPv6 地址 (含冒号, 可能含字母 a-f)
 * 3. 合法的 域名 (含字母、数字、点等，且不含冒号)
 *
 * @param addr 待判断的地址字符串
 * @return true 如果是域名，false 如果是IP地址
 */
bool isDomainName(const char* addr) {
    if (addr == nullptr || *addr == '\0') {
        return false;
    }
    
    bool hasLetter = false;
    
    // 遍历字符串，优先检查 IPv6 的最高优先级特征：冒号
    for (const char* p = addr; *p != '\0'; ++p) {
        char c = *p;
        
        // 1. 如果包含冒号 ':', 则一定是 IPv6 地址 (IP地址)
        // 必须优先判断冒号，以处理包含字母 a-f 的 IPv6 情况。
        if (c == ':') {
            return false; // 是 IPv6 地址
        }
        
        // 2. 记录是否存在字母 (用于区分 IPv4 和域名)
        if (std::isalpha(static_cast<unsigned char>(c))) {
            hasLetter = true;
        }
    }
    
    // 执行到这里，字符串**不是 IPv6 地址** (不含冒号)。
    
    // 3. 检查是否为域名
    if (hasLetter) {
        // 如果包含字母，且不是 IPv6，根据前提**它一定是域名**。
        // （因为合法的 IPv4 不含字母）
        return true; 
    }
    
    // 4. 否则，它既不是 IPv6 (无冒号)，也不是域名 (无字母)。
    // 根据前提，它只能是合法的 IPv4 地址 (只包含数字和点)。
    return false; // 是 IPv4 地址
}