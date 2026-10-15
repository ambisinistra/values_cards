# Builds the page from its sources and serves it with nginx.
#   docker build -t psychomirror .
#   docker run --rm -p 8080:80 psychomirror      ->  http://localhost:8080

FROM python:3.12-alpine AS build
WORKDIR /src
COPY value_cards.py build.py ./
COPY prompts ./prompts
COPY src ./src
RUN python3 build.py

FROM nginx:1.27-alpine
COPY --from=build /src/index.html /usr/share/nginx/html/index.html
EXPOSE 80
