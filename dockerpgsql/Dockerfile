# See https://jer-k.github.io/docker-postgres-image-with-seeded-data
FROM postgres:14.1-alpine
COPY billsim-bk.sql.gz /docker-entrypoint-initdb.d/
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=billsim