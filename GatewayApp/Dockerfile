FROM maven:3.5-jdk-17 AS build
COPY src /usr/src/gatewayapp/src
COPY pom.xml /usr/src/gatewayapp
RUN mvn -f /usr/src/gatewayapp/pom.xml clean package


FROM openjdk:17
COPY --from=build /usr/src/gatewayapp/target/GatewayApp-1.0-SNAPSHOT.jar /usr/gatewayapp/GatewayApp-1.0-SNAPSHOT.jar
EXPOSE 8085

ENTRYPOINT ["java","-jar","/usr/gatewayapp/GatewayApp-1.0-SNAPSHOT.jar"]