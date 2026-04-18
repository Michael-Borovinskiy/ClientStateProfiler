package com.boro.apps.usersrvc.security;


import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.r2dbc.repository.config.EnableR2dbcRepositories;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.method.configuration.EnableReactiveMethodSecurity;
import org.springframework.security.config.annotation.web.reactive.EnableWebFluxSecurity;
import org.springframework.security.config.web.server.ServerHttpSecurity;
import org.springframework.security.web.server.SecurityWebFilterChain;

import static org.springframework.security.config.Customizer.withDefaults;


@Configuration
@EnableWebFluxSecurity
@EnableReactiveMethodSecurity
@EnableR2dbcRepositories
@RequiredArgsConstructor
public class SecurityConfiguration  {

    private final SecurityPathsProperties paths;

    @Bean
    SecurityWebFilterChain springSecurityFilterChain(ServerHttpSecurity http) {
        return http
                .authorizeExchange((authorize) -> authorize
                        .pathMatchers(paths.getPublicGet().toArray(String[]::new)).permitAll()
                        .pathMatchers(HttpMethod.POST, paths.getPublicPost().toArray(String[]::new)).permitAll()
                        .pathMatchers(HttpMethod.GET, paths.getAuthenticatedGet().toArray(String[]::new)).authenticated()
                        .pathMatchers(HttpMethod.GET, paths.getAdminGet().toArray(String[]::new)).hasAnyAuthority("ROLE_ADMIN")
                        .pathMatchers(HttpMethod.GET, paths.getMonitoringGet().toArray(String[]::new)).hasAnyAuthority("ROLE_MONITORING_USER")
                        .pathMatchers(HttpMethod.POST, paths.getMonitoringPost().toArray(String[]::new)).hasAnyAuthority("ROLE_MONITORING_USER")
                        .pathMatchers(HttpMethod.PUT, paths.getMonitoringPost().toArray(String[]::new)).hasAnyAuthority("ROLE_MONITORING_USER")
                        .pathMatchers(HttpMethod.DELETE, paths.getMonitoringPost().toArray(String[]::new)).hasAnyAuthority("ROLE_MONITORING_USER")
                )
                .httpBasic(withDefaults())
                .formLogin((form) -> form
                        .loginPage("/login")
                ).csrf(ServerHttpSecurity.CsrfSpec::disable)
                .build();

    }

}