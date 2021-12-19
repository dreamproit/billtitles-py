# See https://cadu.dev/creating-a-docker-image-with-database-preloaded/
# dump build stage
FROM postgres:14.1-alpine as dumper

COPY billsim-bk.sql.gz /docker-entrypoint-initdb.d/

RUN ["sed", "-i", "s/exec \"$@\"/echo \"skipping...\"/", "/usr/local/bin/docker-entrypoint.sh"]

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV PGDATA=/data

RUN ["/usr/local/bin/docker-entrypoint.sh", "postgres"]

# final build stage
FROM postgres:14.1-alpine

COPY --from=dumper /data $PGDATA