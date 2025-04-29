FROM maven:3.5-jdk-17 AS build
COPY src /usr/src/migrate/src
COPY pom.xml /usr/src/migrate
RUN mvn -f /usr/src/migrate/pom.xml clean package


FROM openjdk:17
COPY --from=build /usr/src/migrate/target/MigrationService-1.0-SNAPSHOT.jar /usr/migrate/MigrationService-1.0-SNAPSHOT.jar
EXPOSE 8085

ENTRYPOINT ["java","-jar","/usr/migrate/MigrationService-1.0-SNAPSHOT.jar"]