FROM metabase/metabase:v0.49.14

ADD https://github.com/ClickHouse/metabase-clickhouse-driver/releases/download/1.5.1/clickhouse.metabase-driver.jar /plugins/
RUN chmod 644 /plugins/clickhouse.metabase-driver.jar && ls -l /plugins
