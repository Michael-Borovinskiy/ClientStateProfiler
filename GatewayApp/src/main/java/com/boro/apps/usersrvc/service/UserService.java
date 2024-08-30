package com.boro.apps.usersrvc.service;


import com.boro.apps.usersrvc.domain.User;
import com.boro.apps.usersrvc.domain.UserDto;
import com.boro.apps.usersrvc.domain.UserRequestBody;
import com.boro.apps.usersrvc.exceptions.UserAlreadyExistException;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

public interface UserService {

    Flux<UserDto> getAll();
    Mono<UserDto> getUserById(Long id);
    Mono<UserDto> signUp(UserRequestBody userRequestBody) throws UserAlreadyExistException;

    Mono<UserDto> getUserAuthorities();
}
