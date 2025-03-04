#include <iostream>
#include <cstring>
#include <chrono>
#include <openssl/hmac.h>
#include <openssl/evp.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

#define PORT 8080
#define KEY "secret_key"

// Generate HMAC for a given message
std::string generate_hmac(const std::string& message) {
    unsigned char* digest;
    unsigned int len = 0;
    digest = HMAC(EVP_sha256(), KEY, strlen(KEY), (unsigned char*)message.c_str(), message.length(), nullptr, &len);
    return std::string(reinterpret_cast<char*>(digest), len);
}

// Send message with HMAC over a socket
void send_message(const std::string& message) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in server_addr{};
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    inet_pton(AF_INET, "127.0.0.1", &server_addr.sin_addr);
    
    connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr));
    std::string hmac = generate_hmac(message);
    std::string payload = message + ":" + hmac;
    send(sock, payload.c_str(), payload.length(), 0);
    close(sock);
}

// Receive message and validate HMAC
void receive_message() {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    sockaddr_in server_addr{};
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    server_addr.sin_addr.s_addr = INADDR_ANY;
    bind(server_fd, (struct sockaddr*)&server_addr, sizeof(server_addr));
    listen(server_fd, 1);
    
    int client_sock = accept(server_fd, nullptr, nullptr);
    char buffer[1024] = {0};
    read(client_sock, buffer, sizeof(buffer));
    close(client_sock);
    close(server_fd);
    
    std::string received(buffer);
    size_t sep = received.find(":");
    if (sep == std::string::npos) return;
    std::string msg = received.substr(0, sep);
    std::string hmac = received.substr(sep + 1);
    
    if (generate_hmac(msg) == hmac) std::cout << "HMAC Verified: " << msg << "\n";
    else std::cout << "HMAC Verification Failed\n";
}

// Benchmark the HMAC generation process
void benchmark_hmac() {
    std::string test_msg = "Benchmark Test";
    auto start = std::chrono::high_resolution_clock::now();
    for (int i = 0; i < 1000; ++i) generate_hmac(test_msg);
    auto end = std::chrono::high_resolution_clock::now();
    std::cout << "HMAC Generation Time: " 
              << std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() 
              << " ms\n";
}

int main() {
    benchmark_hmac();
    return 0;
}