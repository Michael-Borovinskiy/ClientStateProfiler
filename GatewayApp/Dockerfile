FROM openjdk:17
COPY ./target/GatewayApp-1.0-SNAPSHOT.jar /tmp/gatewayApp.jar
WORKDIR /tmp/
EXPOSE 8085
ENTRYPOINT [ "java",  "-jar", "/tmp/gatewayApp.jar" ]