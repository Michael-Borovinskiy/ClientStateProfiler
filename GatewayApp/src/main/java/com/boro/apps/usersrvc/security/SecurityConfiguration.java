package com.boro.apps.usersrvc.security;


import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.r2dbc.repository.config.EnableR2dbcRepositories;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.method.configuration.EnableReactiveMethodSecurity;
import org.springframework.security.config.annotation.web.reactive.EnableWebFluxSecurity;
import org.springframework.security.config.web.server.ServerHttpSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.server.SecurityWebFilterChain;

import static org.springframework.security.config.Customizer.withDefaults;


@Configuration
@EnableWebFluxSecurity
@EnableReactiveMethodSecurity
@EnableR2dbcRepositories
public class SecurityConfiguration  {

    @Bean
    SecurityWebFilterChain springSecurityFilterChain(ServerHttpSecurity http) {
        return http
                .authorizeExchange((authorize) -> authorize
                        .pathMatchers("/login", "/signup", "/logout", "/static/public/css/*", "/GatewayApp/src/main/resources/static/public/css/*", "/users/static/public/css/*").permitAll()
                        .pathMatchers(HttpMethod.POST, "/users/v1/users").permitAll()
                        .pathMatchers(HttpMethod.GET, "/users/v1/users/*", "/logout", "/", "/users/v1/user_authorities", "/selfinfo").authenticated()
                        .pathMatchers(HttpMethod.GET, "/users/v1/users").hasAnyAuthority("ROLE_ADMIN")
                )
                .httpBasic(withDefaults())
                .formLogin((form) -> form
                        .loginPage("/login")
                ).csrf(ServerHttpSecurity.CsrfSpec::disable)
                .build();

    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

}