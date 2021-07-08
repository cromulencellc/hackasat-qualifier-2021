#ifndef INTERFACE_H
#define INTERFACE_H

typedef struct GenericMessageHeader {
    unsigned int directive;
    char key[32];
    unsigned int len;
} GenericMessageHeader;

typedef struct GenericResponse{
    GenericMessageHeader header;
    double response[7];
} GenericResponse;

typedef struct GenericMessage {
	GenericMessageHeader header;
	char* bytes;
} GenericMessage;

typedef struct GenericMessage* genericmessage;

typedef struct CommitedVote{
    int voter;
    double *answer;
} CommitedVote;

typedef struct CommitedVote* commitedvote;
typedef struct Question* question;

struct Question{
    pthread_cond_t question_cond;
    pthread_mutex_t lock;
    int *new_question;
    int *connections;
    int *new_commit;
};

struct Log {
    size_t log_sz;
    char* log;
};

typedef struct Log* log_p;

typedef struct Voter {
    int ready;
    int hasvoted;
    char hash[32];
    struct Log logs[10];
    double *answer;
    int log_i;
} Voter;

typedef enum VoterDirectives {
    POSE_QUESTION = 0,
    VOTER_VOTE = 1,
    MSG_RESPONSE = 2,
    VOTER_LOG_CACHE = 3,
    VOTER_LOG_SAVE = 4,
    VOTER_READY = 5,
   	INVALID_DIRECTIVE = 99,
} VoterDirectives;

typedef enum InterfaceState {
    STATE_INIT = 0,
    STATE_AWAITING_RESPONSES = 1,
    STATE_FINISHED = 2,
} InterfaceState;

#endif