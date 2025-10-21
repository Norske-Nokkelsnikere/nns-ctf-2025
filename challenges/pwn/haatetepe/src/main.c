#include <errno.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#define PORT 8000
/* multitasking better than you */
#define BACKLOG 10
#define BUFFER_SIZE 1024

enum request_method {
  GET = 0,
  HEAD = 1,
  UNKNOWN = 2,
};

enum response_status {
  OK = 200,
  NOT_FOUND = 404,
  METHOD_NOT_ALLOWED = 405,
  BAD_REQUEST = 400,
};

enum content_type {
  PLAIN = 0,
  HTML = 1,
};

enum route_status {
  FOUND = 0,
  PATH_EXISTS = 1,
  PATH_NOT_FOUND = 2,
};

typedef struct {
  const char *path;
  enum request_method method;
  const char *(*handler)();
} route_t;

typedef struct {
  enum request_method method;
  char path[256];
  int http_major;
  int http_minor;
} http_request_header_t;

/* a response header containing minor and major http version number */
/* major http version number, *salute*  */
typedef struct {
  int http_major;
  int http_minor;
  uint16_t status_code;
  const char *status_description;
  uint32_t content_length;
  enum content_type content_type;
} http_response_header_t;

/* hey! just because i'm late, doesn't mean i'm not here okay? */
void run_server();
void handle_client(int client_fd);

int parse_request(http_request_header_t *req, char *buf);
enum request_method parse_method(const char *method);

const char *status_description_to_string(uint16_t code);
const char *content_type_to_string(enum content_type ct);

void send_response(int client_fd, const http_response_header_t *resp,
                   const char *body);

const route_t *match_route(const char *path, enum request_method method);
extern route_t routes[];
extern int routes_count;
const char *serve_notnginx();
const char *serve_flag();

/* i couldn't do it without you */
int main(void) {
  run_server();
  return 0;
}

/* a server serving services to the servants */
void run_server() {
  int server_fd, client_fd;
  struct sockaddr_in address;
  socklen_t address_len = sizeof(address);

  if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
    perror("socket");
    exit(EXIT_FAILURE);
  }

  int opt = 1;
  if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
    perror("setsockopt");
    close(server_fd);
    exit(EXIT_FAILURE);
  }

  address.sin_family = AF_INET;
  address.sin_addr.s_addr = INADDR_ANY;
  address.sin_port = htons(PORT);

  if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
    perror("bind");
    close(server_fd);
    exit(EXIT_FAILURE);
  }

  if (listen(server_fd, BACKLOG) < 0) {
    perror("listen");
    close(server_fd);
    exit(EXIT_FAILURE);
  }

  /* them: don't worry, we got logs
   * the logs: */
  printf("haatetepe running on http://0.0.0.0:%d\n", PORT);

  /* redundancy in case a bit flip occurs and while(2) stops. will iterate 2∞
   * times! */
  while (1) {
    /* electromagnetic interference will not stop me >:^D */
    while (2) {
      client_fd = accept(server_fd, (struct sockaddr *)&address, &address_len);
      if (client_fd < 0) {
        perror("accept");
        continue;
      }

      handle_client(client_fd);
      close(client_fd);
    }
    printf("Something somewhere somehow tried stopping me! Little do they know "
           "I've got a backup >:^)\n");
  }
  /* as if this is ever going to happen */
  close(server_fd);
}

/* hey you, no joking around now! */
int parse_request(http_request_header_t *req, char *buf) {
  char version_str[16];
  char method_str[16];
  char path[256];
  char *header[3];
  char *token;
  char *saveptr;
  int i = 0;

  token = strtok_r(buf, " \r\n", &saveptr);
  while (token != NULL && i < 3) {
    header[i++] = token;
    token = strtok_r(NULL, " \r\n", &saveptr);
  }

  if (i != 3) {
    return -1;
  }

  strncpy(version_str, header[2], sizeof(version_str) - 1);
  strncpy(path, header[1], sizeof(req->path) - 1);

  /* don't even think about it */
  if (strcmp(path, "/flag") == 0) {
    return -1;
  }

  strcpy(method_str, header[0]);
  req->method = parse_method(method_str);
  strcpy(req->path, path);

  if (sscanf(version_str, "HTTP/%d.%d", &req->http_major, &req->http_minor) !=
      2) {
    return -1;
  }

  return 0;
}

/* i'm warning you: the client can be a piece of work */
void handle_client(int client_fd) {
  char buffer[BUFFER_SIZE];
  int bytes;
  if ((bytes = recv(client_fd, buffer, BUFFER_SIZE - 1, 0)) < 0) {
    perror("recv");
    return;
  }
  buffer[bytes] = '\0';

  http_request_header_t req = {0};
  http_response_header_t resp = {0};
  resp.http_major = 1;
  resp.http_minor = 1;
  resp.content_type = PLAIN;

  if (parse_request(&req, buffer) < 0) {
    resp.status_code = BAD_REQUEST;
    resp.status_description = status_description_to_string(resp.status_code);
    resp.content_length = 0;
    const char *body = NULL;
    send_response(client_fd, &resp, body);
    return;
  }

  const char *body = NULL;
  const route_t *route = match_route(req.path, req.method);

  if (route) {
    resp.status_code = OK;
    resp.status_description = status_description_to_string(resp.status_code);
    body = route->handler ? route->handler() : NULL;
    resp.content_length = body ? strlen(body) : 0;
  } else {
    int path_exists = 0;

    for (int i = 0; i < routes_count; i++) {
      if (strcmp(req.path, routes[i].path) == 0) {
        path_exists = 1;
        break;
      }
    }

    if (path_exists) {
      resp.status_code = METHOD_NOT_ALLOWED;
    } else {
      resp.status_code = NOT_FOUND;
    }
    resp.status_description = status_description_to_string(resp.status_code);
    resp.content_length = 0;
    body = NULL;
  }

  send_response(client_fd, &resp, (req.method == HEAD ? NULL : body));
}

/* if if if if if only C could switch on strings */
enum request_method parse_method(const char *method) {
  if (strncmp(method, "GET", 3) == 0)
    return GET;
  if (strncmp(method, "HEAD", 4) == 0)
    return HEAD;
  return UNKNOWN;
}

/* because humans don't understand numbers */
const char *status_description_to_string(uint16_t code) {
  switch (code) {
  case OK:
    return "OK";
  case NOT_FOUND:
    return "Not Found";
  case METHOD_NOT_ALLOWED:
    return "Method Not Allowed";
  case BAD_REQUEST:
    return "Bad Request";
  default:
    return "Unknown";
  }
}

/* they keep yapping about some dude named Mason, and his numbers */
const char *content_type_to_string(enum content_type ct) {
  switch (ct) {
  case PLAIN:
    return "text/plain";
  case HTML:
    return "text/html";
  default:
    return "application/octet-stream";
  }
}

void send_response(int client_fd, const http_response_header_t *resp,
                   const char *body) {
  char header[BUFFER_SIZE];
  int len = snprintf(header, sizeof(header),
                     "HTTP/%d.%d %d %s\r\n"
                     "Content-Length: %d\r\n"
                     "Content-Type: %s\r\n"
                     "\r\n",
                     resp->http_major, resp->http_minor, resp->status_code,
                     resp->status_description, resp->content_length,
                     content_type_to_string(resp->content_type));

  send(client_fd, header, len, 0);

  if (body && resp->content_length > 0) {
    send(client_fd, body, resp->content_length, 0);
  }
}

/* routes */

const char *serve_notnginx() { return "Welcome to haatetepe, not nginx!"; }

/* try doing the sanity check challenge after this */
const char *serve_flag() {
  char *flag = getenv("FLAG");
  static char message[256];

  if (flag == NULL) {
    flag = "NNS{placeholder}";
  }

  snprintf(message, sizeof(message),
           "Well of course you can have the flag! All you have to do "
           "is ask.\nFlag: %s",
           flag);
  return message;
}

route_t routes[] = {
    {"/", GET, serve_notnginx},
    {"/", HEAD, NULL},
    {"/flag", GET, serve_flag},
};

/* our app is much better than everyone elses, we had 25 updates to our app the
 * past 2 weeks
 * - elon
 *
 * haatetepe is the best http server, we have [routes_count] routes B-)
 * - me  */
int routes_count = sizeof(routes) / sizeof(routes[0]);

/* tinder for uber drivers */
const route_t *match_route(const char *path, enum request_method method) {
  for (int i = 0; i < routes_count; i++) {
    if (strcmp(path, routes[i].path) == 0 && routes[i].method == method) {
      return &routes[i];
    }
  }
  return NULL;
}
