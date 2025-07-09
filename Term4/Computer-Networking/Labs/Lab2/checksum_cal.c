#include <stdio.h>
#include <stdint.h>

// 计算 IPv4 报文头部的校验和
uint16_t calculate_checksum(uint16_t *data, int length) {
    uint32_t sum = 0;

    for (int i = 0; i < length; i++) {
        sum += data[i];
        // 如果加和超过 16 位，就把高位加回来（模拟 one’s complement sum）
        if (sum > 0xFFFF) {
            sum = (sum & 0xFFFF) + 1;
        }
    }

    // 按位取反，得到最终校验和
    return ~sum & 0xFFFF;
}

int main() {
    // 示例：10 个 16-bit 的 IPv4 报文头（十六进制表示）
    uint16_t ip_header[] = {
        0x4500,
        0x0274,
        0xC532,
        0x039D,
        0x4001,
        0x0000,  // Checksum 字段应设为 0
        0x0A1D,
        0xA91B,
        0x0A03,
        0x1302
    };

    int length = sizeof(ip_header) / sizeof(ip_header[0]);
    uint16_t checksum = calculate_checksum(ip_header, length);

    printf("IPv4 header checksum: 0x%04x\n", checksum);
    return 0;
}