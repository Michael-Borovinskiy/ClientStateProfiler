package com.boro.apps.usersrvc.service;

import com.boro.apps.usersrvc.domain.User;
import org.springframework.data.repository.reactive.ReactiveCrudRepository;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;


public interface UserRepo extends ReactiveCrudRepository<User, Long> {

    Mono<User> findByLogin(String login);
    Mono<User> findById(Long id);
    Flux<User> findAll();
    Mono<Boolean> existsByLogin(String login);
}
