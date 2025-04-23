FROM openjdk:17
COPY ./target/ExpertiseMonitoring-1.0-SNAPSHOT.jar /tmp/expertiseMonitoring.jar
WORKDIR /tmp/
EXPOSE 8084
ENTRYPOINT [ "java","-jar", "/tmp/expertiseMonitoring.jar"]