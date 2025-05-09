# ClientStateProfiler
Educational java project of building services for clients monitoring system*. This is a web-app with docker, so you can start it from docker-compose easily.

Here we use:
  - java 17
  - spring-boot 3.1.6
  - spring-cloud gateway
  - webflux
  - data-r2dbc
  - flyway-core
  - postgresql
  - thymeleaf as frontend
  - jasypt-spring-boot-starter 2.1.2
    
*use Environment variables: jasypt.encryptor.password=commonpoint for each microservice if you like starting apps manually or simply use docker-compose to start

**START**

Run apps from docker-compose. 
Then your data will be migrated if needed and your web-app will be accessible at localhost:8085. We use postgresql in docker container as a db where we store user and other services data. The passwords are encrypted with BCryptPasswordEncoder. Some sensible data in configuration files is also encrypted by using jasypt-spring-boot-starter.

You can login as TEST-USER (with basic roles) or register new one: 

  **TEST-USER**
    login:
      Max
    password:
      rewq21


