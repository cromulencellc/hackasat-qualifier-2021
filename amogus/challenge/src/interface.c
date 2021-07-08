#include <fcntl.h>
#include <string.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <inttypes.h>
#include <netdb.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <errno.h>
#include <pthread.h>
#include <signal.h>
#include <openssl/sha.h>

#include "interface.h"

#define DEBUG 0

#if DEBUG
    #define LOG printf
#else
    #define LOG(...) while(0){}
#endif

#define NUM_VOTERS 3
#define SERVERPORT 31337
#define SOCKETERROR (-1)
#define MSG_SUCCESS 1
#define MSG_FAILURE 0
#define QUESTION_TIME 2
#define NEW_QUESTION_WAIT 1

int check(int ret, const char *err_s, int fatal);
char* recv_msg(int client_fd);
int welcome_voters();

InterfaceState state = STATE_AWAITING_RESPONSES;
Voter voters[NUM_VOTERS] = {0};
commitedvote current_commit = NULL;
genericmessage gmsg = NULL;

int log_fd = 1;

void timeout_func(int signo) {
    exit(-1);
}

void* ec_malloc(size_t sz){
    void *pt = NULL;

    if((pt = malloc(sz)) == NULL){
        perror("In malloc: ");
        exit(-1);
    }

    return pt;
}

void print_hash(char* hash){
    for (int i=0; i < 32; i++)
        LOG("%02X", hash[i] & 0xff);
    LOG("\n");
}

void sha256(char* input_hash, char* output_hash) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_CTX sha256;
    SHA256_Init(&sha256);
    SHA256_Update(&sha256, input_hash, 32);
    SHA256_Final(hash, &sha256);
    memcpy(output_hash, hash, 32);
}

int find_voter_index(char* hash){
    for (int i = 0; i < NUM_VOTERS; i++){
        if (!!strncmp(hash, voters[i].hash, 32) == 0){
            LOG("Found voter %d\n", i);
            return i;
        }
    }
    return -1;
}

void move_hash_forward(char* hash){
    LOG("Updating hash for voter\n");

    char temp[32];
    sha256(hash, temp);

    LOG("New hash: ");
    print_hash(temp);

    memcpy(hash, temp, 32);

    return;
}

// Listens for data and parses into a GenericMessage structure
GenericMessage* recv_data(int client_fd){
    int ret;

    // Recieve the header
    ret = recv(client_fd, &gmsg->header, sizeof(GenericMessageHeader), 0);
    if(ret <= 0){
        printf("Voter closed connection\n");
        return NULL;
    }
    if (ret != sizeof(GenericMessageHeader)){
        printf("Nefarious data received. Computer has been kicked from voting:%d\n", ret);
        exit(1);
    }
    LOG("\nServer got voter data: directive:%d msg_len:%d\n", gmsg->header.directive,  gmsg->header.len);
    for (int i=0; i < 32; i++)
        LOG("%02X", ((char*)gmsg)[i] & 0xff);
    LOG("\n");

    gmsg->bytes = NULL;

    if (gmsg->header.len > 0){
        // Allocate a message block on the heap
        gmsg->bytes = (char*)ec_malloc(gmsg->header.len);
        LOG("[?] gmsg bytes: %p\n", gmsg->bytes);

        ret = recv(client_fd, gmsg->bytes, gmsg->header.len, 0);

        if(ret <= 0 || ret != gmsg->header.len){
            printf("Nefarious data received. Computer has been kicked from voting:%d\n", ret);
            exit(1);
        }
    }

    return gmsg;
}

// Constructs a generic message
int send_message(int client_fd, char* msg, size_t size, VoterDirectives d, int voter_idx){
    GenericResponse m;

    m.header.directive = d;
    if(voter_idx == -1){
        memset((char*)&m + sizeof(m.header.directive), '\xFF', sizeof(voters[voter_idx].hash));
    }
    else{
        memcpy((char*)&m + sizeof(m.header.directive), voters[voter_idx].hash, sizeof(voters[voter_idx].hash));
    }

    m.header.len = size;

    memcpy((char*)&m + sizeof(GenericMessageHeader), msg, m.header.len);

    LOG("Sending message with length %d\n", m.header.len);
    for (int i=0; i < sizeof(GenericMessageHeader)+m.header.len; i++)
        LOG("%02X", ((char*)&m)[i] & 0xff);
    LOG("\n");

    int ret = send(client_fd, &m, sizeof(m) - (sizeof(m.response) - size), 0);

    return ret;
}

// Constructs a standard message response
int send_message_response(int client_fd, int s, int voter_idx){
    return send_message(client_fd, (char*)&s, sizeof(int), MSG_RESPONSE, voter_idx);
}

// Parses any voter message, and does the corresponding action
int parse_voter_message(int client_fd, GenericMessage* message){
    LOG("Parsing voter message!\n");
    int success = MSG_FAILURE, commit_happened = false;

    int idx = find_voter_index(message->header.key);
    if (idx < 0){
        LOG("Voter failed hash check, no voter found\n");
        message->header.directive = INVALID_DIRECTIVE;
    }

    switch (message->header.directive) {
        case VOTER_READY:
            LOG("Voter is READY and waiting for questions\n");
            // if (state == STATE_AWAITING_RESPONSES){
            if (1){
                if(!voters[idx].ready && voters[idx].answer){
                    free(voters[idx].answer);
                }

                voters[idx].ready = 1;

                success = MSG_SUCCESS;

                send_message_response(client_fd, success, idx);

                break; // dont send a default message response
            }
            break;
        case VOTER_VOTE:
            if (state == STATE_AWAITING_RESPONSES && voters[idx].hasvoted == 0){
                LOG("Voter voted with data:\n");
                for (int i=0; i < message->header.len; i++)
                    LOG("%02X", message->bytes[i] & 0xff);
                LOG("\n");

                // Double Free
                if(voters[idx].answer){
                    free(voters[idx].answer);
                }

                voters[idx].answer = (double*)ec_malloc(sizeof(double)*4);

                // Bad memcpy. Assumes that the size of the voter's answer is 24 bytes long
                // Initially meant as a heap leak, but the size is too small to be any sort of leak.
                memcpy(voters[idx].answer, message->bytes, sizeof(double)*4);

                if(!current_commit){
                    current_commit = (commitedvote)ec_malloc(sizeof(CommitedVote));
                }
                current_commit->answer = (double*)voters[idx].answer;
                commit_happened = true;

                voters[idx].hasvoted = true;

                success = MSG_SUCCESS;

                send_message_response(client_fd, success, idx);
            } else{
                LOG("Voter voted wrong! (length or state) | State: %d | Voted: %d \n", state, voters[idx].hasvoted);
                send_message_response(client_fd, success, idx);
            }
            break;
        case VOTER_LOG_CACHE:
            LOG("Voter caching log message with len %d: %s\n", message->header.len, message->bytes);

            if(voters[idx].log_i == 10){    // Backlog too large
                LOG("Too many logs...\n");
                send_message_response(client_fd, success, idx);
                break;
            }

            if(message->header.len > 0){
                voters[idx].logs[voters[idx].log_i].log = (char*)ec_malloc(message->header.len);

                memcpy(voters[idx].logs[voters[idx].log_i].log, message->bytes, message->header.len);

                voters[idx].logs[voters[idx].log_i].log_sz = message->header.len;
                voters[idx].log_i++;    // Iterate to next free log

                success = MSG_SUCCESS;
            }

            send_message_response(client_fd, success, idx);

            break;
        case VOTER_LOG_SAVE:
            if(voters[idx].log_i == 0){ // No logs saved
                LOG("No logs in cache to save...\n");
                break;
            }

            voters[idx].log_i--;

            size_t msg_sz = 0;

            // If their log is initialized then write it to the log file and send back a message with the total
            // # of bytes written to the log file.
            if(voters[idx].logs[voters[idx].log_i].log){
                msg_sz = write(log_fd, voters[idx].logs[voters[idx].log_i].log, voters[idx].logs[voters[idx].log_i].log_sz);
                success = MSG_SUCCESS;

                free(voters[idx].logs[voters[idx].log_i].log);
            }
            else
                break;

            send_message(client_fd, (char*)&msg_sz, sizeof(int), MSG_RESPONSE, idx);
    }

    if (success == MSG_SUCCESS)
        move_hash_forward(voters[idx].hash);

    free(message->bytes);

    message->bytes = NULL;

    return commit_happened;
}

int check(int ret, const char *err_s, int fatal){
    // TODO: Shouldn't be socket error. Must be more generic
    if(ret == SOCKETERROR){
        perror(err_s);
        if(fatal){
            LOG("check failed");
            exit(EXIT_FAILURE);
        }
    }
    return ret;
}

void *socket_listen_loop(void* pose_new_question){
    struct sockaddr_in server, client;
    socklen_t client_len = sizeof(client);
    fd_set active_fd_set, read_fd_set;
    int sock, connection = 0;
    const int opt = 1;

    gmsg = (genericmessage)malloc(sizeof(GenericMessage));

    LOG("Starting server on port %d\n", SERVERPORT);

    sock = check(socket(AF_INET, SOCK_STREAM, 0), "Creating socket failed\n", true);
    setsockopt(sock, SOL_SOCKET, (SO_REUSEPORT | SO_REUSEADDR| SO_DEBUG), &opt, sizeof(opt));

    server.sin_family      = AF_INET;
    server.sin_port        = htons(SERVERPORT);
    server.sin_addr.s_addr = INADDR_ANY;

    check(bind(sock, (struct sockaddr *)&server, (socklen_t)sizeof(server)), "Bind failed", true);
    
    if (listen(sock, 3) < 0){
        perror("listen");
        exit(1);
    }

    FD_ZERO(&active_fd_set);
    FD_SET(sock, &active_fd_set);

    question q = (question)pose_new_question;

    // pthread_create(&ask_thread, NULL, ask_question, (void*)q);

    while(1){
        read_fd_set = active_fd_set;

        if (select(FD_SETSIZE, &read_fd_set, NULL, NULL, NULL) < 0){
            perror("Failure on select");
            exit(1);
        }

        // Shamelessly copied from gnu.org multiple connection server
        for (int i = 0; i < FD_SETSIZE; ++i) {
            if (FD_ISSET(i, &read_fd_set)) { // if bit i in read_fd_set is valid
                if (i == sock) {
                    /* Connection request on original socket. */
                    int newfd = accept(sock, (struct sockaddr *) &client, &client_len);
                    if (newfd < 0){
                        perror ("Failure on accept");
                        exit (1);
                    }

                    LOG("Server: voter connect from host %s\n", inet_ntoa(client.sin_addr));

                    FD_SET(newfd, &active_fd_set);
                    if(connection < 3){
                        q->connections[connection++] = newfd;
                    }
                } else {
                    GenericMessage* m = recv_data(i);
                    if (m == NULL){
                        // As we get a new connection, add it to our fd socket list that we 
                        // use to send out question-ready status to voters
                        for(int j = 0; j < 3; j++){
                            if(q->connections[j] == i){
                                q->connections[j] = 0;
                                connection--;
                            }
                        }
                        close(i);
                        FD_CLR(i, &active_fd_set);
                    } else{
                        if(parse_voter_message(i, m)){  // If there's a new commit send it to everyone
                            // sleep(0.001);
                            sleep(0.1);
                            for(int j = 0; j < 3; j++){
                                if(q->connections[j] > 0){
                                    send_message(q->connections[j], (char*)current_commit->answer, sizeof(double)*4, VOTER_VOTE, -1);
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return NULL;
}

// Runs the logic of the interface
void interface(question q){

    double* d = NULL;
    uint32_t voter_count = 0;

    // This file contains pregenerated sim data from pedant's filter challenge from HAS1. Ty Obama. I mean pedant.
    FILE *fp = fopen("startrack_sim.i2c", "r");
    if(fp == NULL){
        perror("Could not open interface to startracker\n");
        exit(-1);
    }

    int n_count = 0;

    double quat[4] = {0.0, 0.0, 0.0, 0.0}; // Quaterion that we're posing as a question
    char st_data[65] = {0};                // Max line length should be 64
    char *ret = NULL;

    sleep(5);   // Initial sleep on this thread to make sure we're connected by all the voters first before we start
    while(true){

        ret = fgets(st_data, 65, fp);
        
        if(ret == NULL){
            printf("ERROR: Got EOF or error on read... Exiting\n");
            exit(-1);
        }

        n_count = sscanf(st_data, "%lf, %lf, %lf, %lf", quat, quat+1, quat+2, quat+3);

        if(n_count < 4){
            printf("ERROR: Got less nums than expected. Exiting...\n");
            exit(-1);
        }

        // Set voters to not voted before we send out the question
        for(int i = 0; i < NUM_VOTERS; i++){
            voters[i].hasvoted = false;
        }

        state = STATE_AWAITING_RESPONSES;

        // Give each voter the question
        for(int i = 0; i < NUM_VOTERS; i++){
            if(q->connections[i] > 0){
                send_message(q->connections[i], (char*)quat, sizeof(quat), POSE_QUESTION, -1);
            }
        }

        // Start responding to VOTER_READY with the question
        // Wait for specified amount of time for voters to calculate and vote
        printf("Interface is waiting %d seconds for voters to vote!\n", QUESTION_TIME);

        sleep(QUESTION_TIME);

        // Stop recieving reponses

        for(int voter_index = 0; voter_index < NUM_VOTERS; voter_index++){
            if(voters[voter_index].hasvoted && voters[voter_index].answer){
                voter_count++;
            }
        }

        // minor race condition here 

        // Give the last voter time to vote
        if(voter_count == 2){
            state = STATE_AWAITING_RESPONSES;
            sleep(0.1);
        }
        voter_count = 0;
        state = STATE_FINISHED;

        for (int voter_index = 0; voter_index < NUM_VOTERS; voter_index++){
            if(voters[voter_index].hasvoted && voters[voter_index].answer){
                d = voters[voter_index].answer;
                LOG("Voter[%d] voted: [%.5f %.5f %.5f]\n", voter_index, d[0], d[1], d[2]);
            }
        }

        if(current_commit){
            LOG("Committed answer: [%.5f %.5f %.5f %.5f]\n", current_commit->answer[0], current_commit->answer[1], current_commit->answer[2], current_commit->answer[3]);
        }

        sleep(NEW_QUESTION_WAIT);
    }
}

int main(int argc, char **argv){
    
    if(argc > 1){
        // Log file will default to 1 (stdout)
        log_fd = open(argv[1], O_RDWR);
        if(log_fd < 0){
            perror("While opening log file\n");
            exit(-1);
        }
    }

    // Shamelessly stolen from pedant
    int timeout = 300;
    char *timeout_str = getenv("TIMEOUT");
    if (timeout_str) {
        timeout = atoi(timeout_str);
    }
    signal(SIGALRM, timeout_func);
    alarm(timeout+2);
    signal(SIGPIPE, SIG_IGN);

    // new_question: are we ready to ask voters new question. No longer used (removed with mutex stuff)
    // connections: array of fds for each of the sockets to the voters
    int new_question = false, connections[3] = {0};

    // Was used to handle part of threads at some point. Took it out because it was too complicated for the challenge
    struct Question q = {
        .new_question  = &new_question,
        .connections   = connections,
        .question_cond = PTHREAD_COND_INITIALIZER,
        .lock          = PTHREAD_MUTEX_INITIALIZER
    };
    
    // Initialize the keys
    memset(voters, 0, sizeof(voters));
    memcpy(voters[0].hash, getenv("KEY1"), 32);
    memcpy(voters[1].hash, getenv("KEY2"), 32);
    memcpy(voters[2].hash, getenv("KEY3"), 32);

    pthread_t socketserver;
    pthread_create(&socketserver, NULL, &socket_listen_loop, (void*)&q);

    LOG("Main loop continuing after socket server has started!\n");

    interface(&q);

    LOG("Exiting...\n");
}