FROM maven:3.5-jdk-17 AS build
COPY src /usr/src/expertisemonitoring/src
COPY pom.xml /usr/src/expertisemonitoring
RUN mvn -f /usr/src/expertisemonitoring/pom.xml clean package


FROM openjdk:17
COPY --from=build /usr/src/expertisemonitoring/target/ExpertiseMonitoring-1.0-SNAPSHOT.jar /usr/expertisemonitoring/ExpertiseMonitoring-1.0-SNAPSHOT.jar
EXPOSE 8084
ENTRYPOINT ["java","-jar","/usr/expertisemonitoring/ExpertiseMonitoring-1.0-SNAPSHOT.jar"]