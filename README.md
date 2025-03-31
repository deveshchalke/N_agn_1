CNA-Programming-Assignment-1
Programming Assignment 1: HTTP Web Proxy Server Programming Assignment (Python-based) (2025)

STEP - 1 (Main Branch)
- Established a TCP socket using `AF_INET` and `SOCK_STREAM`.
- Assigned the socket to the hostname and port specified in the command-line arguments.
- Set the server to listen for incoming connections.
- Accepted a single connection and promptly closed it.

STEP - 2 & 3 (Obtaining_remote_homepage Branch)
- **Fixed**: Removed an extra leading slash in URI parsing and implemented basic request forwarding.
- Created a server socket using `socket.socket(socket.AF_INET, socket.SOCK_STREAM)`.
- Bound the server socket to the specified hostname and port from command-line arguments.
- Configured the server to listen with a backlog of 50 connections.
- Accepted client connections.
- Read and decoded the HTTP request from the client.
- Extracted the HTTP method, URI, and version from the request line.
- Corrected URI parsing by removing any leading slashes with `lstrip('/')` and stripping the "http://" or "https://" protocol prefix.
- Retrieved the hostname and requested resource from the cleaned URI.
- Connected to the origin server (defaulting to port 80) by resolving the hostname.
- Built and relayed a minimal HTTP request including `Host` and `Connection: close` headers.
- Received the response from the origin server and relayed it to the client.
- Integrated basic error handling and ensured proper cleanup by closing the client socket after processing.

STEP - 4 (Handle page that does not exist)
- After receiving the origin server’s response, extracted and decoded the header to determine the status line.
- Checked if the status line contains "404" to detect a "Not Found" error.
- Logged a message to indicate a 404 Not Found response and forwarded the error response to the client without caching.
- **Fixed**:
  - Replaced `serverSocket.listen(50)` with `server_socket.listen(50)` to match variable naming.
  - Corrected a typo in printing the requested resource (`resourse` changed to `resource`).
  - Used the correct variable `hostname` instead of `host` when constructing the HTTP request.

STEP - 5 (Cache requested webpages where caching is not prohibited by the RFC)
- Determined cache storage path based on the hostname and requested resource.
- Checked if the requested resource was already cached; if available, served it directly.
- If the resource was not cached, forwarded the request to the origin server.
- Examined the `Cache-Control` header in the response to check for `no-store` or `private` directives.
- If caching was allowed, created necessary directories and stored the complete response in the cache.
- Logged cache-related actions, including cache hits, caching new responses, and cases where caching was skipped due to restrictions.

STEP - 6 (Read from a cached file & Redownload the file from the origin server after removal from proxy server)
- Checked whether a requested resource was already available in the cache.
- If a cache hit was detected, read the file from disk and returned the cached response directly to the client without contacting the origin server.
- If the cached file was missing, the proxy determined it as a cache miss and proceeded to request the file from the origin server.
- Upon receiving the response, cached the new file and forwarded it to the client.
- This functionality was implemented in an earlier commit: "Added a check to see if the resource is already cached. If so, serve it directly."

STEP - 7 (Handles URL redirections (301 and 302 only))
- Implemented a mechanism to decode the origin server's response header.
- Developed logic to check the status line for "301" or "302" redirections.
- Logged redirection occurrences and relayed the redirection response to the client.
- Preserved caching rules for redirection responses based on `Cache-Control` headers.

STEP - 8 (Handles `Cache-Control` header `max-age=`)
- Integrated the `time` module to track cache expiration.
- Retrieved the cached file’s last modification time using `os.path.getmtime()`.
- Analyzed the `Cache-Control` header to identify a `max-age` directive.
- Compared the elapsed time since caching (using `time.time()`) against the defined `max-age` limit.
- If the cached file was still within the valid duration, served it to the client.
- If the cache had expired, logged the expiration event and fetched a fresh response from the origin server.
