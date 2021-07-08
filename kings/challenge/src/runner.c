#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <strings.h>
#include <sys/types.h>
#include <sys/time.h>
#include <errno.h>
#include <sys/poll.h>
#include <sys/wait.h> 
#include <signal.h>
#include <fcntl.h> 

#include <sys/socket.h>
#include <netinet/in.h>

void error(char *msg) {
    perror(msg);
    exit(1);
}

void timeout_func(int signo) {
    exit(-1);
}

int setup_socket_server(int type, short port) {
  int server_fd;
  struct sockaddr_in serv_addr; 

  server_fd = socket(AF_INET, type, 0);
  if (server_fd < 0) 
    error("ERROR opening socket");
  
  bzero((char *) &serv_addr, sizeof(serv_addr));
  
  serv_addr.sin_family = AF_INET;
  serv_addr.sin_port = htons(port);
  serv_addr.sin_addr.s_addr = INADDR_ANY;
  
  int enable = 1;
  if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int)) < 0)
      error("setsockopt(SO_REUSEADDR) failed");

  if (bind(server_fd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0)
    error("ERROR on binding");

  return server_fd;
}


int main(int argc, char *argv[]) {
    struct pollfd fds[3];
    int stdinfd[2];
    int stdoutfd[2];
    
    struct sockaddr_in tcp_addr;
    int tcplen = sizeof(tcp_addr);

    int tcpserver_fd = setup_socket_server(SOCK_STREAM, 54321);
    listen(tcpserver_fd, 1);

    int nfds = 2;
    bzero(fds, sizeof(fds));

    fds[0].fd     = tcpserver_fd;
    fds[0].events = POLLIN;

    pipe(stdinfd);
    pipe(stdoutfd);

    fds[1].fd     = stdoutfd[0];
    fds[1].events = POLLIN;

    pid_t cpid = fork(); 
    if (cpid == 0) {
        close(stdinfd[1]);
        close(stdoutfd[0]); 
        dup2(stdinfd[0], 0);
        dup2(stdoutfd[1], 1);
        execl("/challenge/challenge", "/challenge/challenge", (char *)NULL);
    }

    close(stdinfd[0]);
    close(stdoutfd[1]);

    int exfd = open("/challenge/exploit.bin", O_RDONLY);
    char *buff = malloc(0x2000);
    int len = read(exfd, buff, 0x2000);
    write(stdinfd[1], buff, len);
    int total = 0;
    int bytesRead = 0;
    while (total < 64) {
        bytesRead = read(stdoutfd[0], buff+total, 64-total);
        total += bytesRead;
        if (bytesRead == 0){
            return 0;
        }
    }
    buff[64] = 0;
    fprintf(stderr, "%s\n", buff);
    // Data coming in from cFS

    int timeout = 300;
    char *timeout_str = getenv("TIMEOUT");
    if (timeout_str) {
        timeout = atoi(timeout_str);
    }
    signal(SIGALRM, timeout_func);
    alarm(timeout+2);

    signal(SIGPIPE, SIG_IGN);

    while (!waitpid(cpid, NULL, WNOHANG))
    { 
        if (poll(fds, nfds, -1) < 0) {
            error("Poll Failed");
        }
        if (fds[0].revents == POLLIN) {
            if (fds[2].fd != -1) {
                close(fds[2].fd);
                bzero(&fds[2], sizeof(struct pollfd));

                fds[2].fd = -1;
                nfds = 2;
            }

            fds[2].fd = accept(tcpserver_fd, (struct sockaddr *) &tcp_addr, &tcplen);
            if (fds[2].fd < 0) {
                fds[2].fd = -1;
                error("ERROR on accept");
            }
            fds[2].events = POLLIN;
            nfds = 3;
        }
        if (fds[1].revents == POLLIN) { 
            // child stdout to /dev/stdout
            char b;
            read(fds[1].fd, &b, 1);
            if (b == EOF) {
                fprintf(stderr, "Client closed pipe\n");
                break;
            }
            send(fds[2].fd, &b, 1, 0);
        }
        if (fds[2].revents == POLLIN) {  
            // /dev/stdin to child stdin
            char b; 
            recv(fds[2].fd, &b, 1, 0);
            if (-1 == write(stdinfd[1], &b, 1)) {
                fprintf(stderr, "Client closed pipe\n");
                break;
            }
        }
    }

    close(stdinfd[1]);
    close(stdoutfd[0]); 
    close(fds[0].fd);
    close(fds[1].fd);
    if (fds[2].fd != -1) {
        close(fds[2].fd);
    }

    return 0;
}











